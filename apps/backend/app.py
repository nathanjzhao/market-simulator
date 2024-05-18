from random import randint
import time
from typing import Dict, Set, Any, List
import uuid

from fastapi import Depends, FastAPI, Request, Response, Query, Body, HTTPException
from fastapi.responses import StreamingResponse 
from fastapi.middleware.cors import CORSMiddleware
from kafka import TopicPartition
from aiokafka.helpers import create_ssl_context

import aiokafka
import asyncio
import json
import logging
from datetime import datetime
from dotenv import load_dotenv
import os

from backend.logic import OrderBook
from backend.utils.auth import get_current_user
from backend.utils.db import get_db, Base, engine
from backend.utils.schema import DecimalEncoder, MarketRequestMessage
from .user_routes import router as user_router


load_dotenv()

# instantiate the API
app = FastAPI()
app.include_router(user_router)

origins = [
    "http://localhost:3000",  # Allow frontend origin during development
    # "https://your-production-frontend-url.com",  # Allow frontend origin in production
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# global variables
consumer_task = None
consumer = None
producer = None
_state = 0

# env variables
KAFKA_TOPIC = os.getenv('KAFKA_TOPIC')
KAFKA_CONSUMER_GROUP_PREFIX = os.getenv('KAFKA_CONSUMER_GROUP_PREFIX', 'group')
KAFKA_BOOTSTRAP_SERVERS = os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'localhost:9092')
KAFKA_USERNAME = os.getenv('KAFKA_USERNAME')
KAFKA_PASSWORD = os.getenv('KAFKA_PASSWORD')

SYMBOLS = os.getenv('SYMBOLS').split(',')

# initialize logger
logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
log = logging.getLogger(__name__)

orderbook = OrderBook()


@app.on_event("startup")
async def startup_event():
    log.info('Initializing API ...')
    Base.metadata.create_all(bind=engine)
    await initialize()
    await consume()


@app.on_event("shutdown")
async def shutdown_event():
    log.info('Shutting down API')
    consumer_task.cancel()
    if consumer:
        await consumer.stop()
    if producer:
        await producer.stop()

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/state")
async def state():
    return {"state": _state}

@app.get("/symbols")
async def symbols(current_user: str = Depends(get_current_user)):
    return {"symbols" : SYMBOLS}

@app.post("/orderbook_stream")
async def orderbook_stream(symbols: List[str] = Body(default=["AAPL"]), current_user: str = Depends(get_current_user)):
    async def event_stream():
        while True:
            # Get the current state of the order book
            orderbook_as_dict = orderbook.to_json()

            # Send the current state of the order book to the client
            yield f"data: {orderbook_as_dict}\n\n"

            # Sleep for a bit to prevent busy-waiting
            await asyncio.sleep(1)

    return StreamingResponse(event_stream(), media_type="text/event-stream")

@app.post("/kafka_stream")
async def kafka_stream(symbols: List[str] = Body(default=["AAPL"]), current_user: str = Depends(get_current_user)):
    async def event_stream():
        old_state = _state
        while True:
            if old_state != _state:
            # if old_state != _state and _state['topic'] in topics:
                old_state = _state
                yield f'data: {_state}\n\n'
            await asyncio.sleep(1)  # Sleep for a bit to prevent busy-waiting

    return StreamingResponse(event_stream(), media_type="text/event-stream")
 
@app.post("/market_request")
async def add_market_request(request: MarketRequestMessage, current_user: str = Depends(get_current_user)):
    # Convert the request to a dict so it can be serialized to JSON)
    request_dict = request.dict()

    request_dict['op'] = 'Created'
    request_dict['id'] = str(uuid.uuid4())
    request_dict['timestamp'] = int(time.time())
    request_dict['user'] = current_user.username

    request_json = json.dumps(request_dict, cls=DecimalEncoder).encode('utf-8')
    
    fulfillments = orderbook.push(request_dict)
    orderbook.process_fulfillments(fulfillments, producer)

    # Send the market request to a Kafka topic
    await producer.send_and_wait(KAFKA_TOPIC, request_json)

    return {"message": "Market request added", "request": request_dict}
    
async def initialize():
    producer_loop = asyncio.get_event_loop()
    consumer_loop = asyncio.get_event_loop()
    global producer
    global consumer

    producer = aiokafka.AIOKafkaProducer(loop=producer_loop,
                                bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
                                ssl_context=create_ssl_context(),
                                sasl_mechanism='SCRAM-SHA-256',
                                security_protocol='SASL_SSL',
                                sasl_plain_username=KAFKA_USERNAME,
                                sasl_plain_password=KAFKA_PASSWORD)
    await producer.start()
    
    group_id = f'{KAFKA_CONSUMER_GROUP_PREFIX}-{randint(0, 10000)}'
    log.info(f'Initializing KafkaConsumer for topic {KAFKA_TOPIC}, group_id {group_id}'
              f' and using bootstrap servers {KAFKA_BOOTSTRAP_SERVERS}')
    
    consumer = aiokafka.AIOKafkaConsumer(KAFKA_TOPIC, loop=consumer_loop,
                                         bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
                                         ssl_context=create_ssl_context(),
                                         sasl_mechanism='SCRAM-SHA-256',
                                         security_protocol='SASL_SSL',
                                         sasl_plain_username=KAFKA_USERNAME,
                                         sasl_plain_password=KAFKA_PASSWORD,
                                         group_id=group_id,
                                         auto_offset_reset='earliest')
    # get cluster layout and join group
    await consumer.start()

    partitions: Set[TopicPartition] = consumer.assignment()
    nr_partitions = len(partitions)

    if nr_partitions != 1:
        log.warning(f'Found {nr_partitions} partitions for topic {KAFKA_TOPIC}. Expecting '
                    f'only one, remaining partitions will be ignored!')
        
    for tp in partitions:

        # get the log_end_offset
        end_offset_dict = await consumer.end_offsets([tp])
        end_offset = end_offset_dict[tp]

        if end_offset == 0:
            log.warning(f'Topic ({KAFKA_TOPIC}) has no messages (log_end_offset: '
                        f'{end_offset}), skipping initialization ...')
            return

        log.debug(f'Found log_end_offset: {end_offset} seeking to {end_offset-1}')
        consumer.seek(tp, end_offset-1)
        msg = await consumer.getone()
        log.info(f'Initializing API with data from msg: {msg}')

        # update the API state
        _update_state(msg)
        return

async def consume():
    global consumer_task
    consumer_task = asyncio.create_task(send_consumer_message(consumer))

async def send_consumer_message(consumer):
    try:
        # consume messages
        async for msg in consumer:
            log.info(f"Consumed msg: {msg}")
            
            # update the API state
            _update_state(msg)
    finally:
        # will leave consumer group; perform autocommit if enabled
        log.warning('Stopping consumer')
        await consumer.stop()

def _update_state(message: Any) -> None:
    if message.value:
        value = json.loads(message.value)
        global _state
        _state = value
    else:
        log.warning("Received empty message")
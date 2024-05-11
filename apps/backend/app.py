from random import randint
from typing import Set, Any, List


from fastapi import Depends, FastAPI, Response, Query, Body, HTTPException
from fastapi.responses import StreamingResponse 
from fastapi.middleware.cors import CORSMiddleware
from kafka import TopicPartition
from aiokafka.helpers import create_ssl_context

from starlette.concurrency import run_until_first_complete
import dataclasses
import uvicorn
import aiokafka
import asyncio
import json
import logging
from datetime import datetime
from dotenv import load_dotenv
import os

from backend.utils.auth import authenticate_user, get_current_user
from backend.utils.db import get_db, Base, engine, User
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
_state = 0

# env variables
KAFKA_TOPICS = os.getenv('KAFKA_TOPICS').split(',')
KAFKA_CONSUMER_GROUP_PREFIX = os.getenv('KAFKA_CONSUMER_GROUP_PREFIX', 'group')
KAFKA_BOOTSTRAP_SERVERS = os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'localhost:9092')
KAFKA_USERNAME = os.getenv('KAFKA_USERNAME')
KAFKA_PASSWORD = os.getenv('KAFKA_PASSWORD')

# initialize logger
logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
log = logging.getLogger(__name__)


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

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/state")
async def state():
    return {"state": _state}

@app.get("/send_request")
async def send_request():
    loop = asyncio.get_event_loop()
    producer = aiokafka.AIOKafkaProducer(loop=loop,
                                         bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
                                         ssl_context=create_ssl_context(),
                                         sasl_mechanism='SCRAM-SHA-256',
                                         security_protocol='SASL_SSL',
                                         sasl_plain_username=KAFKA_USERNAME,
                                         sasl_plain_password=KAFKA_PASSWORD)
    # get cluster layout and initial topic/partition leadership information
    await producer.start()
    try:
        # produce message
        timestamp = datetime.now().isoformat()
        value = {'timestamp': timestamp, 'symbol': 'AAPL', 'dir': 'BUY', 'price': randint(1, 100)}
        log.info(f'Sending message with value: {value}')
        value_json = json.dumps(value).encode('utf-8')
        await producer.send_and_wait(KAFKA_TOPICS, value_json)
    finally:
        # wait for all pending messages to be delivered or expire.
        await producer.stop()

    return {"message": "Message sent"}


MAX_MESSAGES = 1000

@app.get("/topics")
async def topics(current_user: str = Depends(get_current_user)):
    return {"topics" : KAFKA_TOPICS}

@app.post("/stream")
async def stream(topics: List[str] = Body(default=["market"]), current_user: str = Depends(get_current_user)):
    async def event_stream():
        old_state = _state
        while True:
            if old_state != _state:
            # if old_state != _state and _state['topic'] in topics:
                old_state = _state
                yield f"data: {_state}\n\n"
            await asyncio.sleep(1)  # Sleep for a bit to prevent busy-waiting

    return StreamingResponse(event_stream(), media_type="text/event-stream")

async def initialize():
    loop = asyncio.get_event_loop()
    global consumer
    group_id = f'{KAFKA_CONSUMER_GROUP_PREFIX}-{randint(0, 10000)}'
    log.info(f'Initializing KafkaConsumer for topic {KAFKA_TOPICS}, group_id {group_id}'
              f' and using bootstrap servers {KAFKA_BOOTSTRAP_SERVERS}')
    
    consumer = aiokafka.AIOKafkaConsumer(*KAFKA_TOPICS, loop=loop,
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
        log.warning(f'Found {nr_partitions} partitions for topic {KAFKA_TOPICS}. Expecting '
                    f'only one, remaining partitions will be ignored!')
        
    for tp in partitions:

        # get the log_end_offset
        end_offset_dict = await consumer.end_offsets([tp])
        end_offset = end_offset_dict[tp]

        if end_offset == 0:
            log.warning(f'Topic ({KAFKA_TOPICS}) has no messages (log_end_offset: '
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
            # x = json.loads(msg.value)
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
        _state = value['state']
    else:
        log.warning("Received empty message")
from dotenv import load_dotenv
import aiokafka
from aiokafka.helpers import create_ssl_context
import asyncio
import json
import os
from random import randint

load_dotenv()

# env variables
KAFKA_TOPICS = os.getenv('KAFKA_TOPICS').split(',')
KAFKA_BOOTSTRAP_SERVERS = os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'localhost:9092')
KAFKA_USERNAME = os.getenv('KAFKA_USERNAME')
KAFKA_PASSWORD = os.getenv('KAFKA_PASSWORD')

# global variables
loop = asyncio.get_event_loop()


async def send_one():
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
        msg_id = f'{randint(1, 10000)}'
        value = {'message_id': msg_id, 'text': 'some text', 'state': randint(1, 100)}
        print(f'Sending message with value: {value}')
        value_json = json.dumps(value).encode('utf-8')
        await producer.send_and_wait(KAFKA_TOPICS[0], value_json)
    finally:
        # wait for all pending messages to be delivered or expire.
        await producer.stop()

# send message
loop.run_until_complete(send_one())
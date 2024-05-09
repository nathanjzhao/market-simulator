import aiokafka
from aiokafka.helpers import create_ssl_context
import asyncio
import os


# env variables
KAFKA_TOPIC = os.getenv('KAFKA_TOPIC')
KAFKA_CONSUMER_GROUP = os.getenv('KAFKA_CONSUMER_GROUP', 'group')
KAFKA_BOOTSTRAP_SERVERS = os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'localhost:9092')
KAFKA_USERNAME = os.getenv('KAFKA_USERNAME')
KAFKA_PASSWORD = os.getenv('KAFKA_PASSWORD')

# global variables
loop = asyncio.get_event_loop()


async def consume():
    consumer = aiokafka.AIOKafkaConsumer(KAFKA_TOPIC, loop=loop,
                                         bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
                                         ssl_context=create_ssl_context(),
                                         sasl_mechanism='SCRAM-SHA-256',
                                         security_protocol='SASL_SSL',
                                         sasl_plain_username=KAFKA_USERNAME,
                                         sasl_plain_password=KAFKA_PASSWORD,
                                         group_id=KAFKA_CONSUMER_GROUP,
                                         auto_offset_reset='earliest')
    # get cluster layout and join group KAFKA_CONSUMER_GROUP
    await consumer.start()
    try:
        # consume messages
        async for msg in consumer:
            print(f"Consumed msg: {msg}")
    finally:
        # will leave consumer group; perform autocommit if enabled.
        await consumer.stop()

loop.run_until_complete(consume())
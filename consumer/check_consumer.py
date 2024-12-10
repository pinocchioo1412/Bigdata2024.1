import sys
from pathlib import Path
from confluent_kafka import Consumer, KafkaError
from script.utils import load_environment_variables
from dotenv import load_dotenv

path_to_utils = Path(__file__).parent.parent
sys.path.insert(0, str(path_to_utils))

load_dotenv()
env_vars = load_environment_variables()

conf = {

    'bootstrap.servers': env_vars.get("KAFKA_BROKERS"),
    'group.id': "myGroup", 
    'auto.offset.reset': 'earliest'  
}
consumer = Consumer(conf)

consumer.subscribe([env_vars.get("STOCK_PRICE_KAFKA_TOPIC")])

try:

    while True:
        msg = consumer.poll(timeout=1.0) 

        if msg is None:
            continue

        if msg.error():

            if msg.error().code() == KafkaError._PARTITION_EOF:
                continue
            else:

                print(msg.error())
                break

        print('Received message: {}'.format(msg.value().decode('utf-8')))


except KeyboardInterrupt:
    pass

finally:

    consumer.close()

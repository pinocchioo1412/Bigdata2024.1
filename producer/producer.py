import socket

from confluent_kafka import Producer
from dotenv import load_dotenv
from producer.producer_utils import retrieve_real_time_data
from script.utils import load_environment_variables

load_dotenv()
env_vars = load_environment_variables()
# Configuration for Kafka Producer
conf = {
    # Pointing to all three brokers
    'bootstrap.servers': env_vars.get("KAFKA_BROKERS"),
    'client.id': socket.gethostname(),
    'enable.idempotence': True,
}
producer = Producer(conf)

if __name__ == '__main__':
    retrieve_real_time_data(producer,
                            env_vars.get("COINS"),
                            env_vars.get("STOCK_PRICE_KAFKA_TOPIC"),
                            )

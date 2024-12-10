# How to deploy project
## 1.Clone repository
## 2.run pip install -r requirements.txt
this is everything you need :
confluent-kafka
python-dotenv~=0.21.0
findspark
psycopg2-binary
influxdb_client
PyHDFS~=0.3.1
py4j
pyspark~=3.4.1
pymongo~=4.6.3
requests~=2.31.0
pathlib~=1.0.1
pandas
influxdb-client
## 3.Download my_spark_image
bash : docker build -t my-spark-image:latest 
## 4. Deploy Docker
bash : docker-compose up -d
After make sure everything run smoothly
![image](https://github.com/user-attachments/assets/089631f7-1b3c-4540-87d6-1e3e9bc73451)

## 5. run python -m producer.producer
this will start crawling data from the API provided and send it to kafka
You can run bash : python -m consumer.checkconsumer to make sure that message delivered
By the way you can check the kafka brokers if they're working or checking running application 
through localhost:8080 or localhost:9100

![image](https://github.com/user-attachments/assets/d8ae1173-cd78-4ebf-8cb5-f4b037e5074c)


![image](https://github.com/user-attachments/assets/25dd9df3-0efa-4b88-af82-c74d02966a06)
## 6.Then you can check if data has been sent to hdfs by link to localhost:9870 ->utilities->data
you may see like this 
![image](https://github.com/user-attachments/assets/7bcd19a8-7bb5-4f9b-98d3-84d1d9812181)
If u dont see data stored in browsing file, restart spark_speed and spark_batch container
Now the data has been store successfully, we can do a lot things with them
## 7. First i store them in influxdb for visualizing later 
link to localhost:8086 to see the data stored
u may see something like this : 
![image](https://github.com/user-attachments/assets/4b7d10a4-60ea-4a8a-9dbb-b4add1d70ff8)
## 8. You can use them to visualize in grafana like this:
this is current price with real-time accuracy approximation

![image](https://github.com/user-attachments/assets/a43cf1a1-7a08-4b40-b523-b21292a569c1)



import json

import pyhdfs
from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from pyspark.sql.types import StructType, StructField, StringType, DoubleType

# Initialize Spark Session
spark = SparkSession.builder \
    .appName("Crypto Dependency Analysis") \
    .config("spark.mongodb.output.uri", "mongodb://root:admin@mongodb:27017/bigdata.stock2024") \
    .getOrCreate()

# Set up the HDFS client
hdfs = pyhdfs.HdfsClient(hosts="namenode:9870", user_name="hdfs")
directory = '/data'
if not hdfs.exists(directory):
    hdfs.mkdirs(directory)
files = hdfs.listdir(directory)
print("Files in '{}':".format(directory), files)

# Define the schema for the DataFrame
schema = StructType([
    StructField("iso", StringType(), True),
    StructField("name", StringType(), True),
    StructField("current_price", DoubleType(), True),
    StructField("open", DoubleType(), True),
    StructField("high", DoubleType(), True),
    StructField("low", DoubleType(), True),
    StructField("close", DoubleType(), True),
    StructField("date_time", StringType(), True)
])


# Function to create a DataFrame from a file's content
def create_dataframe_from_file(file_path):
    try:
        file_content = hdfs.open(file_path).read().decode('utf-8')
        data = json.loads(file_content)
        return spark.createDataFrame([data], schema)
    except Exception as e:
        print("Failed to read '{}': {}".format(file_path, e))
        return None


# Create an empty DataFrame with the specified schema
df = spark.createDataFrame([], schema)

# Iterate over files and create DataFrame
for file in files:
    file_path = "{}/{}".format(directory, file)
    file_df = create_dataframe_from_file(file_path)
    if file_df:
        df = df.unionByName(file_df)

# Remove duplicates
df = df.dropDuplicates()

basic_stats_t = df.groupBy("iso").agg(
    F.mean("open").alias("avg_open"),
    F.mean("high").alias("avg_high"),
    F.mean("low").alias("avg_low"),
    F.mean("close").alias("avg_close"),
    F.stddev("close").alias("std_dev_close"),
    F.max("high").alias("historical_high"),
    F.min("low").alias("historical_low")
)

basic_stats_t.show()
# Calculate price change for each crypto
df = df.withColumn("price_change", (df.close - df.open) / df.open)

# Basic Statistics for each stock
basic_stats = df.groupBy("iso").agg(
    F.mean("price_change").alias("avg_price_change"),
    F.stddev("price_change").alias("std_dev_price_change")
)

# K-Means Model
from pyspark.ml.feature import VectorAssembler
from pyspark.ml.clustering import KMeans

input_cols = ["avg_price_change", "std_dev_price_change"]
vec_assembler = VectorAssembler(inputCols=input_cols, outputCol="features")
df_kmeans = vec_assembler.transform(basic_stats)

kmeans = KMeans().setK(2).setSeed(1).setFeaturesCol("features")
model = kmeans.fit(df_kmeans)

# Predict clusters for each crypto
predictions = model.transform(df_kmeans)
predictions.select("iso", "prediction").show()

basic_stats.write.format("mongo").mode("append").save()

# Stop SparkSession
spark.stop()

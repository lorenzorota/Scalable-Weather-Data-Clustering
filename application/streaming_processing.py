#toDo
#fine tune number centers
#test with 0.2, 0.4, 0.6, 0.8... of the total data and benchmark

from pyspark.sql import SparkSession
import numpy as np
from pyspark.sql.functions import *
from pyspark.sql.types import *
import time
####Streaming Part###


def normalizeData(train_df, columns, maximums, minimums):
    for i in range(len(columns)):
        train_df = train_df.withColumn(columns[i], ((train_df[columns[i]] - float(minimums[i])) / (float(maximums[i])-float(minimums[i]))))
    return train_df


def closestPoint(p, centers):
    bestIndex = 0
    closest = float("+inf")
    for i in range(len(centers)):
        tempDist = np.sum((p - centers[i]) ** 2)
        # tempDist = sum((x**2 for x in [a - b for a, b in zip(p, centers[i])]))
        if tempDist < closest:
            closest = tempDist
            bestIndex = i
    return bestIndex


newSchema = StructType([
    StructField("wind_speed", DoubleType(), False),
    StructField("city", StringType(), False),
    StructField("wind_chill", DoubleType(), False),
    StructField("elevation", DoubleType(), False),
    StructField("temp", DoubleType(), False),
    StructField("uv", DoubleType(), False),
    StructField("longitude", DoubleType(), False),
    StructField("humidity", DoubleType(), False),
    StructField("winddir", DoubleType(), False),
    StructField("pressure", DoubleType(), False),
    StructField("latitude", DoubleType(), False),
    StructField("solar_radiation", DoubleType(), False),
    StructField("precip_rate", DoubleType(), False),
    StructField("timestamp", LongType(), False)
])

centersSchema = StructType([
    StructField("wind_speed", DoubleType(), False),
    StructField("wind_chill", DoubleType(), False),
    StructField("elevation", DoubleType(), False),
    StructField("temp", DoubleType(), False),
    StructField("uv", DoubleType(), False),
    StructField("humidity", DoubleType(), False),
    StructField("winddir", DoubleType(), False),
    StructField("pressure", DoubleType(), False),
    StructField("solar_radiation", DoubleType(), False),
    StructField("precip_rate", DoubleType(), False),
])

spark = SparkSession.builder.appName("Test application to read file").getOrCreate()
spark.sparkContext.setLogLevel("ERROR")
URI = spark.sparkContext._gateway.jvm.java.net.URI
Path = spark.sparkContext._gateway.jvm.org.apache.hadoop.fs.Path
FileSystem = spark.sparkContext._gateway.jvm.org.apache.hadoop.fs.FileSystem
Configuration = spark.sparkContext._gateway.jvm.org.apache.hadoop.conf.Configuration
fs = FileSystem.get(URI("hdfs://namenode:9000"), Configuration())

centers = np.array(spark.read.format("csv").schema(centersSchema).load("hdfs://namenode:9000/user/root/centers.csv").collect(), dtype=float)
maximums = np.array(spark.read.format("csv").load("hdfs://namenode:9000/user/root/maximums.csv").collect())
minimums = np.array(spark.read.format("csv").load("hdfs://namenode:9000/user/root/minimums.csv").collect())


status = fs.listStatus(Path('hdfs://namenode:9000/user/root/topics/stream/partition=0'))
previousFile=status[0].getPath().toString()
c=1
while True:
    time.sleep(7)
    status = fs.listStatus(Path('hdfs://namenode:9000/user/root/topics/stream/partition=0'))
    currentFile = status[-1].getPath().toString()
    if currentFile == previousFile:
        print('no new file')
        continue
    print(c)
    previousFile=currentFile
    dfStream = spark.read.format("avro").schema(newSchema).load(currentFile)
    dfStream = dfStream.drop('timestamp')
    dfStream = dfStream.drop('city')
    dfStream = dfStream.drop('latitude')
    dfStream = dfStream.drop('longitude')
    dfStream = dfStream.dropna()
    dfStream=normalizeData(dfStream,dfStream.schema.names, maximums, minimums)
    # print('printing df count')
    # print(dfStream.count())
    # dfStream.show()
    dfStream = dfStream.rdd.map(lambda p: np.array(p))

    closest = dfStream.map(lambda p: (closestPoint(p, centers)))
    closest = closest.collect()
    print('closest centers for the new points')
    print(closest)
    c=c+1

spark.stop()
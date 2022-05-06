from pyspark.sql import SparkSession
from pyspark import SparkConf
import numpy as np
from pyspark.sql.functions import *
from pyspark.sql.types import *
import time
import pandas as pd

def standardize_train_test_data(train_df, columns):

    aggMax=[]
    aggMin=[]
    for column in columns:
        aggMin.append(min(train_df[column]).alias(column))
        aggMax.append(max(train_df[column]).alias(column))

    minimums = train_df.agg(*aggMin).collect()[0]
    maximums = train_df.agg(*aggMax).collect()[0]
    for column in columns:
        train_df = train_df.withColumn(column, ((train_df[column] - minimums[column]) / (maximums[column]-minimums[column])))
    return [train_df,np.array(minimums),np.array(maximums)]


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


spark = SparkSession.builder.appName("Test application to read file").getOrCreate()

spark.sparkContext.setLogLevel("ERROR")

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


print('We first retrieve from HDFS')


dataframeFull = spark.read.format("avro").schema(newSchema).load("hdfs://namenode:9000/user/root/topics/common/partition=0")
print('We have the file loaded into the spark dataframe, we now print it')
dataframeFull.show(truncate=False)

dataframeFull=dataframeFull.drop('timestamp')
dataframeFull=dataframeFull.drop('city')
dataframeFull=dataframeFull.drop('latitude')
dataframeFull=dataframeFull.drop('longitude')
#drop the rows with na's
dataframeFull=dataframeFull.dropna()

#normalise the data
[df,minimums,maximums]=standardize_train_test_data(dataframeFull,dataframeFull.schema.names)
K = 50
convergeDist = 0.05
print('PRINTING DF COUNT')
print(dataframeFull.count())
# dataframeFull=dataframeFull.rdd

start_time_percentage = time.time()
# turn into rdd
df=df.rdd
# turn into np arrays, and also rdd->pipelineRDD
df=df.map(lambda p: np.array(p))
beta=0.8
alpha=1.05
kPoints = np.array(df.takeSample(False, K, 1))
# kPoints = data.takeSample(False, K, 1)
tempDist = 1
iter=0
while tempDist > convergeDist:
    iter=iter+1
    print(iter)
    start_time = time.time()
    #use beta% of data each time
    partialData=df.sample(False, beta, seed=5)
    # closest = df.map(lambda p: (closestPoint(p, kPoints), (p, 1)))
    closest = partialData.map(lambda p: (closestPoint(p, kPoints), (p, 1)))
    # increase beta until 1
    beta=np.max([1, beta*alpha])
    #assign to each point the closest center
    #for each center calculate the total sums, and the number of elements
    pointStats = closest.reduceByKey(lambda p1_c1, p2_c2: (p1_c1[0] + p2_c2[0], p1_c1[1] + p2_c2[1]))
    #calculate the new points using the mean
    newPoints = pointStats.map(lambda st: (st[0], st[1][0] / st[1][1])).collect()

    tempDist = np.sum(np.sum((kPoints[iK] - p) ** 2) for (iK, p) in newPoints)

    for (iK, p) in newPoints:
        kPoints[iK] = p
    print("--- %s seconds ---" % (time.time() - start_time))
print('iterations: ' + str(iter))


print("Final centers: " + str(kPoints))
print('\n')
print('iterations: '+ str(iter))
kPoints=np.array(kPoints)
kpointsDenormalized= kPoints*(maximums-minimums) - minimums
print("Final centers denormalized: " + str(kpointsDenormalized))


maximums=pd.DataFrame(maximums)
minimums=pd.DataFrame(minimums)
kPoints=pd.DataFrame(kPoints)


kPoints=spark.createDataFrame(kPoints)
kPoints.write.format("com.databricks.spark.csv").mode("overwrite").save('hdfs://namenode:9000/user/root/centers.csv')

maximums=spark.createDataFrame(maximums)
maximums.write.format("com.databricks.spark.csv").mode("overwrite").save('hdfs://namenode:9000/user/root/maximums.csv')

minimums=spark.createDataFrame(minimums)
minimums.write.format("com.databricks.spark.csv").mode("overwrite").save('hdfs://namenode:9000/user/root/minimums.csv')

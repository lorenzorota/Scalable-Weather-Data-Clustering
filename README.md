# Scalable Weather Data Clustering Project

A data processing pipeline for clustering weather data.

## Authors

Marios Souroulla,
Philip Andreadis,
Lorenzo Rota

## Description

The purpose of the project is to cluster big amounts of weather data (Big Data). We perform a modified
 k-means algorithm over historic data to calculate the K-best centers that describe the various
weather profiles. Then, we stream data, and we use the calculated centers to classify the
streaming data into one of the centers.

For the data ingestion we use Apache Kafka, we store the data on HDFS, and we process them using Apache Spark in python.

## Structure

The project runs as a pipeline and is structured into 3 consecutive layers:

1. __Data Acquisition__: This is responsible for emulating the weather data source by fetching data from multiple weather stations and publishing it to a real-time data streaming API. For more information on what this entails and how to set this up, read the instructions `data_acquisition/README.md`. It's important to note that this service be running continuously.

2. __Data Ingestion__: For any data processing to take place, there needs to be a bridge between the data source and the data sink. This is where the data ingestion layer comes in. In this project, data ingestion will be comprised of batch ingestion and streaming ingestion (following a lambda architecture). More information on how to run this can be found under `data_ingestion/README.md`.

3. __Application__: Here the core of the data processing will take place. In this case, it will be an application of a two versions of k-means clustering of historical data. The application also support streaming processing where new data records will be assigned to the clusters that were computed from the historical data. More information of this can be found under `application/README.md`.

While the Data Acquisition layer can run independently, the other two layers require that Kafka, Hadoop and Spark are up and running. For this, follow the instructions under `docker_containers/README.md`.

## How to run the project

The instructions on how to run each layer are explained in the corresponding READMEs.

The correct sequence in order to run properly is:

Data Acquisition -> Data Ingestion -> Application (Data Processing).

## Project Report

See the 'Scalable_Computing_Project.pdf'.

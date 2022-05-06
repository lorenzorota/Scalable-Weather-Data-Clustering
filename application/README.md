# K-Means Application

The instructions on how to run the k-means application will be explained here.

## Setting up the Dockerfile

Since docker should be properly running (after having set up the other containers), we just need to build the `Dockerfile` in this directory and run it afterwards. The files you can run are either `batch_procesing.py` or `streaming_procesing.py`. The script 'batch_processing.py' will read the ingested data from the HDFS directory, run the K-means algorith, and output 3 .csv files in the HDFS directory. The first file is the 'centers.csv' which contains the K centers calculated by the K-means algorithm, the second and third files are 'maximums.csv' and 'minimums'csv' which contain the maximums and minimums for each column, needed for the normalization of data. These 3 .csv files are used by the 'streaming_processing.py' script. In order for the streaming to work, you need to have the streaming ingestion running, and having already producd the 3 .csv files decsribed before (i.e. run batch proecessing first). Additionally there is also `batch_processing_benchmarking.py` which is used for benchmarking the historical data by running the application on {10, 30, 50, 70, 90, 100}% of the ingested historical data.

First you need to build the docker file:

```bash
docker build -t python-example .
```

If you want to run the batch processing, run:

```bash
docker run --rm --network hadoop-spark --name application python-example /app/batch_processing.py
```

To run the streaming processing, run:

```bash
docker run --rm --network hadoop-spark --name application python-example /app/streaming_processing.py
```

Optionally, to perform benchmarking on the historical data, run:

```bash
docker run --rm --network hadoop-spark --name application python-example /app/batch_processing_benchmarking.py
```

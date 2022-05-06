# Data Ingestion

Before you can run the application, you will need to carry out data ingestion. This project supports two types:

1. Batch Ingestion
2. Streaming Ingestion

Before running either, make sure that you set up the docker containers and followed the instructions in `docker_containers/README.md`.

## Batch Ingestion

To begin the batch ingestion of historic data, simply run:

```bash
python batch_ingestion.py
```

It will first run a clean-up to ensure that the kafka topic, on which the data will be ingested, is emptied so that the data ingestion can be carried out correctly.

Next, it will start up the source connector to ingest the data from multiple sources and store it in a single kafka topic. Once this is done, the script will kill the source connector and start up the sink connector, which will write the records as avro files into hdfs (the topic will be broken up into smaller batches, where the size of each batch is determined by the `flush.size` in the sink configuration). At the end, the clean-up will run again and ensure that the topic is emptied and all connectors are gracefully shutdown.

## Streaming Ingestion

To run the streaming ingestion, you can simply run the following script with one of the three options

```bash
python streaming_ingestion.py [--start, --stop, --reset]
```

When the start option is passed, it will start the source, where the single kafka topic gets populated with records as more data becomes available, and the sink connector, which will move the data from the topic into avro files in hdfs (similarly to batch ingestion, but with a much smaller flush size).

Stop simply kills the source and sink connectors, which can be resumed at any point in time by starting them up again.

Reset will delete the kafka a topic as well as delete the hdfs directory for the streaming data.
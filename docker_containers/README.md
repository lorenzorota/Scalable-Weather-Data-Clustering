# Kafka-Hadoop-Spark Integration

Both Hadoop and Spark will be installed from a docker image provided by Big Data Europe.

## Setting up the containers

Make sure that you have docker installer and running. To check that it works, enter

```bash
docker --version
docker-compose --version
docker-machine –version
```

Now create a network

```bash
docker network create -d bridge hadoop-spark
```

## Hadoop

To compose the docker image we simply run

```bash
cd hadoop
docker-compose up -d
cd ..
```

Next, we want to move a file into our docker container and then into HDFS. Here is an example of how we can achieve this.

1. Find the ID of the docker container for the hadoop namenode

    ```bash
    docker container ls
    > CONTAINER ID         IMAGE                                            ...
    > ...
    > <SOME_CONTAINER_ID>  bde2020/hadoop-namenode:2.0.0-hadoop3.2.1-java8  ...
    ```

2. Now move a file from local computer into docker container

    ```bash
    docker cp original_file <SOME_CONTAINER_ID>:dockerized_file
    ```

3. Enter the bash shell of the docker container

    ```bash
    docker exec -it namenode bash
    ```

4. Create a directory in HDFS

    ```bash
    hadoop fs -mkdir -p input
    ```

5. Move file into HDFS

    ```bash
    hdfs dfs -put dockerized_file input
    ```

6. Confirm that it is indeed there

    ```bash
    hdfs dfs -ls input
    > Found 1 items
    > -rw-r--r--   3 root supergroup     xxxxxx yyyy-mm-dd hh:mm input/dockerized_file
    ```

7. To delete the file from HDFS

    ```bash
    hdfs dfs -rm input/dockerized_file
    ```

To shut it down, we simply run

```bash
cd hadoop
docker-compose down
cd ..
```

## Spark

To compose the docker image we simply run

```bash
cd spark
docker-compose up -d
cd ..
```

To shut it down, we simply run

```bash
cd spark
docker-compose down
cd ..
```

## Kafka

The following instructions are for both installing Kafka as well as testing out the source and sink connectors for this project. To properly run the data ingestion steps of the pipeline, refer to the README in the `data_ingestion` directory. Only steps 1-4 are required for that.

Requirements:

- HDFS3 Sink Connector (==1.1.9)
- Maven (>=3.8.5)
- Java (>=17.0.2)

You can download the sink connector from <https://www.confluent.io/hub/confluentinc/kafka-connect-hdfs3> (make sure to download the correct version). Unzip the file and store it under `./resources/kafka-connect-hdfs3-1.1.9`.

1. (optional) If we want to build both the batch and speed source connectors, we must first install the latest version of Maven and then run the following:

    ```bash
    cd kafka
    mvn install:install-file -Dfile=resources/pubnub-gson-6.0.0-all.jar -DgroupId=com.pubnub -DartifactId=pubnub-gson -Dversion=6.0.0 -Dpackaging=jar -DcreateChecksum=true

    cd kafka-connect-speed
    mvn clean package
    cp -R ./target/components/packages/epic-kafka-connect-speed-0.1.0/epic-kafka-connect-speed-0.1.0 ../resources/kafka-connect-speed-0.1.0
    cd ..

    cd kafka-connect-batch
    mvn clean package
    cp -R ./target/components/packages/epic-kafka-connect-batch-0.1.0/epic-kafka-connect-batch-0.1.0 ../resources/kafka-connect-batch-0.1.0
    cd ../..
    ```

2. To set up the container run

    ```bash
    cd kafka
    docker-compose up -d
    cd ..
    ```

3. Now that you have kafka running, you want to configure the connectors for the batch and streaming ingestion. First make sure that the batch ingestion connector is configured correctly under `../data_ingestion/configs/batch-source.json`, it should be structured as follows

    ```json
    {
        "name": "batch-source",
        "config": {
            "connector.class": "com.acme.kafka.connect.batch.BatchSourceConnector",
            "does.this.work": "yes",
            "tasks.max": "25",
            "pubnub.subscribe.key": "PUBNUB_SUBSCRIBE_KEY",
            "pubnub.channels": "city-1,city-2,...",
            "pubnub.historic.hours" : "24",
            "key.converter": "io.confluent.connect.avro.AvroConverter",
            "key.converter.schema.registry.url": "http://schemaregistry:8085",
            "value.converter": "io.confluent.connect.avro.AvroConverter",
            "value.converter.schema.registry.url": "http://schemaregistry:8085"
        }
    }
    ```

    Next you want to make sure that the streaming ingestion connector is configured correctly under `../data_ingestion/configs/stream-source.json`:

    ```json
    {
        "name": "stream-source",
        "config": {
            "connector.class": "com.acme.kafka.connect.speed.SpeedSourceConnector",
            "does.this.work": "yes",
            "tasks.max": "25",
            "pubnub.subscribe.key": "PUBNUB_SUBSCRIBE_KEY",
            "pubnub.channels": "city-1,city-2,...",
            "pubnub.historic.hours" : "24",
            "key.converter": "io.confluent.connect.avro.AvroConverter",
            "key.converter.schema.registry.url": "http://schemaregistry:8085",
            "value.converter": "io.confluent.connect.avro.AvroConverter",
            "value.converter.schema.registry.url": "http://schemaregistry:8085"
        }
    }
    ```

    Finally you configure the batch and streaming sink connectors as follows:

    ```json
    {
        "name": "batch-sink",
        "config": {
            "connector.class": "io.confluent.connect.hdfs3.Hdfs3SinkConnector",
            "tasks.max": "25",
            "topics": "common",
            "hdfs.url": "hdfs://namenode:9000/user/root",
            "flush.size": "10000",
            "key.converter": "org.apache.kafka.connect.storage.StringConverter",
            "value.converter": "io.confluent.connect.avro.AvroConverter",
            "value.converter.schemas.enable": "true",
            "value.converter.schema.registry.url":"http://schemaregistry:8085",
            "confluent.topic.bootstrap.servers": "kafka:9092",
            "confluent.topic.replication.factor": "1"
        }
    }
    ```

    ```json
    {
        "name": "stream-sink",
        "config": {
            "connector.class": "io.confluent.connect.hdfs3.Hdfs3SinkConnector",
            "tasks.max": "5",
            "topics": "stream",
            "hdfs.url": "hdfs://namenode:9000/user/root",
            "flush.size": "50",
            "key.converter": "org.apache.kafka.connect.storage.StringConverter",
            "value.converter": "io.confluent.connect.avro.AvroConverter",
            "value.converter.schemas.enable": "true",
            "value.converter.schema.registry.url":"http://schemaregistry:8085",
            "confluent.topic.bootstrap.servers": "kafka:9092",
            "confluent.topic.replication.factor": "1"
        }
    }
    ``` 

    Here you just make sure that the `flush.size` is appropriate (for example, you want to write a new avro file after 1 new record is received for each city).

4. (optional) Before you can start the batch ingestion source and sink connectors (in that order), you first need to change the directory to `../data_ingestion/` and then run:

    ```bash
    curl -X POST -H "Content-Type:application/json" -d @configs/batch-source.json http://localhost:8083/connectors

    curl -X POST -H "Content-Type:application/json" -d @configs/batch-sink.json http://localhost:8083/connectors
    ```

5. (optional) You can also check which processes are still `RUNNING`, `FAILED` or `UNASSIGNED` (meaning it finished).

    ```bash
    curl localhost:8083/connectors/batch-source/status
    ```


6. (optional) To test out the streaming ingestion you can start the streaming ingestion source and sink connectors (in any order), run:

    ```bash
    curl -X POST -H "Content-Type:application/json" -d @configs/stream-source.json http://localhost:8083/connectors

    curl -X POST -H "Content-Type:application/json" -d @configs/stream-sink.json http://localhost:8083/connectors
    ```

7. (optional) To stop all connectors:

    ```bash
    curl -X DELETE http://localhost:8083/connectors/stream-source
    curl -X DELETE http://localhost:8083/connectors/batch-source
    curl -X DELETE http://localhost:8083/connectors/stream-sink
    curl -X DELETE http://localhost:8083/connectors/batch-sink
    ```

FROM ubuntu:latest

# Install OpenJDK 8
RUN \
  apt-get update && \
  apt-get install -y openjdk-8-jdk && \
  rm -rf /var/lib/apt/lists/*

# Install Python
RUN \
    apt-get update && \
    apt-get install -y python python-dev python3-pip python3-virtualenv && \
    rm -rf /var/lib/apt/lists/*

# Install PySpark and Numpy
RUN \
    pip install --upgrade pip && \
    pip install numpy && \
    pip install pyspark && \
    pip install confluent_kafka && \
    pip install requests && \
    pip install avro
    
RUN pip install pandas

# Define working directory
WORKDIR /data

# Define default command
CMD ["bash"]
COPY batch_processing.py /app/
COPY streaming_processing.py /app/
COPY batch_processing_benchmarking.py /app/

ENTRYPOINT ["spark-submit", "--packages", "org.apache.spark:spark-avro_2.12:3.2.1"]

#CMD ["spark-submit", "--packages", "org.apache.spark:spark-avro_2.12:3.2.1,org.apache.spark:spark-streaming-kafka-0-10_2.12:3.2.0,org.apache.spark:spark-sql-kafka-0-10_2.12:3.2.0", "/app/$FILE"]

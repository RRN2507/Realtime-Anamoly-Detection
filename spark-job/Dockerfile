FROM apache/spark:3.5.0

USER root
RUN apt-get update && apt-get install -y python3-pip
WORKDIR /opt/spark/work-dir
COPY ./spark-job/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY ./spark-job/streaming_job.py .

# Command to run the spark job
CMD ["/opt/spark/bin/spark-submit", "--packages", "org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.0,org.postgresql:postgresql:42.7.1", "streaming_job.py"]

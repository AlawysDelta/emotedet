FROM openjdk:8-jre

ENV PATH $SPARK_DIR/bin:$PATH
ENV SPARK_VERSION=3.1.2
ENV SPARK_DIR=/opt/spark
ENV PATH $SPARK_DIR/bin:$PATH

ADD setup/spark-${SPARK_VERSION}-bin-hadoop2.7.tgz /opt

RUN apt-get update && apt-get -y install bash python3 python3-pip

RUN pip3 install pyspark numpy elasticsearch
# Create Sym Link 
RUN ln -s /opt/spark-${SPARK_VERSION}-bin-hadoop2.7 ${SPARK_DIR} 

COPY dataset /opt/spark/dataset
# Add Python Code
COPY code  /opt/spark/code

WORKDIR ${SPARK_DIR}
ENTRYPOINT  ./bin/spark-submit --packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.1.1,org.elasticsearch:elasticsearch-spark-30_2.12:7.12.1 ${SPARK_DIR}/code/sparkStreaming.py



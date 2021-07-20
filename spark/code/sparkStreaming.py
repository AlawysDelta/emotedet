from pyspark.conf import SparkConf
import pyspark.sql.types as tp
from pyspark import SparkContext
from pyspark.sql.session import SparkSession
from pyspark.ml.feature import IndexToString, RegexTokenizer, StopWordsRemover, CountVectorizer, StringIndexer
from pyspark.ml.classification import LogisticRegression
from pyspark.ml import Pipeline
from pyspark.ml.evaluation import MulticlassClassificationEvaluator
from pyspark.sql.functions import from_json, current_timestamp

#creating schema to filter Kafka messages' wanted fields
lyricsSchema= tp.StructType([
    tp.StructField(name='id',dataType=tp.StringType(), nullable=True ),
    tp.StructField(name='title',dataType=tp.StringType(), nullable=True ),
    tp.StructField(name='artist',dataType=tp.StringType(), nullable=True ),
    tp.StructField(name='lyrics',dataType=tp.StringType(), nullable=True ),
     tp.StructField(name='header_image_url',dataType=tp.StringType(), nullable=True )
])

#creating schema to read dataset
schema= tp.StructType([
    tp.StructField(name='emotion',dataType=tp.StringType(), nullable=True ),
    tp.StructField(name='id',dataType=tp.StringType(), nullable=True ),
    tp.StructField(name='lyrics',dataType=tp.StringType(), nullable=False )
])

#configuring Spark with ES address and port, autocreating the ES index
conf = SparkConf().set("es.nodes", "elastic")\
                .set("es.port", "9200")\
                .set("es.index.auto.create", "true")

#starting Spark
sc = SparkContext(appName="EmoteDet", conf=conf)
sc.setLogLevel("WARN")
spark = SparkSession(sc)


#reading the dataset
trainingSet = spark.read.csv("/opt/spark/dataset/DATA.csv",
                            schema=schema,
                            header=True,
                            sep=';')


#dropping null lines to fix NullExceptions
trainingSet = trainingSet.na.drop(subset="lyrics")
#creating StopWord list, using the default one and appending song-related stopwords
removerToGetList = StopWordsRemover(inputCol="words", outputCol="wordsSanitized")
stopWordList = removerToGetList.getStopWords()
stopWordList.extend(['verse', 'refrain', 'intro', 'outro', 'bridge', 'chorus', '1', '2', '3', 're','pre', 'oh', 'll', 'solo', 've', 'yeah', 'm', 'urlcopyembedcopy'])


#tokenizing the lyrics field into single words
stage_1 = RegexTokenizer(inputCol="lyrics", outputCol="words", pattern='\\W')
#removing stopwords
stage_2 = StopWordsRemover(inputCol="words", outputCol="wordsSanitized", stopWords=stopWordList)
#get frequency vectors to work with Logistic Regression
stage_3 = CountVectorizer(inputCol="wordsSanitized", outputCol="vector", minDF=1.0)
#assigning and index to each emotion to work with Logistic Regression
stage_4 = StringIndexer(inputCol="emotion", outputCol="emotionLabel")
#classifying lyrics into an emotion using Logistic Regression
model = LogisticRegression(featuresCol="vector", labelCol="emotionLabel")

#creating ML Pipeline
pipeline = Pipeline(stages=[stage_1, stage_2, stage_3, stage_4, model])

#Fitting the Pipeline with the dataset
pipelineFit = pipeline.fit(trainingSet)

#getting the label table for the emotion indexes
labels = pipelineFit.stages[3].labels

#Transforming the dataset to evaluate accuracy
evaluationData = pipelineFit.transform(trainingSet)

#De-index the prediction to get the predicted emotion
reindexer = IndexToString(inputCol="prediction", outputCol="predictedEmotion", labels=labels)

#Evaluate accuracy
evaluator = MulticlassClassificationEvaluator(labelCol="emotionLabel", predictionCol="prediction")
accuracy = evaluator.evaluate(evaluationData)
print(accuracy)


#Reading from Kafka topic "emotedet" using Structured Stream, reading from earliest offset to get all the tracks processed
trackDataFrame = spark \
                .readStream \
                .format("kafka") \
                .option("kafka.bootstrap.servers", "kafkaserver:9092") \
                .option("subscribe", "emotedet") \
                .option("startingOffsets", "earliest").load()

#Format the dataframe using the schema and tanking only the value from Kafka 
trackDataFrame = trackDataFrame.selectExpr("CAST(value AS STRING)") \
                .select(from_json("value", lyricsSchema).alias("data")) \
                .select("data.*")

#Passing data through the ML Pipeline to get the predicted Emotion, selecting only necessary fields
trackDataFrame = reindexer.transform(pipelineFit.transform(trackDataFrame)).select('id', 'title', 'artist', 'lyrics','wordsSanitized', 'header_image_url', 'predictedEmotion')


#Writing data on ES to visualize with Kibana
trackDataFrame.withColumnRenamed('wordsSanitized', 'words').withColumn("timestamp", current_timestamp()).writeStream \
            .option("checkpointLocation", "/save/location")\
                .format("es")\
                .start("emotedet")\
                .awaitTermination()


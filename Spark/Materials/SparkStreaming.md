# Need for Streaming

Sensors, IoT devices, social networks, and online transactions are all generating  data that needs to be monitored constantly and acted upon quickly. Fraudulent bank transactions requires testing transactions against pre trained fraud models as the transactions occur (i.e. as data streams) to quickly stop fraud in its track. All this need Real time Stream processing. While files such as csv, json, Parquet, etc need Batch Processing.

RDD, DF, Spark SQL work well with Batch data but not Streaming data. It is not possible to have Action - Transformation whole workflow say every second. But in Spark Streaming if a job is started it will keep running and in every second will keep on producing output.

If Spark streaming is performed on structured stream data then it is called **structured streaming**. In case of a structured data it is called as **DStream**. 

# Stream Processing Architecture

Modern distributed Stream processing Pipelines execute as follows:

- Receive Streaming data from data sources (live logs, IoT device data, etc.) into some data ingestion system like Kafka, Amazon Kinesis, etc.
- Process the data in parallel on a cluster. This is what stream processing engines are designed to do.
- Output The results out to downstream systems like HBase, Cassandra, Kafka, etc

# Challenges in Traditional Streaming Systems

Traditional architecture using continuous operators are simple and natural model. However, with today’s trend towards large scale and more complex real time analytics, this traditional architecture has also met some challenges We designed Spark Streaming to satisfy the following requirements:

- **Fast Failure and Straggler Recovery**: With greater scale, there is a higher likelihood of a cluster node failing or unpredictably slowing down (i.e. Stragglers); when Nodes run 24/7 there is high probability of the nodes failing. The system must be able to automatically recover from failures and stragglers to provide results in real time. Unfortunately, the static allocation of continuous operators to worker nodes makes it challenging for traditional systems to recover quickly from faults and stragglers. 
- **Load balancing**: Uneven allocation of the processing load between the workers can cause bottlenecks in a continuous operator system. This is more likely to occur in large clusters and dynamically varying workloads. The system needs to be able to dynamically adapt the resource allocation based on the workload.
- **Unification of Streaming, Batch and Interactive Workloads** : In many use cases, it is also attractive to query the streaming data interactively (after all, the streaming system has it all in memory), or to combine it with static datasets (e g pre computed models) This is hard in continuous operator systems as they are not designed to the dynamically introduce new operators for ad hoc queries This requires a single engine that can combine batch, streaming and interactive queries.
- **Advanced Analytics like Machine Learning and SQL Queries** : More complex workloads require continuously learning and updating data models, or even querying the “latest" view of streaming data with SQL queries Again, having a common abstraction across these analytic tasks makes the developer’s job much easier.

# Receiver Reliability

There are two kinds of data sources based on their reliability.

Sources like Kafka and Flume allow the transferred data to be acknowledged.

If the system receiving data from these reliable sources acknowledges the received data correctly, it can be ensured that no data will be lost due to any kind of failure. This leads to two kinds of receiver:

- **Reliable Receiver** - Correctly sends acknowledgment to a reliable source when the data has been received and stored in Spark with Replication. Ex: Kafka, Flume.
- **Unreliable Receiver** - Doesn’t send acknowledgement to a source. This can be used for sources that do not support acknowledgement, or even for reliable sources when one does not want or need to go into the complexity of acknowledgement. Ex: Fitbit or any other IoT API

# Performance Tuning

Getting best performance out of a Spark Streaming application on a cluster requires a bit of tuning. At a high level, you need to consider two things:

- Reducing processing time of each batch of data Reducing the processing time of each batch of data by efficiently using the cluster resources

- Setting the right batch size such that batches of data can be processed as fast as they are received (that is, data processing keeps up with the data ingestion). 

  In a streaming job data will keep on coming, for Ex say 10 rows (records) of data arrives in every second, this is the mini-batch - every second not 10 records.  Minimum batch size for spark streaming can be 500 Milliseconds, it has proven to be good minimum for many applications. Best approach is to start with a larger size (around 10 seconds) and work your way down to smaller batch size.

# Spark Structured Streaming

Structured Streaming is Apache Spark’s streaming engine which can be used for doing near real time analytics.  Ex: say a ride hailing company wants to monitor it's cars for over speeding, it will create a near Real time streaming application application to calculate the average speed of vehicles every few seconds.

<img src=".\asset\Spark-StructuredStreaming-UseCase.PNG" style="zoom:80%;" />

## Micro Batch Streaming v/s Continuous Processing

In **Micro Batch Streaming** is, spark waits for a very small interval say 1 second (or even 0 seconds i.e., as soon as possible) and batches together all the events that were received during that interval into a micro batch. This micro batch is then scheduled by the Driver to be executed as Tasks at the Executors. After a micro batch execution is complete, the next batch is collected and scheduled again. This scheduling is done frequently to give an impression of streaming execution. 

<p float="left">
    <img src=".\asset\SparkStreaming_Batch_1.PNG"  style="zoom:50%;"/>
    <img src=".\asset\SparkStreaming_Batch_2.PNG"  style="zoom:60%;"/>
</p>



**Continuous Processing** (released in version 2.3 as a new execution engine) does not do micro batching. Instead, it launches long running tasks that read and process incoming data continuously. It does not launch a new task every few seconds.  The long tasks keeps on running whether data is coming or not does not matter. It is like a polling system when data comes it will process.

<p float="left">
    <img src=".\asset\SparkStreaming_Continuous_1.PNG"  style="zoom:50%;"/>
    <img src=".\asset\SparkStreaming_Continuous_2.PNG"  style="zoom:50%;"/>
</p>

# Checkpointing

Say system failure happens at 70 seconds, in that case al the data till 70 seconds will not be lost, it will be stored in the HDFS location as provided in the checkpoint location. 

# Read, Process, Write

1. Input

   ```python
   input = spark.read
   		.format("json")
       	.stream("source-path") # indicates reading a stream 
   ```

2. Process (Transformations)

   ```python
   result = input
   		.select("device", "signal")
       	.where("signal > 15")
           
   result = input.avg("signal") # continuously compute avg across all devices
   
   result = input.groupBy("device-type")
   		 .avg("signal") # continuously compute avg signal foreach type of device
   
   result = input.groupBy(
       			"device-type"
       			,window("event-type", "10 min")
   			).avg("signal") # Continuously compute average signal of each type of device in last 10 minutes using event-time
   ```

3. Write - to target (Action)

   ```python
   result.write
   	  .format("parquet")
         .start("dest-path") # Action
   ```

`start("dest-path")` is like Action, only `start("dest-path")` will start execution.

# Event Time and Processing Time

Event Time is the time at which an event is generated at the source system. Processing Time is the time at which Spark receives an event.

<img src=".\asset\SparkStreamingProcessingTimes.PNG" style="zoom:80%;" />

The red dot in the above image is the message, which originates from the vehicle, then flows through the Kafka topic to Spark’s Kafka source and then reaches executor during task execution. There could be a slight delay (or maybe a long delay if there is any network connectivity issue) between these points. The time at the source is what is called an Event Time, the time at the executor is what is called the Processing Time. 

You can think of the ingestion time as the time at when it was first read into the system at the Kafka source (Ingestion Time is not relevant for spark).

# Tumbling Window and Sliding Window

A **tumbling window** is a non overlapping window, that tumbles over every “window size”. e.g., for a Tumbling window of size 4 seconds, there could be window for [00:00 to 00:04), [00:04 to 00:08), [00:08 to 00:12) etc (ignoring day, hour etc here). If an incoming event has EventTime 00:05, that event will be assigned the window [00:04 to 00:08).

A **Sliding Window** is a window of a given size(say 4 seconds) that slides every given interval(say 2 seconds). That means a sliding window could overlap with another window. For a window of size 4 seconds, that slides every 2 seconds there could windows [00:00 to 00:04), [00:02 to 00:06), [00:04 to 00:08) etc. Notice that the windows 1 and 2 are overlapping here. If an event with EventTime 00:05 comes in, that event will belong to the windows [00:02 to 00:06) and [00:04 to 00:08).

<img src=".\asset\SparkStreamingSlidingWindow.PNG" style="zoom:80%;" />

# Output Modes

Each time the result table is updated, the developer wants to write the changes to an external system, such as
S3, HDFS, or a database. We usually want to write output incrementally. For this purpose, Structured Streaming provides three output modes:

<img src=".\asset\StructuredStreamingOPModes.PNG" style="zoom:80%;" />

- **Append**: Only the new rows appended to the result table since the last trigger will be written to the external storage. This is applicable only on queries where existing rows in the result table cannot change (e.g. a map on an input stream).
- **Complete** : The entire updated result table will be written to external storage (sink). It rewrites full output to the sink.
- **Update** : Only the rows that were updated in the result table since the last trigger will be changed in the external storage. It updates changed records in-place. This mode works for output sinks that can be updated in place, such as a MySQL table.

Not every Output Mode is applicable to every Destination Type. Like HDFS does not support Update and Append will create small files issue. Thus Complete mode is used with HDFS.

# Triggers

Triggers define when data is output, as output modes define. It is basically when streaming should check for new data and update it's output.

- **Default**: Process each micro-batch as soon as the previous one has been processed, giving lowest latency possible for new result. However this can lead to writing of many small output files when the sink is a set of files. Thus spark also supports triggers based on processing time.
- **Fixed Interval**: This is one of the triggers based on processing time. It looks for new data (micro batch) in a fixed interval.
- **One-time**: Processes all the available data as a single micro batch and then automatically stops the query.
- **Continuous Processing**: Long-running tasks that continuously read, process and write data as soon as events are available.

# Watermark

Watermark is used in Spark Streaming to bound the state size. We have to be able to drop old aggregates that are not going  to be updated any more. For this we muse Watermark. 

Watermark is a moving threshold in event-time that trails behind the maximum event-time seen by the query in the processed data. The trailing gap defines how long we will wait for late data to arrive. By knowing the point at which no more data will arrive for a given group, we can limit the total amount of state that we need to maintain for a query. For example, suppose the configured maximum lateness is 10 minutes. That means the events that are up to 10 minutes late will be allowed to aggregate. And if the maximum observed event time is 12:33, then all the future events with event-time older than 12:23 will be considered as “too late” and dropped. Additionally, all the state for windows older than 12:23 will be cleared. You can set this parameter based on the requirements of your application — larger values of this parameter allows data to arrive later but at the cost of increased state size, that is, memory usage and vice versa.

```python
windowedCountsDF = \
  eventsDF \
  .withWatermark("eventTime", "10 minutes") \
  .groupBy(
      "deviceId",
      window("eventTime", "10 minutes", "5 minutes")
   ) \
  .count()
```

![watermark_img](.\asset\SparkStreamingWatermark.png)

Further reading [here](https://databricks.com/blog/2017/05/08/event-time-aggregation-watermarking-apache-sparks-structured-streaming.html).

# Fault Tolerance

End - to - end Fault Tolerance is guaranteed through Checkpointing and write-ahead-logs, Idempotent sinks and Re-playable data sources. 

Structured streaming sources, sinks and underlying execution engine works together to track the progress of stream processing. In case of a failure the streaming engine attempts to restart / re-process the data. This process only works if the source is re-playable. To assure fault tolerance structured streaming assumes every streaming source has offsets. Structured streaming sinks are designed to be idempotent, ie. they generate the same written data for given input whether one or multiple writes are performed. If a node fails while writing out data, it will overwrite the micro-batch based on the offsets.  Re-playable data sources along with idempotent sinks allow structured streaming to ensure end-to-end exactly once semantics under any failure condition.

So below is the general semantics of a streaming query:

```python
spark.readStream
	<input config>
    .filter()
    .groupBY()
    .writeStream
    <sink config>
    .start() # starts the streaming (action)
```

# Use Cases

Many big data applications need to process large data streams in real time, such as:

- Continuous ETL
- Website Monitoring, ex: Clickstream Analysis
- Fraud detection
- Advertisement Monetization
- Social media analysis
- Financial market trends
- Event-based data, Ex: IoT sensors, etc.

# Spark Structured Streaming vs DStreams

# Example Query

```python
spark.readStream
	.schema(dataScema)
    .option("maxFilesPerTrigger", 1)
    .parquet(eventsPath)
    .filter(col("event_name")=="finalize")
    .groupBy("traffic_source")
    .count()
    .writeStream
    .outputMode("append")
    .format("parquet")
    .queryName("program_ratings")
    .trigger(processingTime="3 seconds")
    .option("checkpointLocation", checkpointPath)
    .start(outputPathDir)
```

# App deployment in PySpark

Spark code can be  run either through pyspark (spark shell for python) or spark-submit. spark-submit allows to run applications in **cluster mode** (also in **client mode**) , and in different cluster managers.

## Client vs Cluster Mode

Spark deployment mode (`--deploy-mode`) specifies where to run the driver program of your Spark application/job. Spark provides two deployment modes, `client` and `cluster`. 

In **client** mode, the driver runs locally on the machine from where you are submitting your application using spark-submit command. Client mode is majorly used for interactive and debugging purposes. Note that in client mode only the driver runs locally and all tasks run on cluster worker nodes. In a typical **Cloudera cluster**, you submit the Spark application from the Edge node hence the Spark driver will run on an edge node. In a **Spark Standalone Cluster**, the driver runs on a master node (dedicated server) with dedicated resources.

- The default deployment mode is client mode.
- In client mode, if a machine or a user session running **spark-submit** terminates, your application also terminates with status fail.
- Using Ctrl-c after submitting the spark-submit command also terminates your application.
- Client mode is not used for Production jobs. This is used for testing purposes.
- Driver logs are accessible from the local machine itself.

Also important to note **Network Overhead** in case of **client mode**. As data needs to be moved between the driver and the worker nodes across the network (between the submitting machine(driver machine) and the cluster), depending on the network latency you may notice performance degradation.

In **cluster** mode, the driver runs on one of the worker nodes, and this node shows as a driver on the Spark Web UI of  the Spark application. Cluster mode is used to run production jobs.

- Terminating the current session doesn’t terminate the application. The application would be running on the cluster. 
- Since Spark driver runs on one of the worker node within the cluster, which reduces the data movement overhead between submitting machine and the cluster.
- For the Cloudera cluster, you should use yarn commands to access driver logs.
- In this spark mode, the chance of network disconnection between driver and spark infrastructure reduces. As they reside in the same infrastructure(cluster), It highly reduces the chance of job failure.



# TODO

Join Stream data with batch data.

spark-submit : pyspark vs spark shell

TODO: If data is being written to disk every second then how do we calculate . Where is the streaming unbounded table stored and how is it handled? If we do not retain all data in unbounded table (see slides), then how over all average is calculated every 5 seconds?

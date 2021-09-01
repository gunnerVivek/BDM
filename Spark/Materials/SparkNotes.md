# What is Spark?

- Spark is a fast in-memory data-processing engine.
- Ability to efficiently execute streaming, machine learning or SQL workloads which require fast iterative access to data sets.
- Can run on top of Apache Hadoop YARN, Mesos & Kubernetes
- It can cache data set in memory and speed up iterative data processing. Is  ~100 folds faster than MR, in benchmark tests. The speed up is direct benefit of write speed of RAM over HDD.
- Spark facilitates Custom code, SQL, Realtime streaming, ML, etc. It is called the Swiss Army knife of Data World.

# Hadoop Map Reduce Limitations

Here by MapReduce, we mean MapReduce and associated technologies like Hive. 

- Hive / MapReduce is based on disk based computing.
- Suitable for single pass computations, not iterative computations. Needs a sequence of MR jobs to run iterative tasks.
- Needs integration with several other frameworks / tools to solve Big data use cases. Such as Apache Storm for stream data processing, Mahout for ML, etc.

These days MR / Hive are only used for maintaining old code bases. Hive is used only in situations where DW kind of job requirements and also since SQL developers are readily available. Slowly all these jobs are being migrated to Spark.

# Spark Performance

- Spark processes data in memory, while MR persist back to disk after a MapReduce Job. So spark outperforms MR.
- Nonetheless, spark needs a lot of memory. If data is too big to fit in memory, then there will be major performance degradation for Spark.
- MR kills its job as soon as it's done, So it can run alongside other services with minor performance differences.
- Till Spark has an advantage as long as we are  talking about iterative operations on data.



How many partitions is created in RDD?

One important parameter for parallel collections is the number of *partitions* to cut the dataset into. Spark will run one task for each partition of the cluster. Typically you want 2-4 partitions for each CPU in your cluster. Normally, Spark tries to set the number of partitions automatically based on your cluster. However, you can also set it manually by passing it as a second parameter to `parallelize` (e.g. `sc.parallelize(data, 10)`). Note: some places in the code use the term slices (a synonym for partitions) to maintain backward compatibility.

With less number of partitions 1, fault tolerance will not work as lineage graph cannot be created.

# Spark Core Concepts

- Spark is built around the concepts of RDD and DAG representing transformations and dependencies between them.
- Spark Application - often referred to as Driver Program or Application Master (only when using YARN; a hive job, a MR job, a spark job all are application masters) - at high level consists of SparkContext and user code which interacts with it creating RDDs and performing a series of transformations to achieve final result.
- These transformations of RDDs are then translated into DAG and submitted to Scheduler to be executed on set of worker nodes.

# TODO

lineage vs DAG

how many executers

relation between rdd partitions and num executers

how many partitions

allow for pipelined execution on same cluster in narrow transformation?

which transformations cause narrow vs wide transformation? which types of transforamtions casue shuffle?

what is co - partitioned join?

how to know which RDD is cached in the memory?

# DataFrame  Transformations 

All the below pyspark transformation functions can be found at `pyspark.sql.functions`.

- **Aggregations**

  - **Grouping data**

    - `groupBy`: groups the DF based on specified columns. returns a grouped data object in python. Ex: `df.groupBy("state", "district")`.

  - **Grouped data methods**: These methods  are applied only on already grouped dataframe

    Example: `count(), avg(), sum(), agg()`. The `agg()` method allows to use other transformations on a resulting column such as `alias()`.

  - **Built - in aggregate functions**: In addition to the grouped data functions that we can apply to a grouped data object, we also have a set of aggregate functions that we can import from the built in `functions` module.

- **Datetime**: date_format, add_months, dayofweek, from_unixtime, minute, unix_timestamp, to_date, cast("timestamp") / cast(TimestampType()), date_add.

- **Complex Types**: Built - in String and Collection functions. union, unionByName (df method), explode, array_contains, element_at, collect_set

- **Additional Functions**: Some more non - aggregate functions, DF NA Functions.

  - Non - aggreagte built - in functions: col / column, lit, isnull, rand
  - DataFrameNaFunctions: drop, fill, replace

- **User-Defined Functions**: UDF are custom transforamtion functions. This cannot be optimized by Catalyst Optimizer. The Function has to be serialized and sent to executors which also incurs overhead. Also there is overhead from Python interpreter on executers running python UDFs. These UDFs take long to run, when compared to Pandas UDF, pyspark UDFs are magnitudes slower. 

  - **create udf**: `myUdf = udf(some_python_func)` --> serializes the function and sends it to the executers to be able to use in DF.

  - **apply udf**: `myUdf(col("some_column"))`

  - **register UDF to use in SQL**: This creates the udf in the SQL namespace, so that we can apply the function usng sql code. `spark.udf.register("sql_udf", some_python_func)`.

    Example:

    ```sql
    salesDF.createOrReplaceTempView("sales")
    spark.udf.register("sql_udf", some_python_func)
    
    %sql
    SELECT sql_udf(email) as firstname from sales;
    ```

  - **Use Decorator Syntax**: We can also make use of decorator syntax in Python. But if we declare a UDF using decorator syntax, we will no longer be able to call the local python function.

# Spark Optimization

<img src="D:\repositories\bigdata-masters\Spark\Dbrcks\asset\Catalyst-AQE.PNG" style="zoom:80%;" />

Catalyst optimizer is a general library to represent trees and applying rules to manipulate them. 

**Query** is the query using any of the available APIs, SQl, Dataframe, Dataset.

**Unresolved Logical Plan** is the set of instructions (or plan) of what the developer logically wants to happen has been received. But column names, Table names, UDFs are not yet resolved; this means they may not exist or we may have typo in our code.

**Analysis phase** is where we validate the table names, column names, UDFs etc against the Metadata Catalog. From this analysis and validation we get a logical plan.

**Optimized Logical Plan** is where the sequence of calls will be potentially re ordered or re written, form this we get an **optimized logical plan**.

**Physical Plans** is where the Catalyst optimizer determines that there are multiple ways of executing a query. For example, does it need to transfer all of the data across the network or apply prdicate push down to the source. From this planning we get one or more physical plans. A physical plan represents what the query engine wil actually do. It is distinctly different from a logical plan in that all of the optimizations have been applied. But each optimisation provides a measurably different benefit and this is the optimizations cost model. 

Each physical plan is evaluated according to its own cost model and best performing model is selected. This gives us our **selected physical plan**.

Once all the planning is done the selected physical plan is compiled down to **RDDs**. This is the same RDD that is going to be developed by a developer but it is highly unconcivable that the developer will do a better job than Catalyst Optimizer. Once these RDDs are generated they are executed in the spark core.

Query Optimization  with **Adaptive Query Execution** is new to spark 3.0 and is disabled by default and is recommended that it be enabled. Adaptive Query execution re-optimizes the execution plan of the remaining queries at the logical plan stage. It does this by dynamically switching Join strategies, coalescing shuffle partitions or optimising skew joins.

# Partitioning

Spark API uses the term core to represent a thread available for parallel execution. It is also sometimes loosely referred to as a slot. It is important to note that Spark core and underlying CPU core are not the same thing. 

To check for **#cores** in the cluster use: `sc.defaultParallelism` or `spark.sparkContext.defaultParallelism`.

To check for **#partitions** of data use: `df.rdd.getNumPartitions()`. 

If our goal is to process 1M records in parallel we need to divide that data up. If we have 8 slots (cores) available for parallel execution then it makes sense to have 1M / 8 = 125K records per partition. It is not co-incedental that we talked about 8 cores and same number of partitions. There are number optimisations built into the readers, they will look into the number of slots and the size of the data and  then make a best guess as to how many partitons it should create. The data can double in size multiple times the readers will still read in 8 partitions of data untill data increases to such a huge size where spark forgoes optimization and reads in 10 partitions of data.

<img src="D:\repositories\bigdata-masters\Spark\Dbrcks\asset\coalese vs repartition.PNG" style="zoom:80%;" />

Which to use between Coalesce and Repartition?

Coalesce cannot increase #partitions, this means if need is to increase #partitions then repartition is the obvious choice. However, Coalesce is a Narrow transformation, but is most probably not going to give a relatively balanced distribution. 

Generally we want to make **#partitions a multiple of #cores**. That way every core is being used and every core is being assigned a task. Example: Say we have 8 slots. In this case if we have 5 partitions than we are underutilizing the number of cores. But if we have 9 partitions then we will double the time taken for completing the task, because first 8 partitions will be executed parallelly than we will need to wait for completion of the 9th partition.

There are some rough guidelines around the size of each partition, which is around 200MB. This is largely from experience and is based on efficiency and not so much on resource limitation. 

Whenever wide operations are used data is shuffled, and once data is huffled it has to re-partioned. To get default shuffle partitions use `spark.conf.get("spark.sql.shuffle.partitions")` and to set use `spark.conf.set("spark.sql.shuffle.partitions", "8")` .

## General Partitioning Guidelines

- Err on the side of too many small than too few large partitions
- Don't allow partition size to increase > 200MB per 8GB of core total memory. For small data target 3 partitions per core.
- Size default shuffle partitions by dividing largest shuffle stage input by the target partition size.
  Eg: 4TB / 200MB = 20, 000 shuffle partition count.

AQE dynamically coalesces shuffled partitions, when running queries in spark to deal with very large data, shuffle has a very big impact on query performance. Shuffle can be an expensive operator because it has to move data across the network. Which means data is re-distributed in a way that is required by downstream operators. One key property of this shuffling is the number of partitions. Thmis number can be hard to tune because it depends on a number of factors; if too few partitions   then data size of each partiions will be too large and the partitions might end up needing to spill data to disk as a result it slows down the query. But too many pations will end with very small data sizes on each partition and there are going to be many small network data fetches to read these shuffled blocks which also slows down the query. AQE on spark helps avoid some of these problems.

# Structured Streaming


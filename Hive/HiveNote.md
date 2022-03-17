Hive is not a DBMS. It allows for duplicate, and there is no Primary key & Foreign key constraints in Hive.

No sharding in Hive.

```sql
CREATE TABLE IF NOT EXISTS mydb.employees (
  name         STRING COMMENT 'Employee name',
  salary       FLOAT  COMMENT 'Employee salary',
  subordinates ARRAY<STRING> COMMENT 'Names of subordinates',
  deductions   MAP<STRING, FLOAT>
               COMMENT 'Keys are deductions names, values are percentages',
  address      STRUCT<street:STRING, city:STRING, state:STRING, zip:INT>
               COMMENT 'Home address')
COMMENT 'Description of the table'
LOCATION '/user/hive/warehouse/mydb.db/employees'
TBLPROPERTIES ('creator'='me', 'created_at'='2012-01-02 10:00:00', ...);
```

# Data Load

Load operations are currently pure copy/move operations that move datafiles into location corresponding to Hive tables.

`create table if not exists
saurav_tbl_csv
(
id string,
name string,
marks int
)
row format delimited
fields terminated by ','
STORED AS TEXTFILE;` -- this makes sure that the data is in format ready to accept csv input, by default it is ORC file format

It is not mandatory to provide location while creating an Internal Table, the table will be created in the default location (/user/hive/warehouse). However for External tables it is mandatory to provide location ([see below](#types-of-tables-in-hive)).

```sql
LOAD DATA LOCAL INPATH '/tmp/saurav.csv' INTO TABLE saurav_tbl_csv; -- the input file does not need to be in HDFS
```

- file path can refer to a file (in which case Hive will move the file into the table) or it can be a directory (in which case Hive will
  move all the files within that directory into the table).
- If the keyword LOCAL is specified, then the load command will look for file path in the local file system.
- If a relative path is specified, it will be interpreted relative to the user's current working directory.
- The load command will try to copy all the files addressed by file path to the target file system.
- The table will be created in distributed mode across Data nodes.

### OVERWRITE

```sql
LOAD DATA LOCAL INPATH '/tmp/saurav.csv' OVERWRITE INTO TABLE saurav_tbl_csv;
```

Overwrite acts as Truncate + Insert statement. By default data is appended to the table, however If the OVERWRITE keyword is used then the contents of the target table (or partition) will be deleted and replaced by the files referred to by file path .

**How store query output to file system**?

## Quiz

Q• Identify the correct options
1. *The SQL like queries in Hive are translated to MapReduce jobs*.
2. *We can not access hive tables without Metastore*.
3. A table with less records will have lesser entries in Metastore as compared to tables with larger records.
4. EXPLAIN gives the Abstract Syntax Tree of execution and then executes the MR job.

# Types of tables in Hive

- **Internal Table**

  Internal Table is also called managed table; Hive manages the life cycle.

  When a DROP TABLE command is run it it drops the data (the file location in HDFS), and it also drops the metadata (Metastore).

  **Use Internal Table** when the data is temporary and you want Hive to completely manage the lifecycle of the table and data. This is generally the situation in case of processing tables, for example we want to create a joined table from multiple tables for processing BI queries from it. This joined table can be an Internal table.

- **External Table**

  When you drop an external table, it only drops the meta data. The data does not get deleted from HDFS.
  Thus it is evident that the external table is just a pointer on HDFS data.

  When creating an external table it is mandatory to provide location. Where as for internal table it is not; data will be written to the default location /user/hive/warehouse.

  ```sql
  create external table table_name (
    id int,
    myfields string
  )
  location '/my/location/in/hdfs'; -- 
  ```

  **Use External table** in case of Landing Table, i.e. the data ingestion into HDFS is managed by Hive. The data is also used outside of Hive, and needs to persist Data needs to remain in the underlying location even after a DROP TABLE. This can
  apply if you are pointing multiple schemas (tables or views) at a single data set or if you are iterating through various possible schemas.
  Hive should not own data and control settings,dirs , etc., you have another program or process that will do those things.

  You are not creating table based on existing table (AS SELECT).

# Complex Data Types

Complex types can be built up from primitive types and other composite types. Data type of the fields in the collection are specified using an angled bracket notation, ie. complex_type<data_type>.
Currently Hive supports four complex data types. They are:

1. **ARRAY**
   array<datatype>

   An Ordered sequences of similar type elements that are indexable using zero based integers.
   It is similar to arrays in Java.

   Example: `array ('1', 'bala', 'praveen');`
   Second element is accessed with array[1].

2. **MAP**

   `map<primitive_type, data_type>`

   Collection of key-value pairs.

   Fields are accessed using array notation of keys (e.g., [‘key’]).

3. **STRUCT**

   `STRUCT<col_name : data_type [COMMENT col_comment ], ...>`
   It is a It is a record type which encapsulates a set of named fields that can be any primitive data type.

   Elements in STRUCT type are accessed using the DOT (.) notation. Example -- For a column `c` of type `STRUCT { a INT; b INT}` the `a` field is accessed by the expression `c.a`

4. **UNION** Type

   `UNIONTYPE<data_type , data_type , ...>`

   It is similar to Unions in C.

   At any point of time, an Union Type can hold any one (exactly one) data type from its specified data types.

   So basically if there is a possibility that a column can have multiple data types, use Union type.

## Example of  Complex Data Types

**Sample Data File**:

> 101	first:Amit, last:Mishra	bbsr,751204	Hadoop, Hive
> 102	first:Michael, last:Chopra	bnglr,1235667	Hadoop, Hive, Pig

**Creating the Table**:

```sql
CREATE TABLE complex_data_type
(
    emp_id int,
    name map<string, string>,
    location struct<city: string, pin: int>
    skill_set array<string>
)
ROW FORMAT DELIMITED FILEDS TERMINATED BY '\t' -- field separator
collection items terminated by ',' -- inside every filed items seperator
map keys terminated by ':'  -- only for map complex type
;
```

**Loading data into the table**:

```sql
LOAD DATA LOCAL INPATH '/home/hive/example_data/complex_data.tsv'
OVERWRITE INTO TABLE complex_data_type
;
```

**Querying the Table**:

```sql
-- 
SELECT emp_id, name['first'], location.city, skill_set[0] FROM complex_data_type;
```

If a **non - existent key** is provided than **NULL** will be returned, not Key Error.

## QUIZ

Q. Identify Correct Options

1. We can not insert data in external tables.
2. *We can store integers in STRING array, in which data will be implicitly converted*.
3. We can not have a single Hive tables with different complex types.
4. *Struct can contain different data types referred by different names*.

# Hive Variables

You can define variables on the command line or inside script (hql files) so that you can reference in Hive scripts to customize execution. 

Inside the CLI, variables are displayed and changed using the SET command. 

Hive’s variables are internally stored as Java Strings. 

You can reference variables in queries; Hive replaces the reference with the variable’s value before sending the query to the query processor.

Similar to temporary variables in SQL Server.

| Namespace | Access     | Description                                                  |
| --------- | ---------- | ------------------------------------------------------------ |
| hivevar   | Read/Write | User - defined custom variables <br/>This is **default** name space used for **referring a variable**. Referring means while using Select statement. |
| hiveconf  | Read/Write | Hive - specific configuration properties. <br/>Initially, variable substitution was not part of hive and when it got introduced, all the user-defined variables were stored as part of this as well. Which is definitely not a good idea. So other namespaces - hivevar and system -  were created. <br/>hiveconf is still the **default** namespace, so if you don't provide any namespace while **declaring variable**, it will store your variable in hiveconf namespace. |
| system    | Read/Write | Configuration properties defined by Java                     |
| env       | Read Only  | Environment variables defined by the shell environment.      |



```sql
hive> set hivevar:var1 = "variable-value";
hive> select ${hivevar:var1};
hive> select ${var1}; -- same as above because hivevar is default for reference

hive> set var2 = "some-other-value"; -- this will go to hiveconf by default
hive> select ${hiveconf:var2};
```

The same behaviour can also be achieved from **command line** :

**-hiveconf** option is used for all properties that configure Hive behavior.
**-f** is used for specifying the script file

```shell
% hive -hiveconf CURRENT_DATE='2012-09-16' -f test.hql
```

**-e** option is used to execute query in a single shot. 

**-S** starts execution in silent mode (no logs will be produced).

```sql
hive -e "select * from tbl_name;" -- directly run Hive query from shell without logging 
hive -f query.hql -- most production friendly
```

In **$HOME/.hiverc** file, one can specify a file of commands for the CLI to run as it starts, before showing you the prompt. Hive automatically looks for a file named .hiverc in your HOME directory and runs the commands it contains, if any.

These files are convenient for commands that you run frequently, such as setting system or adding Java archives (JAR files) of custom Hive extensions to Hadoop’s distributed cache.

# SORT BY vs ORDER BY vs DISTRIBUTE BY  vs CLUSTER BY in Hive

<h2>SORT BY </h2>

Hive uses sort by to sort the data based on the data type of the column to be used for sorting per reducer i.e. overall sorting of output is not maintained. e.g. if column is of numeric type the data will be **sorted per reducer** in numeric order.

Sort By compared to Order By is much faster; no data shuffle is happening in Sort By.

<h2>ORDER BY</h2>

Very similar to ORDER BY of SQL. The overall sorting is maintained in case of order by and output is produced in single reducer. Hence, we need to use limit clause so that reducer is not overloaded.

There are some **limitations** in the order by clause. Order by can be run either in strict or  nonstrict mode.

In **strict mode** (ie. hive.mapred.mode=strict), the order by clause has to be followed by a LIMIT clause. The limit clause is not necessary in **nonstrict** mode (ie. hive.mapred.mode=nonstrict). 

The reason is that in order to impose total order of all results, there has to be one reducer to sort the final output. If the number of rows in the output is too large, the single reducer could take a very long time to finish.

It is good practice to use order by with LIMIT clause. 

<h2>DISTRIBUTE BY</h2>

Hive uses the columns in Distribute By to distribute the rows among reducers. All rows with the same Distribute By columns will go to the same reducer. However, Distribute By does not guarantee clustering or sorting properties on the distributed keys.

```sql
Select * from tbl_name DISTRIBUTE BY country;
```

In the above query, it is not guaranteed that all the rows for each country will be sent to a separate reducer, all that is guaranteed is that  all the rows from any one single country will go to the same reducer.

<h2>CLUSTER BY</h2>

Cluster By is a short cut for both Distribute By and Sort By. First data is distributed to each reducer by the distribute by clause and than data is sorted for each of the reducer nodes.

Except ORDER  BY rest all can be mentioned in a create table statement.

# Partitioning

Hive organizes tables horizontally into partitions. It helps to improve performance, because the queries now only need to query a partition instead of scanning the whole table. This is also called partition pruning, where we provide the name of the partition in the query (WHERE clause).

• It is a way of dividing a table into related parts based on the values of partitioned columns such as date, city, department etc.

• Using partition, it is easy to query a portion of the data.

• Partitioning can be done based on more than column which will impose multi dimensional structure on directory storage.

• In Hive, partitioning is supported for both managed and external tables.

• The partition statement lets Hive alter the way it manages the underlying structures of the table’s data directory.

• In case of partitioned tables, subdirectories are created under the table’s data directory for each unique value of a partition column.

• When a partitioned table is queried with one or both partition columns in criteria or in the WHERE clause, what Hive effectively does is partition elimination by scanning only those data directories that are needed.

• If no partitioned columns are used, then all the directories are scanned (full table scan) and partitioning will not have any effect.

```sql
-- show the partitions in the table
hive> show patitions table-name;
```



## Types of Partitions

<h3>Static Partioning</h3>

Static Partitioning is applied, when we know data (supposed to be inserted) belongs to which partition. Here the partition directory will be created manually. 

An ALTER statement is used to add each of the Partitions manually. 

```sql
ALTER TABLE log_messages ADD PARTITION(year = 2012, month = 1, day = 2)
LOCATION 'hdfs://master_server/data/log_messages/2012/01/02';
```

 To *modify* the *partition location* of an already created partition:

```sql
ALTER TABLE log_messages PARTITION(year = 2011, month = 12, day = 2)
SET LOCATION 's3n://ourbucket/logs/2011/01/02';
```



<h3>Dynamic Partitioning</h3>

• In static partitioning, every partitioning needs to be backed with individual hive statement which is not feasible for large number of partitions as it will require writing of lot of hive statements.

• In that scenario dynamic partitioning is suggested as we can create as many number of partitions with single hive statement.

• When using Dynamic Partitioning with external table, location is not provided.

• The columns in the PARTITION BY clause is not part of the CREATE statement.

```sql
CREATE EXTERNAL TABLE IF NOT EXISTS log_messages (
	hms INT,
	severity STRING,
	server STRING,
	process_id INT,
	message STRING
)
PARTITIONED BY (year INT, month INT, day INT)
ROW FORMAT DELIMITED FIELDS TERMINATED BY '\t';
```

We cannot do dynamic partitioning on an existing table. A new table needs to be created with dynamic partition and data should be copied to the new table.

# Bucketing

Bucketing is file level operation where as Partitioning is directory level operation. Bucketing can be used with Partitioning.

Ex: Say there is a competition with thousands of competitors participating from each Country. The results of the competition needs to be stored by ranking the participants from each country specific to their own country. In such a situation The result table will be Partitioned by Country and Bucketed by Rank of the competitor from the country.

Number of Reduce tasks will be equal to number of buckets provided.

CLUSTERED BY clause is used to create buckets.  Physically each bucket is a file in the directory and bucket numbering is 1 - based.

```sql
-- We will however need to look at number of partitions created
-- if there are competitors from 100+ countries than it amy become a performance issue
-- The partitioning here is mostly for illustration purposes only

CREATE TABLE IF NOT EXIST competition_result(
	user_id STRING
    , rank INT 
    , p_language STRING
    , experience_years INT
    , highest_edu_level STRING
    , degree_name STRING
    , has_computing_degree STRING
    , highest_computing_edu_level STRING
)
PARTTIONED BY (country STRING)
CLUSTERED BY (rank) into 4 buckets 
STORED AS TEXTFILE
LOCATION '/usr/usr_name/competition_result/'
ROW FORMAT DELIMITED FIELDS TERMINITATED BY '|'
;
```

- Bucket is physically a file in the table directory hierarchy.  Generally used with partitioning for obatining highest level of optimisation, thus directory is partitions.
- We can explicitly set number of buckets during table creation 
- Sometimes bucketing alone is better for optimisation. Ex: say there are 100 departments, then it is not advisable to use Partitioning as it will create 100 partitions (small file issue). In this case we can use Bucketing alone, as number of buckets can be manually specified with CREATE.
- Bucketed tables produce faster Joins. Because while joining data from right table with that of left table, it knows exactly in which bucket the data is present instead of needing to scan whole partition. However there is a condition to perform this bucketed join operation:
  - Both tables to be joined should be bucketed on the same column - joining column
  - Both tables should have  same number of buckets

- Efficient table sampling on bucketed tables.

Limitation is that it does not ensure if data is properly loaded in the table, we have to handle this data loading by ourselves.

# Big Data File Types - AVRO, ORC, PARQUET

Due to quantum of the data generally involved in the Big data sphere, following properties are desired of any prospective file type:

- get Read fast
- get Written fast
- Be Split-able; so that multiple tasks can be run on parts of file
- Support advanced compression through various compression codecs like LZO, Snappy, BZip, etc.
- Support Schema evolution; allowing to adjust for evolving schemas schemas.

However, it is not possible for any single file type to provide all of the above options. Some formats provides faster read with a little compromise on write and schema-evolution, where as other file formats provide faster write with compromise on reads and compression. Still there are compromises between files being split-able and compression.

## Text Files (Csv, Tsv)

Text files provide good write performance but bad write performance.  Hence, These files are good for dumping data from a DB of HDFS.

This files are by default split-able at new line characters.

Text files do not support block compression and thus compressing text files in Hadoop often comes at a read performance cost. We need to use a file level compression codec like Bzip2. 

Schema evolution has very limited support in text files as it does not store metadata but only data. New fields can only be appended to existing fields while old fields can never be deleted.



## Avro

Avro is a file format + a serialization de-serialization framework. Avro uses JSON for defining data types (Schema) and serializes data in a compact binary format. Every Avro file contains two components one is binary data and alongside with it a schema inthe form of JSON.

Read / Write performance of AVRO is average, with comparatively better write performance as to read.  Thus if your application is mainly dealing with I/O operations than it  is not the best format to go with.

Supports block compression and are split-able. 50 - 55% data compression is achievable.

AVRO supports Full Schema Evolution. It stores meta data separately is avsc (avro schema) file. So if one column from schema definition does not appear in the data, Hive will default it to some value specified in the avsc file.

Fields can be renamed, added, deleted while old files can still be read with new schema. 

Provides rich data structures like record, enum, array, map, etc.

Converting a normal data into an Avro file is called a serialization.

Extension for every avro file is .avro , and for Avro Schema file is .avsc.

**Avro Object**

An Avro object container file consists of :

- A File header
- Followed by one or more file data blocks.

![](.\assets\avro_physical_file.PNG)

The above schema :

![](.\assets\avro_schema.PNG)



Since the Schema is already part of the file; now when reading the file we do not need to supplement any external schema i.e. we do not need to know any schema before reading the file.



# Joins and Types

## Shuffle Join

![](.\assets\shuffle-join.PNG)

This is the default join type. All the data records (from both tables) with same key on which the tables are to be joined are shuffled to the same reducer, thus requiring higher data movement. Thus this method is resource intensive and is the slowest among all the joins.

But the advantage is that Shuffle Join works with All sizes of data (although slow) and layouts of data.



## Broadcast Join -- aka Map-Side join

In Broadcast Join one table is broadcasted (copied) to each node in the cluster. Mapper than scans through other large table to perform the join. Since one table is already available in each of the node, thus shuffle and sort can be reduced and data is joined locally at the Mapper avoiding unnecessary data movement due to shuffle. 

Thus it is very fast, with the caveat that the table to be broadcasted must be small enough to fit in RAM.

This kind of Joins are useful in Star Schema situations, where Dimension tables are good candidate for broadcasting.

What happens when both the tables being joined are too big and neither can fit in memory? Sort - Merge - bucket Join.



## Sort Merge Bucket Join

It is another example of map side join. Mappers take advantage of co-location of joining keys to do efficient joins.

Following criteria must be meet:

1. All Tables must be bucketed.
2. #Buckets in the Big table must be divisible by number of buckets of each of the small tables in the query.
3. Join columns in the query must be the Bucket columns from the table.

In sort Merge Bucket Join we divide the tables into equal number of buckets, this guarantees all records with same join key value is in the same bucket. First the data is sorted and then 

Only works for equi join conditions.

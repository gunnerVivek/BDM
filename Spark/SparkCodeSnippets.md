# Databricks Platform Specific

**Magic commands** : `%python` ,`%scala`, `%sql`, `%sh`, `%fs` and `%md` are the available magic commands.

**Render Html**: use `displayHTML` (available in Python, Scala, and R)

```python
html = """<h1 style="color:orange;text-align:center;font-family:Courier">Render HTML</h1>"""
displayHTML(html)
```

## Access DBFS

- Run file system commands on DBFS using magic command: `%fs`

  ```shell
  # by default list the root folder
  # same as %fs ls /
  %fs ls
  
  # View Head of a file
  %fs head /databricks-datasets/README.md
  
  # Displays information about what is mounted within DBFS.
  # The returned information includes the mount point,
  # source directory, and encryption type.
  %fs mounts
  
  # This provides help text for dbutils.fs
  %fs help
  # provides help text for mounts
  %fs help mounts
  ```

- Run file system commands on DBFS using DBUtils directly

  ```python
  # ls command
  dbutils.fs.ls("/databricks-datasets")
  
  # get help text on any function
  dbutils.widgets.help("multiselect")
  ```

- Visualize results in a table using the Databricks display function

  ```python
  files = dbutils.fs.ls("/databricks-datasets")
  display(files)
  ```

## Add Notebook Parameters with widgets

There are 4 types of widgets:

- `text`: Input a value in a text box.
- `dropdown`: Select a value from a list of provided values.
- `combobox`: Combination of text and dropdown. Select a value from a provided list or input one in the text box.
- `multiselect`: Select one or more values from a list of provided values.

### Widgets Using SQL

```sql
-- Create a text input widget using SQL.
CREATE WIDGET TEXT state DEFAULT "CA";

-- Access the current value of the widget
-- using the function `getArgument`
SELECT *
FROM events
WHERE geo.state = getArgument("state");

# remove the text widget
REMOVE WIDGET state;
```

### Widgets in Python

To create widgets in Python, use the DBUtils module: `dbutils.widgets`

```python
# create a text widget: name, efaultValue, label
dbutils.widgets.text("name", "Brickster", "Name")

# create a multi select widget: name, defaultValue, choices, label
dbutils.widgets.multiselect("colors", "orange", ["red", "orange", "black", "blue"], "Traffic Sources")

# Access the current value of the widget
name = dbutils.widgets.get("name")

# Remove all Widgets
dbutils.widgets.removeAll()
```

# Spark SQL API

## Use Spark Session to run SQL query

`spark.sql()` returns a DataFrame.

```python
budgetDF = spark.sql("""
SELECT name, price
FROM products
WHERE price < 200
ORDER BY price
""")

# View result in returned DataFrame
budgetDF.show() # will print data in tabular format, 20 rows by default
```

## Replicate SQL query with Dataframe Transformations

```python
# 
budgetDF = (productsDF
  .select("name", "price")
  .where("price < 200")
  .orderBy("price")
)
```

## Create a DataFrame from Table

```python
# create a dataframe from products table
productsDF = spark.table("products")
```

##  Acccess schema of DataFrame

```python
# prints in pretty format
productsDF.printSchema()

# prints Non-pretty format; StructType()
productsDF.schema
```

# Reader & Writer

## Read from CSV

- Infer Schema automatically

  ```python
  usersCsvPath = "/mnt/training/ecommerce/users/users-500k.csv"
  
  usersDF = (spark.read
    .option("sep", "\t") # tab seperator
    .option("header", True)
    .option("inferSchema", True)
    .csv(usersCsvPath))
  
  usersDF.printSchema()
  ```

  

- Manually define Schema with struct type

  ```python
  from pyspark.sql.types import LongType, StringType, StructType, StructField
  
  usersCsvPath = "/mnt/training/ecommerce/users/users-500k.csv"
  
  # Define the Schema
  userDefinedSchema = StructType([
    StructField("user_id", StringType(), True),
    StructField("user_first_touch_timestamp", LongType(), True),
    StructField("email", StringType(), True)
  ])
  
  usersDF = (spark.read
    .option("sep", "\t")
    .option("header", True)
    .schema(userDefinedSchema)
    .csv(usersCsvPath)
  )
  ```

  

- Manually define Schema with DDL formatted string

  ```python
  usersCsvPath = "/mnt/training/ecommerce/users/users-500k.csv"
  
  DDLSchema = "user_id string, user_first_touch_timestamp long, email string"
  
  usersDF = (spark.read
    .option("sep", "\t")
    .option("header", True)
    .schema(DDLSchema)
    .csv(usersCsvPath)
  )
  ```

  

## Read from JSON

  -  with Infer Schema

    ```python
    eventsJsonPath = "/mnt/training/ecommerce/events/events-500k.json"
    
    eventsDF = (spark.read
      .option("inferSchema", True)
      .json(eventsJsonPath))
    
    eventsDF.printSchema()
    ```

    

  -  with Manually defined Schema with StructType

    ```python
    from pyspark.sql.types import ArrayType, DoubleType, IntegerType, LongType, StringType, StructType, StructField
    
    userDefinedSchema = StructType([
      StructField("device", StringType(), True),
      StructField("ecommerce", StructType([
        StructField("purchaseRevenue", DoubleType(), True),
        StructField("total_item_quantity", LongType(), True),
        StructField("unique_items", LongType(), True)
      ]), True),
      StructField("event_name", StringType(), True),
      StructField("event_previous_timestamp", LongType(), True),
      StructField("event_timestamp", LongType(), True),
      StructField("geo", StructType([
        StructField("city", StringType(), True),
        StructField("state", StringType(), True)
      ]), True),
      StructField("items", ArrayType(
        StructType([
          StructField("coupon", StringType(), True),
          StructField("item_id", StringType(), True),
          StructField("item_name", StringType(), True),
          StructField("item_revenue_in_usd", DoubleType(), True),
          StructField("price_in_usd", DoubleType(), True),
          StructField("quantity", LongType(), True)
        ])
      ), True),
      StructField("traffic_source", StringType(), True),
      StructField("user_first_touch_timestamp", LongType(), True),
      StructField("user_id", StringType(), True)
    ])
    
    eventsDF = (spark.read
      .schema(userDefinedSchema)
      .json(eventsJsonPath))
    ```

    

  - Manually Schema can also be specified using DDL Schema

## Read from Parquet

```python
df = spark.read.parquet(eventsPath)
```



## Write DataFrame to File

```python
usersOutputPath = workingDir + "/users.parquet"

(usersDF.write
  .option("compression", "snappy")
  .mode("overwrite")
  .parquet(usersOutputPath)
)
```

## Write Dataframe to Tables

Use `saveAsTable`, it creates a **global table**, unlike the local view created by the DataFrame method `createOrReplaceTempView`

```python
usersDF.write.mode("overwrite")\
	   .saveAsTable("users_p") # Gobal Table 
```

Note: A database must be selected using the USE clause or else it will be written to default DB.

## Write DataFrame to Delta Table

```python
eventsOutputPath = workingDir + "/delta/events"

(eventsDF.write
  .format("delta") # Delta format
  .mode("overwrite")
  .save(eventsOutputPath)
)
```

# DataFrame and Column Operations

## Construct Columns

```python
from pyspark.sql.functions import col

col("device")
eventsDF.device
eventsDF["device"]
```

```python
revDF = eventsDF \
	.filter(col("ecommerce.purchase_revenue_in_usd").isNotNull()) \ 
  	.withColumn("purchase_revenue", (col("ecommerce.purchase_revenue_in_usd") * 100).cast("int")) \
	.withColumn("avg_purchase_revenue",
                col("ecommerce.purchase_revenue_in_usd") / col("ecommerce.total_item_quantity")
               ) \
  	.sort(col("avg_purchase_revenue").desc())

display(revDF)
```

### `select() `vs `withColumn()`

`withColumn()` creates new projection for every withColumn statement, but the transformations applied can be used in next step . Select however although does not create 

```python
datetimeDF = (df
              .withColumn("ts", (col("ts") / 1e6).cast("timestamp")) # this will transform the column in place because we have provided same name as original column
              .withColumn("date", to_date("ts"))
)


## Using select()
datetimeDF_1 = (df.select(
   				"user_id"
				, (col("ts")/1e6).cast(TimestampType()).alias("ts")
				, to_date((col("ts")/1e6).cast(TimestampType())).alias("date") # here we needed to again divide by 1 Mil; In select we are selecting columns in parallel no transformation to the original column
	)
)
```

### `select()` and `withColumn()`

We can use withColumn() and  select() together as well. 

```python
detailsDF = (df.withColumn("items", explode("items"))
  .select("email", "items.item_name")
  .withColumn("details", split(col("item_name"), " "))
)
```



## Subset Columns

- `select()`: Selects a set of columns or column based expressions

  https://www.geeksforgeeks.org/how-to-add-multiple-columns-in-pyspark-dataframes/

  https://www.geeksforgeeks.org/select-columns-in-pyspark-dataframe/

  ```python
  devicesDF = eventsDF.select("user_id", "device")
  display(devicesDF)
  ```

  **Select Multiple Columns and use UDF** 

  ```python
  from pyspark.sql.functions import col
  from pyspark.sql.functions import udf
  from pyspark.sql.types import StringType
  
  # this UDF is needed to mimic apply as in Pandas
  is_warrant = udf(lambda x: 'Y' if x == "warranty" else 'N', StringType())
  
  locationsDF = eventsDF.select("user_id",
    col("geo.city").alias("city"),
    col("geo.state").alias("state"),
    is_warrant("event_name").alias("is_warrant") # used UDf to mimic apply
  )
  
  display(locationsDF)
  ```

  

- `selectExpr()`: Selects a set of SQL expressions

  ```python
  # user_id  |  apple_user
  # -------- | -----------
  # UA01073  |  true
  appleDF = eventsDF.selectExpr("user_id", "device in ('macOS', 'iOS') as apple_user")
  ```

  

- `drop()`: Returns a new DataFrame after dropping the given column, specified as a string or column object. Use strings to specify multiple columns

  ```python
  # column list can either be string or col() - can't be mixed
  anonymousDF = eventsDF.drop("user_id", "geo", "device")
  noSalesDF = eventsDF.drop(col("ecommerce"))
  ```



## Add or Replace columns

- `withColumn()`: Returns a new DataFrame by adding a column or replacing the existing column that has the same name

  ```python
  mobileDF = eventsDF.withColumn("mobile", col("device").isin("iOS", "Android"))
  purchaseQuantityDF = eventsDF.withColumn("purchase_quantity", col("ecommerce.total_item_quantity").cast("int"))
  ```

  

- `withColumnRenamed()`: Returns a new DataFrame with the provided column renamed to new column.

  ```python
  # geo column will be renamed to location
  locationDF = eventsDF.withColumnRenamed("geo", "location")
  ```



## Subset Rows

- `filter()`: Filters rows using the given SQL expression or column based condition. Alias `where()`.

  ```python
  purchasesDF = eventsDF.filter("ecommerce.total_item_quantity > 0")
  purchasesDF = eventsDF.filter(eventsDF.ecommerce["total_item_quantity"] > 0)
  revenueDF = eventsDF.filter(col("ecommerce.purchase_revenue_in_usd").isNotNull())
  
  # multiple filter conditions
  androidDF = eventsDF.filter(  (col("traffic_source") != "direct")
                              & (col("device") == "Android")
                             )
  ```

  

- `dropDuplicates()`: Returns a new DataFrame with duplicate rows removed, optionally considering only a subset of columns. Alias `distinct()`.

  ```python
  eventsDF.distinct()
  distinctUsersDF = eventsDF.dropDuplicates(["user_id"])
  ```

  

- `limit()`: Returns a new DataFrame by taking the first n rows.

  ```python
  # first 100 rows
  limitDF = eventsDF.limit(100)
  ```



## Sort Rows

- `sort()`: Returns a new DataFrame sorted by the given columns or expressions. Alias `orderBy()`.

  ```python
  increaseTimestampsDF = eventsDF.sort("event_timestamp")
  increaseTimestampsDF = eventsDF.sort("event_timestamp", ascending=False) # descending
  decreaseTimestampsDF = eventsDF.sort(col("event_timestamp").desc()) # descending
  increaseSessionsDF = eventsDF.orderBy(["user_first_touch_timestamp", "event_timestamp"])
  decreaseSessionsDF = eventsDF.sort(
      					col("user_first_touch_timestamp").desc() # descending
                            , col("event_timestamp") # ascending
  					)
  ```

# Aggregation

## Grouping Data

Use the DataFrame `groupBy()` method to create a grouped data object.

```python
# group by single column
df.groupBy("event_name")
# group by multiple columns
df.groupBy("geo.state", "geo.city")
```

## Grouped Data methods

Various aggregate methods are available on the grouped data object.

```python
eventCountsDF = df.groupBy("event_name").count()

avgStatePurchasesDF = df.groupBy("geo.state").avg("ecommerce.purchase_revenue_in_usd")

cityPurchaseQuantitiesDF = df.groupBy("geo.state", "geo.city").sum("ecommerce.total_item_quantity")
```

## Built-in aggregate function : `agg()`

Use the grouped data method `agg()` to apply built-in aggregate functions. This allows you to apply other transformations on the resulting columns, such as `alias()`.

```python
from pyspark.sql.functions import sum

# Aggregate using agg()
# NOTICE: groupBy column has been aliased as "province"
df.groupBy(df["geo.state"].alias("province"))\
  .agg(sum("ecommerce.total_item_quantity").alias("total_purchases"))
```

### Apply multiple aggregate functions on grouped data.

```python
from pyspark.sql.functions import avg, approx_count_distinct

stateAggregatesDF = df.groupBy("geo.state").agg(
  avg("ecommerce.total_item_quantity").alias("avg_quantity"),
  approx_count_distinct("user_id").alias("distinct_users")
)
```

# Datetime Functions

## Cast to Timestamp: `cast()`

Casts column to a different data type, specified using string representation or DataType.

```python
timestampDF = df.withColumn("purchaseTime", (col("timestamp") / 1e6).cast("timestamp")) # string
# OR
from pyspark.sql.types import TimestampType
timestampDF = df.withColumn("purchaseTime", (col("timestamp") / 1e6).cast(TimestampType())) # DataType
```

## Format Date: `date_format()`

Converts a date/timestamp/string to a string formatted with the given date time pattern. See valid date and time format patterns for [Spark 3](https://spark.apache.org/docs/latest/sql-ref-datetime-pattern.html).

```python
from pyspark.sql.functions import date_format

formattedDF = (timestampDF
               .withColumn("date string", date_format("timestamp", "MMMM dd, yyyy"))
               .withColumn("time string", date_format("timestamp", "HH:mm:ss.SSSSSS"))
)
```

## Extract datetime attribute from timestamp: `year()`, `month()`, etc. 

```python
from pyspark.sql.functions import year, month, dayofweek, minute, second

datetimeDF = (timestampDF
  .withColumn("year", year(col("timestamp")))
  .withColumn("month", month(col("timestamp")))
  .withColumn("dayofweek", dayofweek(col("timestamp")))
  .withColumn("minute", minute(col("timestamp")))
  .withColumn("second", second(col("timestamp")))
)	
```

## `to_date()` and `date_add()`

```python
from pyspark.sql.functions import to_date, date_add

dateDF = timestampDF.withColumn("date", to_date(col("timestamp"))) # to_date
plus2DF = timestampDF.withColumn("plus_two_days", date_add(col("timestamp"), 2)) # date_add
```



# Miscellaneous Functions Commentary

## `explode()` vs `explode_outer()`

Both of them **creates new Rows** for each element of the column to be exploded, but `explode_outer` unlike `explode` will create a new row even for **NULL** values of exploded column.


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

```sql
LOAD DATA LOCAL INPATH '/tmp/saurav.csv' INTO TABLE saurav_tbl_csv; -- the input file does not need to be in HDFS
```

- filepath
  can refer to a file (in which case Hive will move the file into the table) or it can be a directory (in which case Hive will
  move all the files within that directory into the table).
- If the keyword LOCAL is specified, then the load command will look for filepath in the local file system.
- If a relative path is specified, it will be interpreted relative to the user's current working directory.
- The load command will try to copy all the files addressed by filepath to the target filesystem.
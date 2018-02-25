DROP TABLE IF EXISTS cloud;

CREATE EXTERNAL TABLE cloud (
    word_2 STRING,
    leng STRING    
)
ROW FORMAT SERDE 'parquet.hive.serde.ParquetHiveSerDe'
 STORED AS
 INPUTFORMAT 'parquet.hive.DeprecatedParquetInputFormat'
 OUTPUTFORMAT 'parquet.hive.DeprecatedParquetOutputFormat'
LOCATION '/raw/cloud';

select * FROM cloud;
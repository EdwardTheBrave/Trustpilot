DROP TABLE IF EXISTS reviews;

CREATE EXTERNAL TABLE reviews (
    businessUnit_id string,
    consumer_id string,
    displayName string,
    numberOfReviews bigint,
    stars bigint,
    title string,
    `text` string,
    language string,
    createdAt string,
    referralEmail string,
    referenceId string,
    isVerified boolean
)
ROW FORMAT SERDE 'parquet.hive.serde.ParquetHiveSerDe'
 STORED AS
 INPUTFORMAT 'parquet.hive.DeprecatedParquetInputFormat'
 OUTPUTFORMAT 'parquet.hive.DeprecatedParquetOutputFormat'
LOCATION '/raw/reviews';
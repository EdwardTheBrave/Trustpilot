# encoding: utf-8

from pyspark.sql import HiveContext
from pyspark import SparkContext

sc = SparkContext(appName = "Reviews App")
log4jLogger = sc._jvm.org.apache.log4j 
log = log4jLogger.LogManager.getLogger(__name__) 

sqlContext = HiveContext(sc)

log.warn("Lectura de los datos en formato JSON")

datos = sqlContext.read.json("/raw/json")
datos.registerTempTable("reviews_data")

log.warn("Proceso")
df = sqlContext.sql("""
SELECT 
    r.businessUnit.id as businessUnit_id,
    r.consumer.id as consumer_id,
    r.consumer.displayName as displayName,
    r.consumer.numberOfReviews as numberOfReviews,
    r.stars,
    r.title,
    r.text,
    r.language,
    r.createdAt,
    r.referralEmail,
    r.referenceId,
    r.isVerified
FROM reviews_data
     LATERAL VIEW explode(reviews) adTable AS r
    """)

df.show()
df.printSchema()

print("Total Reviews: %d" % df.count())

log.warn("Salida a un fichero Parquet")

df.write.parquet("/raw/reviews", mode="overwrite")

log.warn("Done")
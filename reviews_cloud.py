from pyspark.sql import HiveContext
from pyspark import SparkContext
from pyspark.sql.types import *

def split_text(text):
    return [w.lower() for w in text.split(' ')]

sc = SparkContext(appName = "Cloud App")
log4jLogger = sc._jvm.org.apache.log4j 
log = log4jLogger.LogManager.getLogger(__name__)

sqlContext = HiveContext(sc)

log.warn("Lectura de los datos en formato JSON")

datos = sqlContext.read.json("/raw/json")
datos.registerTempTable("cloud_data")

log.warn("Proceso")

sqlContext.udf.register("split_text", split_text, ArrayType(StringType()))
df = sqlContext.sql("""
    SELECT explode(split_text(r.text)) as word 
    FROM cloud_data LATERAL VIEW explode(reviews) adTable AS r
""")

df.show()
df.printSchema()

print("Total Reviews: %d" % df.count())

log.warn("Salida a un fichero Parquet")

df.write.parquet("/raw/cloud", mode="overwrite")

log.warn("Done")
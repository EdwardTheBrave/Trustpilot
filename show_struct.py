# encoding: utf-8

from pyspark.sql import SQLContext
from pyspark import SparkContext

sc = SparkContext(appName = "Simple App")
log4jLogger = sc._jvm.org.apache.log4j 
log = log4jLogger.LogManager.getLogger(__name__) 

sqlContext = SQLContext(sc)

log.warn("Lectura de los datos en formato JSON")

datos = sqlContext.read.json("/raw/json")
datos.printSchema()
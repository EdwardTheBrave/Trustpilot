# Mi primer proyecto: Trustpilot

En este proyecto se pretende facilitar el código necesario para descargar las valoraciones de los usuarios de tu empresa en Trustpilot, ingestarlas en HDFS, estructurarlas con Spark y utilizar una herramienta de visualización como Tableau para visualizar los datos a través de Impala. Se trata de mi primer mini proyecto de Big Data completo desde la extracción de datos hasta la visualización, sed benévolos!.

Algunos datos (los mínimos necesarios) han sido suprimidos por motivos de confidencialidad y privacidad de la empresa. Datos tales como el API key, Secret Key, Token, etc. deberán sustituirse por los de la empresa con la que se quiera replicar este código para obtener sus propias valoraciones. No obstante, se avisará durante todo el proceso cuando sea necesario sustituir algún dato y este vendrá indicado en el código entre <>.

Todo el ejercicio se desarrolla dentro de la máquina virtual de Cloudera CDH 5, no obstante, si se dispone de las herramientas necesarias se podrá ejecutar en cualquier entorno real de Big Data.

¡Comencemos!

Herramientas y software que necesitaremos:

- Python (es posible que tengas que actualizar la versión si algo no funciona pero no debería ser necesario)
- Spark
- Hive2
.
.
.

Primero, un poco de configuración básica de la máquina de la mano de @dvillaj (ignora este paso si trabajas con software actualizado y un entorno real de Big Data, seguramente tengas todo lo necesario).

Instalación de Python


````
cd
wget https://repo.continuum.io/miniconda/Miniconda2-latest-Linux-x86_64.sh
chmod a+x Miniconda2-latest-Linux-x86_64.sh
./Miniconda2-latest-Linux-x86_64.sh -b
sudo rm Miniconda2-latest-Linux-x86_64.sh

echo '' >> $HOME/.bashrc
echo '# Python' >> $HOME/.bashrc

echo 'export PYTHONIOENCODING=utf8' >> .bashrc
echo 'export PATH=$HOME/miniconda2/bin:$PATH' >> .bashrc
source $HOME/.bashrc
python --version
````

Si la versión de Anaconda es la 2.7.14 todo ha ido bien, sino revisa el proceso!

Hora y Editor por Defecto

```
cd
sudo cp /etc/localtime /root/old.timezone
sudo rm /etc/localtime
sudo ln -s /usr/share/zoneinfo/Europe/Madrid /etc/localtime

cat <<EOF >>~/.bash_profile
export VISUAL="nano"
export EDITOR="nano"
EOF
source $HOME/.bash_profile
```

Spark

```
sudo ln -s /usr/lib/hive/conf/hive-site.xml /usr/lib/spark/conf/hive-site.xml
sudo cp /etc/spark/conf/log4j.properties.template /etc/spark/conf/log4j.properties

sudo sed -i 's/log4j.rootCategory=INFO/log4j.rootCategory=WARN/' \
/etc/spark/conf/log4j.properties
```


¡Ahora sí, comienza lo divertido!

Primero, vamos a clonar este repositorio en la máquina virtual para ahorrarnos los pasos de crear algunos directorios. 

```
cd
git clone https://github.com/EdwardTheBrave/trustpilot

```

Puedes comprobar si todo ha ido bien situándote en tu directorio de usuario y ejecutando el comando "ls". Si ha aparecido el directorio "Trustpilot" vas por buen camino. Explóralo accediendo a él y comprueba que tiene los mismos archivos que en la web. A continuación accedemos al directorio y nos aseguramos de que los ejecutables tienen los permisos necesarios para ejecutarse.

```
cd
cd trustpilot/

chmod a+x get_reviews_trustpilot.py
chmod a+x show_struct.py
chmod a+x reviews.py
chmod a+x tabla.hql

ls
```

Ahora deberían aparecer todos los ficheros de la carpeta con el mismo color (el que tenga tu consola configurado como ejecutable).

Para continuar vamos a modificar el script de get_reviews_trustpilot.py para introducir en él los datos de nuestra empresa que comentaba al principio, y que han sido suprimidos por motivos de confidencialidad y privacidad. Para ello primero accedemos al script en modo edición.

```
nano get_reviews_python.py
```

Modificamos dentro del script las siguientes líneas de comando con la información pertinente en cada una (te las muestro a continuación para que no te dejes ninguna):

```
1. payload = "grant_type=password&username=<email de un usuario de la empresa con acceso a Trustpilot Business>&password=<contraseña de ese usuario>"
2. 'Authorization': "Basic <API Key + Secret Key de la empresa cifradas en Base64>",
3. url = "https://api.trustpilot.com/v1/private/business-units/<Id de tu empresa o business unit ID>/reviews"
4. querystring = {"token":"<token obtenido con la petición anterior>","perPage":"1", "page":"1", "orderBy":"createdat.desc"}
5. 'authorization': "Basic <API Key + Secret Key de la empresa cifradas en Base64>",
```

Una vez tengas los datos, sal del con el comando "ctr+X", indicando que sí deseas guardar los cambios y manteniendo el nombre del fichero.

Estamos listos para ejecutar el primer script. Para ello, ejecutamos la siguiente línea y esperamos (ten en cuenta que revisa todas las valoraciones una a una por lo que si tu empresa tiene muchas puede tardar un poco).

```
python get_reviews_trustpilot.py
```

Si ejecutamos el comando "ls" veremos que se ha creado un nuevo fichero con el nombre trustpilot_reviews_%%% donde %%% son las tres primeras letras del día de la semana en que lo has ejecutado. Lo siguiente que tenemos que hacer es crear en hadoop los directorios que vamos a utilizar e ingestar el fichero creado en hdfs, para ello:

```
hadoop fs -mkdir -p /raw/json
hadoop fs -mkdir -p /raw/reviews

hadoop fs -put <nombre del fichero a ingestar> /raw/json
```

De forma opcional, si se quisiera consultar la estructura del fichero y comprobar que la API de Trustpilot nos ha devuelto un JSON bien estructurado podemos ejecutar el script de show_struct con Spark.

```
spark-submit show_struct.py
```

Continuamos, ya tenemos el fichero ingestado en el entorno hdfs. Sin embargo, el JSON que devuelve la API de Trustpilot es algo enreversado como para tratarlo directamente con hive tal y como está. Para limpiarlo un poco y poder crear las tablas más tarde, utilizamos el script de reviews. Además, comprobamos que el directorio de hadoop que hemos creado como /raw/reviews almacene el fichero de SUCCESS y los ficheros formato Parquet 

```
spark-submit reviews.py

hadoop fs -ls /raw/reviews
```

Si todo está en orden, procedemos a crear la tabla con la información que hemos extraído en Hive. Para ello podemos hacerlo de dos maneras:

Primera forma:
```
beeline -u jdbc:hive2:// -f tabla.hql
```

Segunda forma: Para el caso de que la primera forma de error, o nos sea dificil de comprender, yo recomiendo abrir el navegador y acceder a HUE. HUE se accede poniendo en la URL "localhost:8888". En la pantalla de login introduces usuario y contraseña, en nuestro caso ambos son "cloudera". Por defecto vendrá la versión 4, cambiamos a la versión 3 y abirmos el editor de querys de Hive. En este editor copiamos el contenido del fichero tabla.hql:

```
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
LOCATION '/json/reviews';
```

Una vez hecho esto nos debe de haber aparecido una nueva tabla a la izquierda con las columnas que aparecen en el script de arriba. Ahora, si ejecutamos cualquier query de SQL debería devolver el resultado de la query sin errores. Para ver la estructura mejor prueba a introducir en Hive:

```
select * from reviews limit 30;
```
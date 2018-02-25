# My first Big Data project: Trustpilot at a glance

The aim of this project is to facilitate the necessary code to download your customers' reviews from Trustpilot, intake them in HDFS, struct them with Spark and use Tableau as a visualization tool to visualize the data through Impala. It is my first complete small Big Data project from the data extraction to the data visualization, don't be so hard!

Some information (just the indispensable) has been deleted due to privacy and confidential reasons. Relevant data as the API key, Secret Key, etc. must be replaced with your Company information about which you want to reply this exercise. However, you will be notified whenever you need to change any ditto. Said changes will be indicated with the use of <>.

This whole exercise take place under the virtual machine Cloudera CDH 5 environment. Nevertheless, if you have the necessary tools you will be able to implement it in any real Big Data ecosystem.

**Let's start!**

Necessary software and tools:

* Python (you may need to update your version if something does not work properly but this is pretty unlikely)
* HDFS
* Spark
* Hive2
* Impala
* Tableau

## Previous Configuration

First of all, a little bit of basic configuration on the virtual machina, provided by @dvillaj (ignore this step if you work with updated software and a real Big Data environment, you will probably have all the necessary tools updated)

**Installing Python**


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

If the resulting Anaconda version is 2.7.14 you did it great, otherwise have a look at the process again!

**Default Time Zone and Editor**

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

**Spark**

```
sudo ln -s /usr/lib/hive/conf/hive-site.xml /usr/lib/spark/conf/hive-site.xml
sudo cp /etc/spark/conf/log4j.properties.template /etc/spark/conf/log4j.properties

sudo sed -i 's/log4j.rootCategory=INFO/log4j.rootCategory=WARN/' \
/etc/spark/conf/log4j.properties
```


## Data ETL

Okay, now we can start with the fun!

First, we will clone this repository in the virtual machine in order to save some steps like creating directories. You may check if everything is allright by executing the "ls" command in your home directory. If you now have the "Trusstpilot" directory you are on the right path. Explorre it and check if it has the same files you see on the web.

```
cd
git clone https://github.com/EdwardTheBrave/trustpilot
```

Now, we need to modify the get_reviews_trustpilot.py script to set your Company details mentioned at the beginning of this post. In order to do this, access the script in edition mode. Change the applicable information with the one of your Company. Here I detail you all the lines to be changed so you do not miss any of them:

```
1. payload = "grant_type=password&username=<email de un usuario de la empresa con acceso a Trustpilot Business>&password=<contraseña de ese usuario>"
2. 'Authorization': "Basic <API Key + Secret Key de la empresa cifradas en Base64>",
3. url = "https://api.trustpilot.com/v1/private/business-units/<Id de tu empresa o business unit ID>/reviews"
4. 'authorization': "Basic <API Key + Secret Key de la empresa cifradas en Base64>",
```

Once you finish it, exit from the file saving the changes.

We are ready to run the first script. To do so, execute the following line and wait (take into account that this script goes through all your Company's reviews one at a time, so be patient).

```
python get_reviews_trustpilot.py
```

If you run the "ls" command you will see a new file has appeared with the following name structure "trustpilot_reviews_%%%", where %%% are the first three letters of the day of the week in which you are runing this script. The next thing to do is creating the directories of hadoop in which we will intake the file generated, to do so:

```
hadoop fs -mkdir -p /raw/json
hadoop fs -mkdir -p /raw/reviews
hadoop fs -mkdir -p /raw/cloud

hadoop fs -put <nombre del fichero a ingestar> /raw/json
```

Optionally, if you want to check the structure of the file and check if the Trustpilot API has sent back the right response (a well structured JSON) we can run the show_struct.py script with Spark:

```
spark-submit show_struct.py
```

To continue, we already have the file intaken in HDFS. However, the JSON response has a complex structure and cannot be processed with hive. We will use the reviews.py script to clean the JSON and be able to create the necessary tables. Additionally, we check that the /raw/reviews directory stores a success file and the rest of the files in Parquet format.

```
spark-submit reviews.py

hadoop fs -ls /raw/reviews
```

If everything is allright, we proceed to create the table with the extracted information in Hive. We can do it with two different approaches:

First approach:
```
beeline -u jdbc:hive2:// -f table_total.hql
```

Second approach: 

If you get an error with the first approach, or if you find it more difficult to understand or control, I suggest opening the browser and accessing to HUE. You can access HUE (with the virtual machine runing) by introducing the folowwing URL: "localhost:8888". In the login screen enter your user and password, noth of them are "cloudera" in our example. Change to the 3th version of HUE and open the queries editor of Hive. Copy the table.hql content and run it:

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

Once we have done that, there must have appeared a new table on the left pannel of the screen. Now, if you run any SQL query it should return the answer without errors. In order to appreciate the table structure, run:

```
select * from reviews limit 30;
```


To continue, we need to process the JSON information to create another table that we will use for the visualization. We will make a 'word cloud' with the words of the reviews with higher frequency. To do so, we repeat the process. Access the shell and run:

```
cd
cd trustpilot/

spark-submit reviews_cloud.py

hadoop fs -ls /raw/cloud
```

We create the table:

First approach (on the shell):
```
beeline -u jdbc:hive2:// -f table_cloud.hql
```

Second approach (from Hive on HUE):
```
DROP TABLE IF EXISTS cloud;

CREATE EXTERNAL TABLE cloud (
    word string
)
ROW FORMAT SERDE 'parquet.hive.serde.ParquetHiveSerDe'
 STORED AS
 INPUTFORMAT 'parquet.hive.DeprecatedParquetInputFormat'
 OUTPUTFORMAT 'parquet.hive.DeprecatedParquetOutputFormat'
LOCATION '/raw/cloud';
```

It is at this point that we have all the information processed and the tables created. In order to have the tables available in Impala, we just need to change to the Impala editor in HUE and update the database and metadata. The last thing to do is make some value from the data. In order to do that, we will connect Tableau with Impala to make a small dashboard with the most relevant information.

## Visualization

Lastly, I have used one of the most powerful visualization softwares according to the last Gartner Magic Quadrant, Tableau. In its 10.5 version, we can directly connect it with Impala. Before you try the conection, you must download and install in your computer an ODBC Impala client, find the software and installing instructions in the following link (https://www.cloudera.com/downloads/connectors/impala/odbc/2-5-41.html).

To stablish the connection, we will choose "Hadoop Cloudera" amongst its possible conections, and configure the following settings (as long as you are using the cloudera virtual machine):
* Server: 127.0.0.1
* Host: 21050
* Type: Impala
* Authentication: Username & Password
* Username & Password: cloudera

With that done, we will have stablished the conection and we will be able to use Tableau to make any graphs we want. Here I show you an easy way to visualize your customers reviews with a 'word cloud' and a small dashboard with the information extracted from the API so you can see one of the many possible applications for this repository.

![alt text](https://github.com/EdwardTheBrave/trustpilot/blob/trustpilot/images/Cloud.png)

![alt text](https://github.com/EdwardTheBrave/trustpilot/blob/trustpilot/images/Dashboard.png)

Thank you for your time! For any doubt, my email address is eduardobravogarcia@gmail.com

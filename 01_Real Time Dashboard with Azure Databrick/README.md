# Power BI Real Time Dashboard with Azure Databricks 
In this demo we will Spark Streaming Structure to read stream from files. Then we do some aggregation or transformation before push stream data to Power BI.

## Streaming Dataset in Power BI 
There are 3 ways to create streaming dataset as below: 

![alt text](https://github.com/WipadaChan/pbi_demo_repo/blob/master/01_Real%20Time%20Dashboard%20with%20Azure%20Databrick/image/streamtype.PNG "Streaming Dataset") 

In this demo we will use stream dataset from API.

## Pre-requisite:
1. Azure Databrick cluster (up and running). To create Azure Databrick cluster, plese refer to https://docs.microsoft.com/en-us/azure/databricks/scenarios/quickstart-create-databricks-workspace-portal?tabs=azure-portal 
2. This demo use Databrick Runtime 7.2 ML
3. Power BI (Pro license)
4. Data files (Can be any files in your storage)
 

## Step:
This demo will simulate stream data by reading from file. Do data transformation before pushing result via Power BI streaming dataset API. 
1. Define input path of files location
2. Define input stream structure, how and where we read the input
3. Doing aggregation 
4. Define Stream query by writing stream output to notebook
5. Comparing the different when we add a Checkpoint ()
6. Create Power BI streaming dataset API
7. Push stream to Power BI API 
(all of these steps are in databrick notebook **readStreamFromFile.dbc**)

## Let's do this 

### Step 1. Define input path of files location
I have a folder of JSON files that mount to my Azure Databricks cluster as below location. You can change to your own data file location. 

```python
# Enter your file path
inputPath = "/mnt/training/gaming_data/mobile_streaming_events"
```

### Step 2. Define input stream structure, how and where we read the input

Here is input structure for the file in my **inputPath**, you can change this part according to your data.

```python
# Define structure 
from pyspark.sql.types import StructType, StringType, IntegerType, TimestampType, DoubleType
from pyspark.sql.functions import col, to_date

eventSchema = ( StructType()
  .add('eventName', StringType()) 
  .add('eventParams', StructType() 
    .add('game_keyword', StringType()) 
    .add('app_name', StringType()) 
    .add('scoreAdjustment', IntegerType()) 
    .add('platform', StringType()) 
    .add('app_version', StringType()) 
    .add('device_id', StringType()) 
    .add('client_event_time', TimestampType()) 
    .add('amount', DoubleType()) 
  )     
)

# load stream from file 
gamingEventDF = (spark
  .readStream
  .schema(eventSchema) # Specify defined schema
  .option('streamName','mobilestreaming_demo') 
  .option("maxFilesPerTrigger", 1)              # treat each file as Trigger event
  .json(inputPath) 
)
```

### Step 3. Doing Aggregation
This one is optional, if you want to read directly from stream you can skip this step. 
Note that when doing aggregation on streaming data, it required to write in complete mode. 
```python
# Doing sum aggregation 
agg = (gamingEventDF
        .groupBy('eventName')
        .count())
```
### Step 4. Define Stream query by writing stream output to notebook
#### ForeachBatch
Since we need to take the stream and push the stream via API. So we need a function the interact with the stream
We can apply our custom function with **ForeachBatch** (Micro Batch of Streamed data) or **Foreach** (row of  Streamed data)
##### Below we create simple function to work with Micro Batch of Streamed data

```python
# Define simple function to test with ForeachBatch
def simpleshow(df, epoch_id):
    print("epoch_id: " + str(epoch_id))
    df.show()
    pass
```

Apply **simpleshow** fucntion to **foreachBatch** 

```python
(agg.orderBy(col('count').desc())
  .writeStream
  .outputMode('complete')
  .foreachBatch(simpleshow)
  .start().awaitTermination()
  ) 
```
With this call fucntion in ForeachBatch, you will see aggreagation result print out in your notebook and see how microbatch concept work in Spark Structured Streaming.

### Step 5. Comparing the different when we add a Checkpoint ()
Define path location where you want to store check point. It can be local DBFS path or Azure storage account.
This demo connects to Azure datalake storage gen2 (ADLS Gen2)
```python
checkpoint = "abfss://mycontainer@mystorageaccount.dfs.core.windows.net/directoryname/streamfile/"
```
#### Read with checkpoint

```python
# Adding check point 
query = (agg.orderBy(col('count').desc())
  .writeStream
  .outputMode('complete')
  .option("checkpointLocation", checkpoint) 
  .foreachBatch(simpleshow)
  .start().awaitTermination()
        ) 
```
Since the first read we do not have **Checkpoint**. So it will start reading from the **frist file** again.
You can press cancel now and rerun the code again. Now it will start from the last point, we left. 


### Step 6. Create Power BI streaming dataset API
Our output from **agg** dataframe consist of 2 columns: **'eventName'** and **'count'** where the data type is text and number respectively. 
Here is the structure of our stream dataset where we will create in Power BI as follow the step here
https://docs.microsoft.com/en-us/power-bi/connect-data/service-real-time-streaming#pushing-data-to-datasets 
#### Note that the column name in Power BI Stream dataset and your streaming dataframe should be exactly the same. 

#### Define column name and type 

![alt text](https://github.com/WipadaChan/pbi_demo_repo/blob/master/01_Real%20Time%20Dashboard%20with%20Azure%20Databrick/image/streamDataset.PNG "Streaming Dataset") 

Once it done you will get a URL, copy **Push URL**

![alt text](https://github.com/WipadaChan/pbi_demo_repo/blob/master/01_Real%20Time%20Dashboard%20with%20Azure%20Databrick/image/streamDatasetdone.PNG "Streaming Dataset") 

### Step 7. Push stream to Power BI API 
#### Implement function to work with foreachBatch 
Power BI require JSON string that need to be **wrap** with array
**foreachBatch** will return **DataFrame** and Epoch_id 

So the step in function will be:
1. convert dataframe to json 
2. convert to string and wrap with []
3. push to POST request to Power BI API


```python
import requests
import datetime as dt
import pandas as pd
from pyspark.sql.functions import lit,unix_timestamp
import time
import datetime

def sendToBi (data):
  data_str = data
  newHeaders = {'Content-type': 'application/json'}
  response = requests.post('YOUR PUSH URL',
                         data=data_str,
                         headers=newHeaders)
  return print("Status code: ", response.status_code)

from pyspark.sql.functions import lit,unix_timestamp
import time
import datetime


def convertdf (df):
  df=df.na.fill("Null")
  df2 = df.toJSON().collect()
  str1 = ''.join(df2)
  str1=str1.replace("}{","},{") 
  print("[" + str1 +"]") #this is optional
  return "[" + str1 +"]" #wrap with array
  
def batchstr(df, epoch_id):
    sendToBi(convertdf(df))
    pass
```

### Now push stream data to Power BI 
```python
(agg.orderBy(col('count').desc())
  .writeStream
  .outputMode('complete')
  .option("checkpointLocation", checkpoint)
  .foreachBatch(batchstr)
  .start().awaitTermination())
  ```

### In Power BI Service 
You can now create streaming chart into a Dashboard, by adding tile to your dashboard and select **Custom Streaming Data** 
![alt text](https://github.com/WipadaChan/pbi_demo_repo/blob/master/01_Real%20Time%20Dashboard%20with%20Azure%20Databrick/image/addtile.PNG) 

Then select dataset, you've just created:

![alt text](https://github.com/WipadaChan/pbi_demo_repo/blob/master/01_Real%20Time%20Dashboard%20with%20Azure%20Databrick/image/addDataset.PNG) 

Select visualization type yopu want to add on a dashboard:

![alt text](https://github.com/WipadaChan/pbi_demo_repo/blob/master/01_Real%20Time%20Dashboard%20with%20Azure%20Databrick/image/vizType.PNG) 

Once it's done, you will see your chart with lightning icon indicate that this visual is real time streaming. 

![alt text](https://github.com/WipadaChan/pbi_demo_repo/blob/master/01_Real%20Time%20Dashboard%20with%20Azure%20Databrick/image/result.PNG) 

**Thank You** 
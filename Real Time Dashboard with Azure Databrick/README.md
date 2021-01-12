# Real Time Dashboard with Azure Databricks 
In this demo we will Spark Streaming Structure to read stream from files. Then we do some aggregation or transformation before push stream data to Power BI.

## Streaming Dataset in Power BI 
There are 3 ways to create streaming dataset as below: 

![alt text](https://github.com/WipadaChan/pbi_demo_repo/blob/master/Real%20Time%20Dashboard%20with%20Azure%20Databrick/streamtype.PNG "Streaming Dataset") 

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
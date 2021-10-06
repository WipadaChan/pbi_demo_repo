# Using Python with Power BI REST API.
Power BI REST API allow you to perform management tasks on Power BI objects like reports, datasets, and workspaces. You can try Power BI REST API with no-code option [here](https://youtu.be/fXbJeIY2CgE)

Personally I would love to work with Python, where the important part to using Python with Power BI REST API is authentication. 
Here the reference I found on [Authentication](https://bitbucket.org/omnistream/powerbi-api-example/src/master/example.py)


In this demo will show how to Push data into a Power BI dataset, follow the step from this [tutorial](https://docs.microsoft.com/en-us/power-bi/developer/automation/walkthrough-push-data)

## Pre-requisite:
**1. Power BI Account with Pro license**

**2. Azure Active Directory (Azure AD)**

    1. Create an app-register with the following [link](https://app.powerbi.com/apps)
    As we will call API to interact with dataset, so we need Dataset Read Write permission.

![alt text](https://github.com/WipadaChan/pbi_demo_repo/blob/master/04_PowerBI_REST_API/image/appregis.png "App Registry") 

    2. Take note of your Application ID 

![alt text](https://github.com/WipadaChan/pbi_demo_repo/blob/master/04_PowerBI_REST_API/image/copyAppID.png "Copy App ID")

    3. Login to Azure Portal we need to generate Secret key for our Application:
       - From Azure Portal-->Go to Azure Active Directory --> App regristration: You will see App that you just created.

![alt text](https://github.com/WipadaChan/pbi_demo_repo/blob/master/04_PowerBI_REST_API/image/appcreated.png "App created") 

       - Go to Certificate & Secret --> New Client secret and give the name and expired period you want. 

![alt text](https://github.com/WipadaChan/pbi_demo_repo/blob/master/04_PowerBI_REST_API/image/createClientSecret.png "createClientSecret") 



### Step for Push dataset to Power BI
This will be a location where you need to use when deployment model to AzureML. 
1. Get Authentication Token
2. Create dataset using Push Dataset API 
3. Add row to Power BI table

You can find full example code [here](https://github.com/WipadaChan/pbi_demo_repo/blob/master/04_PowerBI_REST_API/PowerBIRESTApi.ipynb)

## Step:
### 1. Get Authentication Token
As App register used for calling Power BI REST API has delegate permission, so it require username and password for your Azure AD account. 
Becareful not to storing your password here. 

```python
def get_access_token(application_id, application_secret, user_id, user_password):
    data = {
        'grant_type': 'password',
        'scope': 'openid',
        'resource': "https://analysis.windows.net/powerbi/api",
        'client_id': application_id,
        'client_secret': application_secret,
        'username': user_id,
        'password': user_password
    }
    token = requests.post("https://login.microsoftonline.com/common/oauth2/token", data=data)
    assert token.status_code == 200, "Fail to retrieve token: {}".format(token.text)
    #print("Got access token: ")
    #print(token.json())
    return token.json()['access_token']

access_token = get_access_token(application_id,application_secret,user_id,user_password)
```

### 2. Create dataset using Push Dataset API
Once you got a token, you can now call the REST API. We first create a dataset. With 'https://api.powerbi.com/v1.0/myorg/datasets' it will create dataset on My Workspace of your account. If you want to create dataset to specific workspace you need to use 'https://api.PowerBI.com/v1.0/myorg/groups/{GROUP_ID}/datasets' where GROUP_ID is your workspace ID that you can find in the URL when browsing to the 
workspace.

![alt text](https://github.com/WipadaChan/pbi_demo_repo/blob/master/04_PowerBI_REST_API/image/workspaceid.png "createClientSecret") 

In the below code example, we going to create dataset name SalesMarketing with 1 table name Sales and follow by columns in that table. 

```python
import requests
import json
# This will create dataset in My Workspace
create_dataset_url ='https://api.powerbi.com/v1.0/myorg/datasets'
# To create on specific Workspace 
create_dataset_url_grp = f'https://api.PowerBI.com/v1.0/myorg/groups/{GROUP_ID}/datasets'
header = {'Authorization': f'Bearer {access_token}'}

data_str={
   "name":"SalesMarketing",
   "defaultMode": "Push",
   "tables":[
      {
         "name":"Sales",
         "columns":[
            {
               "name":"OrderNumber",
               "dataType":"string"
            },
            {
               "name":"OrderDate",
               "dataType":"DateTime"
            },
            {
               "name":"ShipDate",
               "dataType":"DateTime"
            },
            {
               "name":"ProductID",
               "dataType":"Int64"
            },
            {
               "name":"Quantity",
               "dataType":"Int64"
            },
            {
               "name":"UnitPrice",
               "dataType":"Double"
            },
            {
               "name":"DiscountAmount",
               "dataType":"Double"
            },
            {
               "name":"PromotionCode",
               "dataType":"string"
            },
            {
               "name":"OriginationStateID",
               "dataType":"Int64"
            },
            {
               "name":"TotalAmount",
               "dataType":"Double"
            }
         ]
      }
   ]
}

create_dataset = requests.post(url=create_dataset_url_grp, headers=header, data=json.dumps(data_str))
```

If it created fine you will got below status:

![alt text](https://github.com/WipadaChan/pbi_demo_repo/blob/master/04_PowerBI_REST_API/image/PushDatasetResult.png "createClientSecret")

I extract Dataset ID from response result and table name for use in Add row step.

### 3. Add row to Power BI table
This step will add 2 new rows to Power BI Dataset we just created. 

```python
# This will post row to dataset on MyWorkspace
push_row_url = f'https://api.powerbi.com/v1.0/myorg/datasets/{dataset_id}/tables/{table_name}/rows'
# This will post row to dataset on Specific workspace
push_row_url_grp = f'https://api.powerbi.com/v1.0/myorg/groups/{GROUP_ID}/datasets/{dataset_id}/tables/{table_name}/rows'
header = {'Authorization': f'Bearer {access_token}'}

content={
  "rows": [
    {
      "OrderNumber": "TT02260499",
      "OrderDate": "10/5/2021",
      "ShipDate": "10/6/2021",
      "ProductID": 12,
      "Quantity": 1,
      "UnitPrice": 324.95,
      "DiscountAmount": 0,
      "PromotionCode": "",
      "OriginationStateID": 3,
      "TotalAmount": 324.95
    },
    {
      "OrderNumber": "TT02260500",
      "OrderDate": "10/5/2021",
      "ShipDate": "10/6/2021",
      "ProductID": 12,
      "Quantity": 1,
      "UnitPrice": 324.95,
      "DiscountAmount": 0,
      "PromotionCode": "",
      "OriginationStateID": 3,
      "TotalAmount": 3899.4
    }
  ]
}

pushrow = requests.post(url=push_row_url_grp, headers=header, data=json.dumps(content))
```

Now to can go to the workspace you push the dataset, you will find the dataset as below: 
![alt text](https://github.com/WipadaChan/pbi_demo_repo/blob/master/04_PowerBI_REST_API/image/datasetCreated.png "Dataset")

![alt text](https://github.com/WipadaChan/pbi_demo_repo/blob/master/04_PowerBI_REST_API/image/createReport.png "Report")

**Thank You** 
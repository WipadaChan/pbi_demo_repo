# Deploy trained model to Azure ML and use Power BI to score new data.
Power BI allow collaboration between data scientist and business users, where data scientist can share their trained machine learning model that built in AzureML. Alternatively, you may have trained model built locally or other place than AzureML and you want to share them with business users. 

This demo will show you how to deploy existing Machine Learning model that trained from H2O to Azure ML. Then use deployed model to score new data in Power BI.

**For pickle model**

If you have trained model in pickle format from your local machine, you can find example code [here](https://github.com/WipadaChan/pbi_demo_repo/blob/master/03_DeployH2O_PBI/pickleModel/DeployModelToAzureML-PBI.ipynb)


## Pre-requisite:
**1. Azure ML Workspace.**
![alt text](https://docs.microsoft.com/en-us/azure/machine-learning/media/how-to-manage-workspace/create-workspace.gif  "Create azure ml") 

**2. Trained H2O model**
**3. Enable Power BI user to access AzureML (by add users via IAM in AzureML Workspace and give a Reader Role to that users)**
 

## Train K-Mean Clustering Model with H2O
Here is an example code for model training with H2O. You can find the full notebook in below path 

[Create Customer Segment Model with H2O](https://github.com/WipadaChan/pbi_demo_repo/blob/master/03_DeployH2O_PBI/Customer%20Segment.ipynb)


### Key I would like to point here is location of the trained model in your local machine.
This will be a location where you need to use when deployment model to AzureML. 

```python
# Save Model
path = 'H2o'
model_path = h2o.save_model(model=h2o_km, path=path, force=True)
print(model_path)
```
Here is the path where H2O model is stored in my example
"..\H2o\KMeans_model_python_1619773255297_1"


## Deploy Model to Azure ML and make it accessible via Power BI
**The step below will consist of:**
1. Connecting to AzureML workspace
2. Register Model
3. Prepare Docker and dependency library
4. Prepare scoring.py script
5. Deploy to ACI webservice

Full script can find [here](https://github.com/WipadaChan/pbi_demo_repo/blob/master/03_DeployH2O_PBI/DeployModel.ipynb)

## Step:
### 1. Using AzureML.Core library to connect to your AzureML Workspace
```python
# azureml-core of version 1.0.72 or higher is required
# azureml-dataprep[pandas] of version 1.1.34 or higher is required
from azureml.core import Workspace, Dataset

subscription_id = 'XXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX'
resource_group = 'ResourceGroupName'
workspace_name = 'AzureMLWorkspaceName'

ws = Workspace.get(name=workspace_name, subscription_id=subscription_id, resource_group=resource_group )
```

### 2. Register your model from local machine to AzureML
```python
from azureml.core.model import Model
# Here is where you specify location of your stored H2O model
model = Model.register(model_path="H2o/KMeans_model_python_1619773255297_1",
                          model_name="CustomerSegment",
                          description="Classify customer segment use K-Means Clustering",
                          workspace=ws)
```

### 3. Prepare Environment and its dependency 
Due to this demo using H2O model therefore it requires specific set of enviroment configuration. 
```python
from azureml.core import Environment
#Prepare Docker and required dependency 
myenv = Environment(name="myenv")
myenv.docker.enabled = True

# Specify docker steps as a string.
dockerfile = r'''
FROM mcr.microsoft.com/azureml/intelmpi2018.3-ubuntu16.04

# Install OpenJDK-8
RUN apt-get update && \
    apt-get install -y openjdk-8-jdk && \
    apt-get install -y ant && \
    apt-get clean;

# Fix certificate issues
RUN apt-get update && \
    apt-get install ca-certificates-java && \
    apt-get clean && \
    update-ca-certificates -f;

# Setup JAVA_HOME -- useful for docker commandline
ENV JAVA_HOME /usr/lib/jvm/java-8-openjdk-amd64/
RUN export JAVA_HOME

# Install H2O on python requirements
RUN pip install requests && \
    pip install tabulate && \
    pip install six && \
    pip install future && \
    pip install colorama

# Expose H2O Flow UI port
EXPOSE 54321

# Install H2O
RUN \
    pip uninstall h2o || true && \
    pip install -f http://h2o-release.s3.amazonaws.com/h2o/latest_stable_Py.html --trusted-host h2o-release.s3.amazonaws.com h2o

'''

# Alternatively, load from a file.
#with open("dockerfiles/Dockerfile", "r") as f:
#    dockerfile=f.read()

myenv.docker.base_dockerfile = dockerfile

```

### 4. When deploy model, you need to tell how to score new data with your trained model in "scoring.py" file
**If you want the model to be visible in Power BI, you need to define how input schema is look like.**

Full script can find [here](https://github.com/WipadaChan/pbi_demo_repo/blob/master/03_DeployH2O_PBI/scoring.py)

Back to main script **DeployModel.ipynb**, here is how to tell AzureML to use scoring.py file with your registered model. 

***Note that version of H2O should be the same with your trained model**

```python
from azureml.core.model import InferenceConfig
from azureml.core.environment import Environment
from azureml.core.conda_dependencies import CondaDependencies

# Create the environment

conda_dep = CondaDependencies()

# Define the packages needed by the model and scripts
#conda_dep.add_conda_package("tensorflow")
conda_dep.add_conda_package("numpy")
conda_dep.add_conda_package("pandas")
# You must list azureml-defaults as a pip dependency
conda_dep.add_pip_package("azureml-defaults")
# H2O version should be the same as the one you use when train model 
conda_dep.add_pip_package("h2o==3.32.0.4")
#conda_dep.add_pip_package("gensim")

# Adds dependencies to PythonSection of myenv
myenv.python.conda_dependencies=conda_dep
myenv.inferencing_stack_version='latest'

for pip_package in ["inference_schema"]:
    myenv.python.conda_dependencies.add_pip_package(pip_package)

inference_config = InferenceConfig(entry_script="scoring.py",   
                                   environment=myenv)
```

### 5. Deploy to AzureML using ACI 
```python
from azureml.core.webservice import AciWebservice, Webservice
model = Model(ws, name='CustomerSegment')
deployment_config = AciWebservice.deploy_configuration(cpu_cores = 1, memory_gb = 1)
service = Model.deploy(ws, "customersegment", [model], inference_config, deployment_config)
service.wait_for_deployment(show_output = True)
print(service.state)
print("scoring URI: " + service.scoring_uri)
``` 
Once it succeeded, you will get scoring URI, so you can test to call the service 
![alt text](https://github.com/WipadaChan/pbi_demo_repo/blob/master/03_DeployH2O_PBI/image/URI.png "WebService URI") 


## Using Deployed Model in Power BI Desktop (AI Insight)
Once your model is deployed to AzureML, now you can see your model in Power Query Editor.

### Connect your new data to Power BI Desktop
Connect you data to Power BI the select Transform. It will bring you to Power Query Editor. 
From Power Query Editor, in AI Insight ribbon select Azure Machine Learning.

![alt text](https://github.com/WipadaChan/pbi_demo_repo/blob/master/03_DeployH2O_PBI/image/pbi1.png "Connect data") 

### Select your model from Azure Machine Learning 
Now you will see list of the models deployed on Azure Machine Learning workspaces that you have access permission. 
Select model you desire.
Selected model will automatically match columns with your data (here is where the schema we defined in scoring.py file is used for) 

![alt text](https://github.com/WipadaChan/pbi_demo_repo/blob/master/03_DeployH2O_PBI/image/AzureMLinPBI.png "Connect data") 

After you click OK, it will trigger model and create a new column with predicted result name **AzureML.customersegment**

![alt text](https://github.com/WipadaChan/pbi_demo_repo/blob/master/03_DeployH2O_PBI/image/scoredColumn.png "Connect data") 

**Thank You** 
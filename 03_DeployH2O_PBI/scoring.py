import h2o
import pandas as pd 
import numpy as np 
import os
import json
from inference_schema.schema_decorators import input_schema, output_schema
from inference_schema.parameter_types.standard_py_parameter_type import StandardPythonParameterType
from inference_schema.parameter_types.numpy_parameter_type import NumpyParameterType
from inference_schema.parameter_types.pandas_parameter_type import PandasParameterType




# Called when the deployed service starts
def init():
    global model_path

    # Get the path where the deployed model can be found.
    model_path = os.path.join(os.getenv('AZUREML_MODEL_DIR'))
    # load models
    


input_sample = pd.DataFrame(data=[{
    "CreditScore": 619,
    "Tenure": 2,
    "Balance": 0.00,
    "NumOfProducts": 1,
    "IsActiveMember": 1,
    "EstimatedSalary": 101348.88

}])

# This is an integer type sample. Use the data type that reflects the expected result.
output_sample = np.array([0])

# To indicate that we support a variable length of data input,
# set enforce_shape=False
@input_schema('data', PandasParameterType(input_sample))
@output_schema(NumpyParameterType(output_sample))
def run(data):
    h2o.init()
    try:
        
        model =  h2o.load_model(model_path+'/KMeans_model_python_1619773255297_1')
        print("input_data....")
        print(data.columns)
        print(type(data))
        data_h2o =h2o.H2OFrame(data)
        result = model.predict(data_h2o).as_data_frame()['predict']
        print("result.....")
        print(result)
    # You can return any data type, as long as it is JSON serializable.
        return json.dumps(result.tolist()) #np.array(result.tolist()) 
        
    except Exception as e:
        error = str(e)
        return error
    h2o.shutdown()
        


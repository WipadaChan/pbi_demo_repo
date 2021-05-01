import os
import pickle
import json
import numpy as np
import pandas as pd

import sklearn
from inference_schema.schema_decorators import input_schema, output_schema
from inference_schema.parameter_types.standard_py_parameter_type import StandardPythonParameterType
from inference_schema.parameter_types.numpy_parameter_type import NumpyParameterType
from inference_schema.parameter_types.pandas_parameter_type import PandasParameterType


# Called when the deployed service starts
def init():
    global model

    # Get the path where the deployed model can be found.
    model_path = os.path.join(os.getenv('AZUREML_MODEL_DIR'))
    # load models
    with open(model_path + '/finalized_model.pkl', 'rb') as handle:
        model = pickle.load(handle)



input_sample = pd.DataFrame(data=[{
    "alcohol": 13.58,
    "malic_acid": 2.58,
    "ash": 2.69,
    "alcalinity_of_ash": 24.5,
    "magnesium": 105,
    "total_phenols": 1.55,
    "flavanoids": 0.84,
    "nonflavanoid_phenols": 0.39,
    "proanthocyanins": 1.54,
    "color_intensity": 8.66,
    "hue": 0.74 ,
    "od280/od315_of_diluted_wines":1.8,
    "proline":750

}])

# This is an integer type sample. Use the data type that reflects the expected result.
output_sample = np.array([0])

# To indicate that we support a variable length of data input,
# set enforce_shape=False
@input_schema('data', PandasParameterType(input_sample))
@output_schema(NumpyParameterType(output_sample))
def run(data):
    try:
        print("input_data....")
        print(data.columns)
        print(type(data))
        result = model.predict(data)
        print("result.....")
        print(result)
    # You can return any data type, as long as it is JSON serializable.
        return result.tolist()
    except Exception as e:
        error = str(e)
        return error


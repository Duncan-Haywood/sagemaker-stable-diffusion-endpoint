# Usage

## general

- install projects with `pip install poetry; poetry install; poetry run python ./endpoint/file_name.py`

## for endpoint deployment

- see the infastructure folder for instructions on this
- this package has dependencies to have a `model_bucket_name` in the os environment

## for prediction

- needs the infrastructure up and running already
- to use in a python file run `poetry build; {install the built .whl or .tar.gz in dist with either poetry or pip};` then in the python file use ```# python
from endpoint import predict
predictor = predict.Predictor()
response = predictor.predict(args, kwargs) # see the file for documentation on available args and response type
```  
- a dependency is that there must be a parameter in aws ssm parameter store with the name `endpoint_name/production` or `endpoint_name/test` depending on the environment and the environment variable `production` must be set to `False` if it is supposed to use `"test"` infrastructure

# development notes

- still lots of unimplemented unit testing that could be added. that's mostly why the tests are failing from as much as I know. Right now, it's relying on a single integration test to hold it all together.


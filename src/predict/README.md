# for prediction

- needs the infrastructure up and running already
- to use in a python file run `poetry build; {install the built .whl or .tar.gz in dist with either poetry or pip};` then in the python file use 

```# python
from endpoint import predict
predictor = predict.Predictor()
response = predictor.predict(args, kwargs) # see the file for documentation on available args and response type
```

- a dependency is that there must be a parameter in aws ssm parameter store with the name `endpoint_name/production` or `endpoint_name/test` depending on the environment and the environment variable `production` must be set to `False` if it is supposed to use `"test"` infrastructure
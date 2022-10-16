FROM public.ecr.aws/lambda/python:3.8 as base
# requirements
RUN pip install poetry 
COPY pyproject.toml poetry.lock ./
RUN poetry export --output ./requirements.txt \
    && pip install -r ./requirements.txt --target ${LAMBDA_TASK_ROOT}
# application code
COPY ./model_upload/model_from_hub_to_s3.py ${LAMBDA_TASK_ROOT}
# Set the CMD to your handler (could also be done as a parameter override outside of the Dockerfile)
CMD [ "model_from_hub_to_s3.lambda_handler" ]

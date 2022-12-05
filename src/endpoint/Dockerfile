FROM python:3.9-bullseye
RUN pip install poetry
COPY pyproject.toml poetry.lock /
RUN poetry install
COPY endpoint /
COPY tests /
ENTRYPOINT "poetry run python".split()
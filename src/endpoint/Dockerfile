FROM python:3.9-bullseye
RUN pip install poetry
COPY pyproject.toml poetry.lock /
RUN poetry install

ENTRYPOINT ["poetry","run"]
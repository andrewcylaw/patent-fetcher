FROM python:3.13-slim

# References https://medium.com/@albertazzir/blazing-fast-python-docker-builds-with-poetry-a78a66f5aed0
ENV POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=1 \
    POETRY_VIRTUALENVS_CREATE=1 \
    POETRY_CACHE_DIR=/tmp/poetry_cache

RUN pip install poetry==2.1.3
COPY . .
RUN poetry install --without test && rm -rf $POETRY_CACHE_DIR


# Use this ENTRYPOINT to allow running
#  docker run patent_fetcher 2001-04-25 2001-05-25
ENTRYPOINT ["poetry", "run", "patent_fetcher"]

# Use this ENTRYPOINT for the cli with more options
# ENTRYPOINT ["poetry", "run", "patent_fetcher_cli"]

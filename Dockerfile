FROM python:3.9-slim-buster

RUN pip install --upgrade pip pipenv > /dev/null

WORKDIR /app

ADD Pipfile* /app/
RUN pipenv install --system --deploy --ignore-pipfile > /dev/null

ADD . /app

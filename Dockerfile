FROM python:3.13.13-alpine

ENV PATH="${PATH}:/root/.local/bin"
ENV PYTHONPATH /app/src

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY ./migrations /app/migrations
COPY ./src /app/src
COPY alembic.ini /app/
COPY cli.py /app/

RUN chmod +x /app/cli.py
RUN chmod +x ./src/start.sh

EXPOSE 8000

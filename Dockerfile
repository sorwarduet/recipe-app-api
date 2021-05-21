FROM python:3.9.5-alpine

MAINTAINER Md. Sorwar Alam

ENV PYHONUNBUFFERED 1
COPY ./requirements.txt /requirements.txt
RUN pip install -r requirements.txt

RUN mkdir /app
WORKDIR /app
COPY ./app /app

RUN adduser -D user
USER user

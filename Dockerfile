FROM registry.opensource.zalan.do/stups/python:3.6.5-22

RUN mkdir /api
COPY . /api

WORKDIR /api

RUN pip install -r requirements.txt
RUN pip install -r requirements.dev.txt

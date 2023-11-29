FROM python:3.8
LABEL Aidan McCoy "acsm3002@gmail.com"
RUN apt-get update -y
COPY . /app
WORKDIR /app
RUN pip install -r requirements.txt

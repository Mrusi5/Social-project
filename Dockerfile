FROM python:3.10.6

WORKDIR /app

COPY requirements.txt .

RUN pip install -r requirements.txt && \
    apt-get update 

COPY . .

RUN chmod a+x docker/*.sh
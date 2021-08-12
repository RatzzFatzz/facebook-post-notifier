FROM python:3.9-slim-buster
WORKDIR /src
COPY requirements.txt .
RUN pip3 install -r requirements.txt
COPY ./src /src
CMD python /src/facebook_notifier.py
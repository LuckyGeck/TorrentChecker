FROM python:3.6.2

RUN mkdir -p /usr/src
WORKDIR /usr/src

COPY requirements.txt /usr/src/
RUN pip install --no-cache-dir -r requirements.txt

COPY . /usr/src

VOLUME /shows /movies /config /logs

CMD [ "python", "./run.py" ]

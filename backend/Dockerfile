FROM python:3.10.8-alpine3.16

RUN adduser -D nsu

WORKDIR /home/nsu

COPY requirements.txt requirements.txt
RUN python -m venv venv
RUN venv/bin/pip install -r requirements.txt
COPY . .
RUN chmod +x boot.sh

ENV FLASK_APP nsu.py

RUN chown -R nsu:nsu ./
USER nsu

EXPOSE 5000
ENTRYPOINT ["./boot.sh"]
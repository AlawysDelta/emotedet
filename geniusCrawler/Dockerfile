FROM python:3.8-alpine

WORKDIR /opt/crawler
RUN pip3 install lyricsgenius spotipy
COPY crawler.py .
COPY worker.py .
ENTRYPOINT [ "python3", "worker.py" ]
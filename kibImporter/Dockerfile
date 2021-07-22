FROM alpine:latest
RUN apk add curl
WORKDIR /opt
ADD import.sh .
ADD imports/docker.ndjson .
ADD imports/emotedet.ndjson .
ADD imports/kafka.ndjson .
ENTRYPOINT ./import.sh
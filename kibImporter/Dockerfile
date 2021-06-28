FROM alpine:latest
RUN apk add curl
WORKDIR /opt
ADD import.sh .
COPY imports/* .
ENTRYPOINT ./import.sh
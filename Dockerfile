FROM alpine:latest

MAINTAINER Zoltán Farkas

RUN apk update
RUN apk upgrade
RUN apk add zip coreutils dcron py2-pip bash
RUN pip install --upgrade pip
RUN pip install Flask wget PyYAML requests
ADD devel/* /usr/bin/
RUN chmod u+x /usr/bin/flowbster-run.sh

EXPOSE 5000 5001

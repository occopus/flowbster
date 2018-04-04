FROM ubuntu:latest

MAINTAINER Zoltán Farkas

RUN apt-get update
RUN apt-get -y upgrade
RUN apt-get install -y python python-pip zip coreutils cron
RUN pip install --upgrade pip
RUN pip install Flask wget PyYAML requests
ADD devel/* /usr/bin/
RUN chmod u+x /usr/bin/flowbster-run.sh

EXPOSE 5000 5001

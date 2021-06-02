FROM python:3.7-slim
# OS stuff
RUN apt-get update 
RUN apt-get install dialog apt-utils -y -q
RUN apt-get install -y -q less vim cron wget 
RUN apt-get install -y -q default-libmysqlclient-dev
RUN apt-get install -y -q build-essential libssl-dev libffi-dev libpcre3-dev pkg-config
RUN apt-get install -y -q libpq-dev libxml2-dev libxmlsec1-dev libxmlsec1-openssl
RUN apt-get install -y python3-pip
# Python stuff
RUN /usr/local/bin/python -m pip install --upgrade pip
RUN /usr/local/bin/python -m pip install ipdb

# Root user environment stuff
COPY .docker/bashrc /root/.bashrc
COPY .docker/bash_aliases /root/.bash_aliases

# Application stuff
RUN mkdir /app
WORKDIR /app
COPY requirements.txt ./
RUN pip install -r requirements.txt
EXPOSE 8000

# Django cron
COPY .docker/crontab /root/crontab
CMD ["./.docker/start_cron.sh"]

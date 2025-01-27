FROM python:3.8

WORKDIR /

RUN apt update && apt install -y build-essential \
                      libmemcached-dev \
                      libssl-dev \
                      libevent-dev \
                      libffi-dev \
                      xvfb \
                      libxi6 \
                      libgconf-2-4 \
                      libgdal-dev \
                      python3-venv \
                      gcc \
                      curl \
                      nano \
                      net-tools \
                      htop \
                      nmap \
                      screen

COPY requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt && rm requirements.txt
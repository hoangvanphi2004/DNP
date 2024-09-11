FROM nvidia/cuda:11.2.2-devel-ubuntu20.04

RUN apt-get update
RUN apt-get install python3 -y
RUN apt-get install python3-pip -y
RUN apt-get install tmux -y
RUN apt install libgl1-mesa-glx -y
RUN apt-get install --no-install-recommends -y libglib2.0-0

WORKDIR /

COPY requirements.txt /

RUN pip install mmengine
RUN pip install boxmot
RUN pip install chardet
RUN apt-get install --no-install-recommends -y git 
RUN git clone https://github.com/edenhill/librdkafka.git && cd librdkafka \
    && git checkout tags/v2.5.3 && ./configure --clean \
    && ./configure --prefix /usr/local \
    && make && make install
RUN pip install confluent-kafka
RUN pip install ultralytics

RUN pip install configparser
RUN pip install torchvision
RUN apt install nano
RUN apt-get install coreutils
RUN apt-get install -y netcat

COPY . .

FROM nvidia/cuda:11.2.2-devel-ubuntu20.04

RUN apt-get update
RUN apt-get install python3 -y
RUN apt-get install python3-pip -y
RUN apt-get install tmux -y
RUN apt install libgl1-mesa-glx -y
RUN apt-get install --no-install-recommends -y libglib2.0-0

WORKDIR /

COPY requirements.txt /

#Conda download
# RUN ~/miniconda3/bin/conda init bash

# RUN ~/miniconda3/bin/conda init zsh

RUN pip install mmengine
RUN pip install boxmot
RUN pip install chardet 
RUN pip install confluent-kafka
RUN pip install ultralytics

COPY . .

RUN pip install configparser

CMD [ "./run.sh" ]

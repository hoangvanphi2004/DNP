# DNP Project
## 1. Introduce
The purpose of this project is to build a system to detect people pose in a video.
## 2. How to use
1. First you need to download docker and run docker, install miniconda and install cuda
2. Clone this repo
3. Now, install Kafka:
```bash
pip install confluent-kafka
```
4. After that, create conda environment, install MMEngine, MMCV, MMPOSE using MIM, BoxMOT and install ultralytics:
```bash
conda create --name DNP python=3.8 -y
pip install -U openmim
mim install mmengine
mim install "mmcv>=2.0.1"
mim install "mmdet>=3.1.0"
mim install "mmpose>=1.1.0"
conda install -c conda-forge ultralytics
pip install boxmot
```
5. Download the config file:
```bash
mim download mmpose --config td-hm_hrnet-w48_8xb32-210e_coco-256x192  --dest .
```
6. Run each block in different commandline windows:
```bash
conda activate DNP
docker-compose up
```
```bash
python createKafkaTopic.py
python sendVideo.py
```
```bash
conda activate DNP
python predictBoundingBox.py
```
```bash
conda activate DNP
python predictPose.py
```

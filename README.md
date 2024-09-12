<div align="center">

  # DNP Project
  
</div>

## 1. Introduce
This project was created during the time i was learning in IAI lab. This project is about a system detect body keypoints, position of staffs and students in a classroom.
## 2. Technology
This is some model i use in this project:
+ YOLOv8 for detect person in class
+ OCSORT for tracking people in class
+ rtmpose for detect body keypoints
Beside, i also use some platform to delivery the system to user easier. I use:
+ Docker for create light container, make it easier to deploy
+ Kafka for process management 
## 3. How to use
### 3.1 Extract video information
1. First you need to have docker installed in your computer, you can download it <a href="https://www.docker.com/products/docker-desktop/">here</a>
2. Pull <a href="https://hub.docker.com/repository/docker/philosophi1/dnp/general">this</a> docker image to your computer 
3. Clone this repo to the folder you want.
4. Create folder name "ckpt" in the repo folder. After that:
   + Download <a href="https://download.openmmlab.com/mmpose/v1/projects/rtmw/rtmw-dw-x-l_simcc-cocktail14_270e-256x192-20231122.pth">this </a> model and move it to "ckpt" folder. This is the model to detect body keypoints
   + Download <a href="https://github.com/ultralytics/assets/releases/download/v8.2.0/yolov8l.pt">this</a> model and move it to "ckpt" folder. This is the model to detect person. 
5. Create "input" folder in the repo folder. Move the video you want to detect into this folder.
6. After that, run this command:
 ```bash
 docker compose up
 ```
7. Wait until the process is done!
The video information would be saved in output folder as a json file.
After the process is done. Remember to run the command
```bash
docker compose down
```
To shutdown the system

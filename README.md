<div align="center">

  # DNP Project
  
</div>

## 1. Introduce
This project was created during the time i was learning in IAI lab. This project is about a system which detect body keypoints, position of staffs and students in a classroom.
## 2. Technology
These are some models i use in this project:
+ YOLOv8 for detecting person in class
+ OCSORT for tracking people in class
+ rtmpose for detecting body keypoints

Beside, i also use some platforms to deliver the system to user easier. I use:
+ Docker for creating light container, make it easier to deploy
+ Kafka for process management 
## 3. How to use
### 3.1 Extract video information
1. First you need to have docker installed in your computer, you can download it <a href="https://www.docker.com/products/docker-desktop/">here</a>
2. Pull <a href="https://hub.docker.com/repository/docker/philosophi1/dnp/general">this</a> docker image to your computer 
3. Clone this repo to the folder you want.
4. Create folder name "ckpt" in the repo folder. After that:
   + Download <a href="https://download.openmmlab.com/mmpose/v1/projects/rtmw/rtmw-dw-x-l_simcc-cocktail14_270e-256x192-20231122.pth">this</a> model and move it to "ckpt" folder. This is the model to detect body keypoints
   + Download <a href="https://github.com/ultralytics/assets/releases/download/v8.2.0/yolov8l.pt">this</a> model and move it to "ckpt" folder. This is the model to detect person. 
5. Create "input" folder in the repo folder. Move the video you want to detect into this folder.
6. After that, run this command in commandline:
 ```bash
 docker compose up
 ```
7. Wait until the process is done!

The video information would be saved in output folder as an json file. The structure of the file look like the code below, for more information, please checkout in <a href="https://github.com/hoangvanphi2004/DNP/blob/main/writeToJSON.py">writeToJSON.py</a> file.

```python
{
    "frame_id": [frame id],
    "img_w": [width of frame],
    "img_h": [height of frame],
    "approach": {
        [bounding box id]: {
            "tl_coord2d": [top left point],
            "br_coord2d": [bottom right point]
        } 
    },
    "action": {
        //This part is for my future work
    },
    "pose": {
        "persons": {
            [person id]: {
                [point id]: [keypoint]
            }
        },
        "is_staff":{
            [person id]: [1 if the person is staff 0 otherwise]
        },
        "Datetime": [the time frame is captured]
    }
}
```

After the process is done, remember to run this command to turn off the system:

```bash
docker compose down
```

### 3.2 Visualize video information
To do this you must have opencv and numpy installed in your computer. To do this, run these commands:
```bash
pip install opencv-python
pip install numpy
```
After that you can follow the following lines to visualize the keypoints:

1. Go to the output folder, create folder name "visualize".
2. Run this command in commandline:
```bash
python3 visualize.py [json_file_you_want_to_visualize] [background_image_path]
```
This will visualize your json file (video information file) on the background image. If you just want a black background, you can leave it blank.
## 4. Credit and Contact
Thanks to Du Pham for helping me in the project.

If you find any issues about my project or want to contribute, please contact me:
+ Email: hoangvanphi2004@gmail.com
+ Facebook: fb.com/hoangvanphi2004
<div align="center">

  # Thanks for visiting my project
  
</div>

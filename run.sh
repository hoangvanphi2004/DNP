#!/bin/bash

# declare -a windows = (
#     [0] = docker
#     [1] = sendVideo
#     [2] = predictBoundingBox
#     [3] = predictPose
#     [4] = receiveVideo 
# )

tmux new-session -d -s ss
for i in {1..5}
do  
    tmux new-window -t ss:$i
    # tmux send-keys -t ss:$i 'conda activate DNP' C-m
    case $i in
        1)
            # tmux send-keys -t ss:1 'docker-compose up' C-m
            sleep 10
            ;;
        2)
            tmux send-keys -t ss:2 'python3 deleteKafkaTopic.py' C-m
            tmux send-keys -t ss:2 'python3 createKafkaTopic.py' C-m
            tmux send-keys -t ss:2 'python3 sendVideo.py' C-m
            ;;
        3)  
            python3 predictBoundingBox.py
            # tmux send-keys -t ss:3 'python3 predictBoundingBox.py' C-m
            ;;
        4)
            tmux send-keys -t ss:4 'python3 predictPose.py' C-m
            ;;
        5)
            tmux send-keys -t ss:5 'python3 receiveVideo.py' C-m
            ;;
    esac  
done


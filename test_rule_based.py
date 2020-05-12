"""
The template of the script for the machine learning process in game pingpong
"""

# Import the necessary modules and classes
from mlgame.communication import ml as comm
import os
import pickle
import numpy as np
import random

def calculate(direct_x, direct_y, cur_ball_x, cur_ball_y, side):
    # change pivot to center
    cur_ball_x += 2
    cur_ball_y += 2

    if side == "1P":
        cross = 415
    else:
        cross = 80
    
    m = direct_y/(direct_x if direct_x != 0 else 1)
    # (y - y0) = m(x - x0)
    # (x - x0) = (y - y0)/m
    # x        = (y - y0)/m + x0
    candidate = (cross - cur_ball_y)/(m if m!= 0 else 1) + cur_ball_x -2
    if candidate >= 0 and candidate <= 200:
        return candidate
    elif candidate > 200:
        if int((candidate/200)) % 2 == 1:
            return 200 - candidate % 200
        else:
            return candidate % 200
    else:
        candidate = abs(candidate)
        if int((candidate/200)) % 2 == 0:
            return candidate % 200
        else:
            return 200 - candidate % 200

def ml_loop(side: str):
    # === Here is the execution order of the loop === #
    # 1. Put the initialization code here
    ball_served = 0
    match = 100
    ini_move = random.randint(-16,16)
    serv_dir = random.choice(["l","r"])
    prev_ball_dire = 1
    savepoint = 1
    feature = []
    features = np.array([0,0,0,0,0,0])

    # 2. Inform the game process that ml process is ready
    comm.ml_ready()

    # 3. Start an endless loop
    while True:
        # 3.1. Receive the scene information sent from the game process
        scene_info = comm.recv_from_game()

        feature = [scene_info["ball"][0],
                        scene_info["ball"][1],
                        scene_info["ball_speed"][0],
                        scene_info["ball_speed"][1],
                        scene_info["blocker"][0],
                        0]
        feature = np.array(feature).reshape((-1,6))
        features = np.vstack((features,feature))

        if((prev_ball_dire!=0) and (scene_info["ball_speed"][1]/prev_ball_dire < 0) and (scene_info["ball"][1] > 412) and (side=="1P")):
            prev_frame = scene_info["frame"]
            frame = features[prev_frame]
            point = calculate(frame[2],frame[3],frame[0],frame[1],"1P")
            for i in range(savepoint, prev_frame):
                features[i][5] = point
            #print("bounced with 1p, updating %d to %d"%(savepoint,scene_info["frame"]))
            savepoint = scene_info["frame"] + 1
        elif((prev_ball_dire!=0) and (scene_info["ball_speed"][1]/prev_ball_dire < 0) and (scene_info["ball"][1] < 83) and (side=="1P")):
            prev_frame = scene_info["frame"]
            frame = features[prev_frame]
            point = calculate(frame[2],frame[3],frame[0],frame[1],"2P")
            for i in range(savepoint, prev_frame):
                features[i][5] = point
            #print("bounced with 2p, updating %d to %d"%(savepoint,scene_info["frame"]))
            savepoint = scene_info["frame"] + 1

        # 3.2. If either of two sides wins the game, do the updating or
        #      resetting stuff and inform the game process when the ml process
        #      is ready.
        if scene_info["frame"] == 5999 and side == "1P":
            destiFile = os.path.join(os.path.dirname(__file__), "test_log", "test%d.pickle"%match)
            match += 1
            #print(features.shape)
            with open(destiFile,"wb") as rf:
                pickle.dump(features[1:],rf)
            with open(destiFile,"rb") as rf:
                check = pickle.load(rf)
                print("Data now has %d elements."%len(check))
            

        if scene_info["status"] != "GAME_ALIVE":
            # Do some updating or resetting stuff
            features = np.array([0,0,0,0,0,0])
            ball_served = 0
            ini_move = random.randint(-16,16)
            serv_dir = random.choice(["l","r"])

            # 3.2.1 Inform the game process that
            #       the ml process is ready for the next round
            comm.ml_ready()
            continue

            

        # 3.3 Put the code here to handle the scene information
        dire = random.randint(0,2)

        # 3.4 Send the instruction for this frame to the game process
        if ball_served == 0:
            if(ini_move<0):
                comm.send_to_game({"frame": scene_info["frame"], "command": "MOVE_LEFT"})
                ini_move += 1
            elif(ini_move>0):
                comm.send_to_game({"frame": scene_info["frame"], "command": "MOVE_RIGHT"})
                ini_move -= 1
            else:
                if(serv_dir == "l"):
                    comm.send_to_game({"frame": scene_info["frame"], "command": "SERVE_TO_LEFT"})
                else:
                    comm.send_to_game({"frame": scene_info["frame"], "command": "SERVE_TO_RIGHT"})
                ball_served = 1
        
        elif ball_served == 1:
            plt = (scene_info["platform_1P"][0] if (side == "1P") else scene_info["platform_2P"][0])
            
            if plt > 0 : 
                comm.send_to_game({"frame": scene_info["frame"], "command": "MOVE_LEFT"})
            else:
                savepoint = scene_info["frame"]
                ball_served = 2
            
        else:
            if dire == 1:
                comm.send_to_game({"frame": scene_info["frame"], "command": "MOVE_RIGHT"})
            elif dire == 2:
                comm.send_to_game({"frame": scene_info["frame"], "command": "MOVE_LEFT"})
            else:
                comm.send_to_game({"frame": scene_info["frame"], "command": "NONE"})

        prev_ball_dire = scene_info["ball_speed"][1]

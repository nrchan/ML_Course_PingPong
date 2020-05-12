# Import the necessary modules and classes
from mlgame.communication import ml as comm
import os
import pickle
import numpy as np
import random

def direction(esti, curPos):
        if curPos + 20  < esti - 1: return 1 #right
        elif curPos + 20 > esti + 1: return 2 #left
        else: return 0

def ml_loop(side: str):
    # === Here is the execution order of the loop === #
    # 1. Put the initialization code here
    ball_served = False
    """
    ini_move = random.randrange(-16,16)
    serv_dir = random.choice(["l","r"])
    """
    with open(os.path.join(os.path.dirname(__file__), 'save', 'model_test'), 'rb') as f:
        model = pickle.load(f)

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
                        scene_info["blocker"][0]]
        feature = np.array(feature).reshape((-1,5))

        plt = 0
        if side == "1P":
            plt = scene_info["platform_1P"][0]
        else:
            plt = scene_info["platform_2P"][0]

        # 3.2. If either of two sides wins the game, do the updating or
        #      resetting stuff and inform the game process when the ml process
        #      is ready.
        if scene_info["status"] != "GAME_ALIVE":
            # Do some updating or resetting stuff
            ball_served = False
            """
            ini_move = random.randint(-16,16)
            serv_dir = random.choice(["l","r"])
            """
            # 3.2.1 Inform the game process that
            #       the ml process is ready for the next round
            comm.ml_ready()
            continue

        # 3.3 Put the code here to handle the scene information
        esti = model.predict(feature)
        dire = direction(esti, plt)

        # 3.4 Send the instruction for this frame to the game process
        if not ball_served:
            """
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
                ball_served = True
            """
            comm.send_to_game({"frame": scene_info["frame"], "command": "SERVE_TO_LEFT"})
            ball_served = True
            
        else:
            if dire == 1:
                comm.send_to_game({"frame": scene_info["frame"], "command": "MOVE_RIGHT"})
            elif dire == 2:
                comm.send_to_game({"frame": scene_info["frame"], "command": "MOVE_LEFT"})
            else:
                comm.send_to_game({"frame": scene_info["frame"], "command": "NONE"})

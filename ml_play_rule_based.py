"""
The template of the script for the machine learning process in game pingpong
"""

# Import the necessary modules and classes
import games.pingpong.communication as comm
from games.pingpong.communication import (
    SceneInfo, GameStatus, PlatformAction
)

def ml_loop(side: str):
    """
    The main loop for the machine learning process

    The `side` parameter can be used for switch the code for either of both sides,
    so you can write the code for both sides in the same script. Such as:
    ```python
    if side == "1P":
        ml_loop_for_1P()
    else:
        ml_loop_for_2P()
    ```

    @param side The side which this script is executed for. Either "1P" or "2P".
    """

    # === Here is the execution order of the loop === #
    # 1. Put the initialization code here
    ball_served = False
    prev_ball_coor = (0,0)

    # 2. Inform the game process that ml process is ready
    comm.ml_ready()

    # 3. Start an endless loop
    while True:
        # 3.1. Receive the scene information sent from the game process
        scene_info = comm.get_scene_info()

        # 3.2. If either of two sides wins the game, do the updating or
        #      resetting stuff and inform the game process when the ml process
        #      is ready.
        if scene_info.status != GameStatus.GAME_ALIVE:
            # Do some updating or resetting stuff
            ball_served = False
            prev_ball_coor = (0,0)
            # 3.2.1 Inform the game process that
            #       the ml process is ready for the next round
            comm.ml_ready()
            continue

        # 3.3 Put the code here to handle the scene information
        esti_ball_x = calculate(prev_ball_coor[0], prev_ball_coor[1], scene_info.ball[0], scene_info.ball[1], side)
        if side == "1P":
            platform = scene_info.platform_1P[0]
        else:
            platform = scene_info.platform_2P[0]


        # 3.4 Send the instruction for this frame to the game process
        if not ball_served:
            comm.send_instruction(scene_info.frame, PlatformAction.SERVE_TO_LEFT)
            ball_served = True
        else:
            if (esti_ball_x - (platform+20)) >= 0:
                #print("Estimate: ",esti_ball_x,", Current: ",scene_info.platform[0],", Moving right")
                comm.send_instruction(scene_info.frame, PlatformAction.MOVE_RIGHT)
            elif (esti_ball_x - (platform+20)) < 0:
                comm.send_instruction(scene_info.frame, PlatformAction.MOVE_LEFT)
                #print("Estimate: ",esti_ball_x,", Current: ",scene_info.platform[0],", Moving left")
            else:
                comm.send_instruction(scene_info.frame, PlatformAction.NONE)
                #print("Estimate: ",esti_ball_x,", Current: ",scene_info.platform[0],", Staying")
        
        prev_ball_coor = (scene_info.ball[0], scene_info.ball[1])

def calculate(prev_ball_x, prev_ball_y, cur_ball_x, cur_ball_y, side):
    # change pivot to center
    prev_ball_x += 2
    prev_ball_y += 2
    cur_ball_x += 2
    cur_ball_y += 2

    if side == "1P":
        cross = 420
    else:
        cross = 80
    
    try:
        m = (cur_ball_y - prev_ball_y)/(cur_ball_x - prev_ball_x)
    except ZeroDivisionError:
        m = (cur_ball_y - prev_ball_y)/(cur_ball_x - prev_ball_x + 1)
    # (y - y0) = m(x - x0)
    # (x - x0) = (y - y0)/m
    # x        = (y - y0)/m + x0
    candidate = (cross - cur_ball_y)/(m if m != 0 else 1) + cur_ball_x -2
    #print("Raw estimate: ",candidate,"(x=",cur_ball_x,"m=",m,".)", end = " ")
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
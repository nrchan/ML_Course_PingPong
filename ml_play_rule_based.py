"""
The template of the script for the machine learning process in game pingpong
"""

# Import the necessary modules and classes
from mlgame.communication import ml as comm

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

    def direction(esti, curPos):
        if curPos + 20  < esti: return 1
        elif curPos + 20 > esti: return 2
        else: return 0

    # 2. Inform the game process that ml process is ready
    comm.ml_ready()

    # 3. Start an endless loop
    while True:
        # 3.1. Receive the scene information sent from the game process
        scene_info = comm.recv_from_game()

        # 3.2. If either of two sides wins the game, do the updating or
        #      resetting stuff and inform the game process when the ml process
        #      is ready.
        if scene_info["status"] != "GAME_ALIVE":
            # Do some updating or resetting stuff
            ball_served = False
            prev_ball_coor = (0,0)
            # 3.2.1 Inform the game process that
            #       the ml process is ready for the next round
            comm.ml_ready()
            continue

        # 3.3 Put the code here to handle the scene information
        esti_ball_x = calculate(prev_ball_coor[0], prev_ball_coor[1], scene_info["ball"][0], scene_info["ball"][1], side)
        if side == "1P":
            platform = scene_info["platform_1P"][0]
        else:
            platform = scene_info["platform_2P"][0]


        # 3.4 Send the instruction for this frame to the game process
        if not ball_served:
            comm.send_to_game({"frame": scene_info["frame"], "command": "SERVE_TO_LEFT"})
            ball_served = True
        else:
            command = direction(esti_ball_x, platform)
            if command == 0:
                comm.send_to_game({"frame": scene_info["frame"], "command": "NONE"})
            elif command == 1:
                comm.send_to_game({"frame": scene_info["frame"], "command": "MOVE_RIGHT"})
            else:
                comm.send_to_game({"frame": scene_info["frame"], "command": "MOVE_LEFT"})
        
        prev_ball_coor = (scene_info["ball"][0], scene_info["ball"][1])

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
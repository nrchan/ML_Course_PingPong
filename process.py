import pickle
from os import path

def calculate(direct_x, direct_y, cur_ball_x, cur_ball_y, side):
    cur_ball_x += 2
    cur_ball_y += 2

    if side == "1P":
        cross = 420
    else:
        cross = 80
    
    m = direct_y/(direct_x if direct_x != 0 else 1)
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

def updataData(log):
    destiFile = path.join(path.dirname(__file__), "data.pickle")
    megadata = []
    if path.exists(destiFile):
        with open(destiFile,"rb") as rf:
            megadata = pickle.load(rf)

    megadata.extend(log)

    with open(destiFile,"wb") as wf:
        pickle.dump(megadata, wf)

    with open(destiFile,"rb") as rf:
        check = pickle.load(rf)
        print("Data now has %d elements."%len(check))


if __name__ == '__main__':
    filename = path.join(path.dirname(__file__), 'log', '37.pickle')
    log = pickle.load((open(filename, 'rb')))
    for i in log:
        i["esti_1P"] = calculate(i["ball_speed"][0], i["ball_speed"][1], i["ball"][0], i["ball"][1], "1P")
        i["esti_2P"] = calculate(i["ball_speed"][0], i["ball_speed"][1], i["ball"][0], i["ball"][1], "2P")
        #use to print out unprocessed data
        #print(i)

    #change to correct estimation, please change all numbers here for each case
    #for i in range(1535,1556): log[i]["esti_2P"] = 43.0


    #!!!This will change data.pickle, be sure to comment out if not in use!!!
    #updataData(log)
from handGesture import hand
import cv2
import math
import json
import sys
from websockets import serve
import asyncio

# ----------------------------------------------------------------
# car gesture arch
# ----------------------------------------------------------------

# find the actual percentage for the inbetween values


def findPercents(inp, mi, ma, v):
    va = (inp - mi) * 100 / (ma - mi)
    if v == 100:
        va = v - va
    if va > 100:
        return 100
    elif va < 0:
        return 0
    else:
        return int(va)


cam = cv2.VideoCapture(0)
Wcam = 640
Hcam = 480
cam.set(3, Wcam)
cam.set(4, Hcam)

hands = hand.Hand(max_hands=2)


try:
    while 1:
        success, img = cam.read()
        res = hand.DetectHands(img, hands, False)
        if not res['status']:
            break
        img = res["image"]
        left = res["data"]["left"]
        right = res["data"]["right"]
        enddata = {}
        if right:
            # circle shape x and y axis point
            x0, x1 = right[1][0], right[8][0]
            y0, y1 = right[1][1], right[8][1]
            cv2.circle(img, (x0, y0), 8, (0, 255, 0), cv2.FILLED)
            cv2.circle(img, (x1, y1), 8, (0, 255, 0), cv2.FILLED)
            cv2.line(img, (x0, y0), (x1, y1), (255, 255, 255), 2)
            if y1 < y0:
                enddata["acdirection"] = "forward"
            else:
                enddata["acdirection"] = "backward"
            # print("[x]:", x0, ":", x1)
            # print("[y]:", y0, ":", y1)

            angle = abs(math.atan2(y1 - y0, x1 - x0) * 180 / math.pi)

            if angle < 75:
                enddata["rospeed"] = findPercents(angle, 0, 75, 100)
                enddata["rodirection"] = "right"
            elif angle > 105:
                enddata["rospeed"] = findPercents(angle, 105, 180, 0)
                enddata["rodirection"] = "left"

            enddata["acspeed"] = findPercents(
                math.hypot(x0-x1, y0-y1), 40, 120, 0)

            # # data for the car
            # enddata["acspeed"] = findPercents(math.hypot(
            #     right[4][0]-right[8][0], right[4][1]-right[8][1]), 20, 100, 0)
            # if enddata["acspeed"] > 0:
            #     if right[12][1] < right[11][1]:
            #         enddata["acdirection"] = "backward"
            #         # lines for the eache shape in rgb
            #         cv2.line(img, (right[4][0], right[4][1]),
            #                  (right[8][0], right[8][1]), (0, 0, 0), 2)
            #     else:
            #         enddata["acdirection"] = "forward"
            #         # lines for the eache shape in rgb
            #         cv2.line(img, (right[4][0], right[4][1]),
            #                  (right[8][0], right[8][1]), (255, 255, 255), 2)
            # else:
            #     enddata["acdirection"] = "neutral"
        print(enddata)
        d = json.dumps(enddata)
        cv2.imshow("Images", img)
        cv2.waitKey(1)
except KeyboardInterrupt:
    cam.release()
    cv2.destroyAllWindows()
# after break happens
cam.release()
cv2.destroyAllWindows()

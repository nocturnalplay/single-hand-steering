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
            # x and y co-ordinates
            x0, x1 = right[0][0], right[12][0]
            y0, y1 = right[0][1], right[12][1]

            # circle shape x and y axis point
            cv2.circle(img, (x0, y0), 8, (0, 255, 0), cv2.FILLED)
            cv2.circle(img, (x1, y1), 8, (0, 255, 0), cv2.FILLED)

            # line between the two points
            cv2.line(img, (x0, y0), (x1, y1), (255, 255, 255), 2)

            # front or back acceleration speed
            enddata["acspeed"] = findPercents(
                math.hypot(x0-x1, y0-y1), 50, 140, 0)

            # based on the hand shape fix the direct of the car
            if y1 < y0:
                enddata["acdirection"] = "forward"
            else:
                enddata["acdirection"] = "backward"

            if enddata["acspeed"] == 0:
                enddata["acdirection"] = "neutral"

            # find the angle of the hand to move the car left or right
            angle = abs(math.atan2(y1 - y0, x1 - x0) * 180 / math.pi)
            print(angle)
            if angle < 80:
                enddata["rospeed"] = findPercents(angle, 40, 80, 100)
                enddata["rodirection"] = "right"
            elif angle > 100:
                enddata["rospeed"] = findPercents(angle, 100, 150, 0)
                enddata["rodirection"] = "left"
            else:
                enddata["rodirection"] = "neutral"
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

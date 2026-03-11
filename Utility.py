import cv2
import numpy as np
import pyautogui
import time
import tensorflow as tf
import matplotlib.pyplot as plt

def initializePrediction():
    model = tf.keras.models.load_model('sudoku_digit_cnn_rev3.keras')
    return model

def preProcess(img):
    imggray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    imgblur = cv2.GaussianBlur(imggray, (5, 5), 1)
    imgthreshold = cv2.adaptiveThreshold(imgblur,255, 1, 1, 11, 2)
    return imgthreshold

def stackedImage(imgArray, scale):
    rows = len(imgArray)
    cols = len(imgArray[0])
    rowsAvailable = isinstance(imgArray[0], list)
    width = imgArray[0][0].shape[1]
    height = imgArray[0][0].shape[0]
    if rowsAvailable:
        for x in range(0, rows):
            for y in range(0, cols):
                imgArray[x][y] = cv2.resize(imgArray[x][y], (0, 0), None, scale, scale)
                if len(imgArray[x][y].shape) == 2: imgArray[x][y]=cv2.cvtColor(imgArray[x][y], cv2.COLOR_GRAY2BGR)
        imageBlank = np.zeros((height, width, 3), np.uint8)
        hor = [imageBlank]*rows
        hor_con = [imageBlank] * rows
        for x in range(0, rows):
            hor[x] = np.hstack(imgArray[x])
            hor_con[x] = np.concatenate(imgArray[x])
        ver = np.vstack(hor)
        ver_con = np.concatenate(hor)

    else:
        for x in range(0, rows):
            imgArray[x] = cv2.resize(imgArray[x], (0, 0), None, scale, scale)
            if len(imgArray[x].shape) == 2: imgArray[x] = cv2.cvtColor(imgArray[x], cv2.COLOR_GRAY2BGR)
        hor = np.hstack(imgArray[x])
        hor_con = np.concatenate(imgArray[x])
        ver = hor

    return ver

def biggestContours(contours):
    biggest = np.array([])
    max_area = 0
    for i in contours:
        area = cv2.contourArea(i)
        if area > 50:
            peri = cv2.arcLength(i,True) #返回周長值
            approx = cv2.approxPolyDP(i,0.02*peri,True) #返回四個頂點座標, 求近似輪廓並減少頂點
            if area > max_area and len(approx) == 4:
                biggest = approx
                max_area = area
    return biggest, max_area

def reorder(mypoints):
    mypoints = mypoints.reshape((4,2)) #[[x,y],[x1,y1],[x2,y2],[x3,y3]]四層, 每層兩個
    mypointsNew = np.zeros((4,1,2),dtype=np.int32) #[[[x,y]],[[x1,y1]],[[x2,y2]],[[x3,y3]]]
    add = mypoints.sum(1) #做總和, 並依照幾何特性去排列矩形圖片的四個頂點座標順序
    mypointsNew[0] = mypoints[np.argmin(add)]
    mypointsNew[3] = mypoints[np.argmax(add)]
    diff = np.diff(mypoints,axis=1)
    mypointsNew[1] = mypoints[np.argmin(diff)]
    mypointsNew[2] = mypoints[np.argmax(diff)]
    return mypointsNew

def splitBoxes(img):
    rows = np.vsplit(img,6) #如果不能整除hieghtImg + widthImg會報錯喔
    boxes = []
    for r in rows:
        cols = np.hsplit(r,6)
        for box in cols:
            boxes.append(box) #存在Boxes裡面的是各個圖片
    return boxes

def selectNumber(question, answer):
    for y in range(6):
        for x in range(6):
            press_number = answer[y][x] - question[y][x]
            if press_number != 0:
                pyautogui.press(str(press_number))
                print(press_number)
                time.sleep(0.01)
                pyautogui.press("right")
                time.sleep(0.01)
            else:
                pyautogui.press("right")
                time.sleep(0.01)
                continue
        pyautogui.move(0,80,0.01)
        pyautogui.leftClick()
    print("破關完成")

# def prediction(boxes, model):
#     result = []
#     for image in boxes:
#         ## Prepare Image
#         img = np.asarray(image)
#         img = img[10:img.shape[0] - 10, 10:img.shape[1] - 10]
#         img = cv2.resize(img, (28,28))
#         img = img.astype("float32") / 255.0
#         img = img.reshape(1,28,28,1)
#         ## Get Prediction
#         Preds = model.predict(img)
#         classIndex = np.argmax(Preds, axis = 1)
#         probabilityValue = np.amax(Preds)
#         print(classIndex, probabilityValue)
#
#         ## Save to Result
#         if probabilityValue > 0.8:
#             result.append(classIndex[0])
#         else:
#             result.append(0)
#     return result

def centralize(img):
    img = np.asarray(img)
    img = img[20:img.shape[0] - 20, 20:img.shape[1] - 20]
    img = 255 - img
    contour, _ = cv2.findContours(img, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
    if not contour:
        return None
    x, y, w, h = cv2.boundingRect(max(contour, key=cv2.contourArea))
    digit = img[y:y + h, x:x + w]
    digit = cv2.resize(digit, (20, 20))
    canvas = np.zeros((28,28),dtype="uint8")
    canvas[4:24,4:24] = digit

    return canvas

def prediction(boxes, model):
    result = []
    for img in boxes:
        ## Prepare Image
        img = centralize(img)
        if img is None:
            result.append(0)
            continue ###這邊出問題
        img = img.astype("float32") / 255
        # CNN 格式
        img = img.reshape(1, 28, 28, 1)
        ## Get Prediction
        Preds = model.predict(img)
        classIndex = int(np.argmax(Preds, axis = 1))
        Answer = classIndex + 1
        probabilityValue = np.amax(Preds)
        ## Save to Result
        if Answer == 2 and probabilityValue < 0.8:
            Answer = 1
            result.append(Answer)
        else:
            if probabilityValue > 0.85:
                result.append(Answer)
            else:
                result.append(0)

    return result
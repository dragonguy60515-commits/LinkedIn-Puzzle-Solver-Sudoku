from Utility import *
from Sudoku import *
import pyautogui
import time
import cv2
import test
import GeneImage

#Image need to resize to big enough, OCR can work successfully. 900*900
hieghtImg = 420
widthImg = 420
#第一格
x = 750
y = 350
model = initializePrediction()

location = pyautogui.locateCenterOnScreen('symbol.png', confidence=0.8)
if location is not None:
    pyautogui.click(location)
else:
    print("找不到影像。")

time.sleep(0.5)
screenshot = pyautogui.screenshot(region=(650,292,600,730))
#
# img = cv2.imread("Sudo.png")
# #Prepare the image
img = cv2.resize(np.array(screenshot), (hieghtImg, widthImg))
img = cv2.resize(img, (hieghtImg, widthImg))
Imgblank = np.zeros((hieghtImg, widthImg, 3), np.uint8)
imgthreshold = preProcess(img)

#Find all contours
imgContours = img.copy()
imgBigcontour = img.copy()
contours, _ = cv2.findContours(imgthreshold, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
cv2.drawContours(imgContours, contours, -1, (0, 0, 255), 3)

#Find the biggest contours
biggest, max_area = biggestContours(contours)
# [[[ 34  12]]
#
#  [[ 35 279]]
#
#  [[369 278]]
#
#  [[369  11]]]

if biggest.size != 0:
    biggest = reorder(biggest) #用reorder函式求得需要的座標順序
    # [[[34  12]]
    #
    #  [[369  11]]
    #
    #  [[35 279]]
    #
    #  [[369 278]]]
    cv2.drawContours(imgBigcontour, biggest, -1, (255, 0, 255), 20)
    pts1 = np.float32(biggest) #原圖, 用來做透視轉換矩陣perspectivewarp
    pts2 = np.float32([[0,0],[widthImg, 0],[0,hieghtImg],[widthImg,hieghtImg]]) #透視轉換後矩陣順序
    matrix = cv2.getPerspectiveTransform(pts1, pts2) #求得可以用來轉換pts1, pts2的透視矩陣
    imgWarpedColored = cv2.warpPerspective(img, matrix, (hieghtImg, widthImg)) #這個output其實也是個圖片, 只是我們將目標區域特別顯示出來(biggestcontour)
    imgDetectedDigits = Imgblank.copy()
    imgWarpedColored = cv2.cvtColor(imgWarpedColored, cv2.COLOR_BGR2GRAY)
    ###遇到黑底白字的狀況------------------------------------
    # imgWarpedColored = 255 - imgWarpedColored
    ###------------------------------------
    imgWarpedColored = cv2.adaptiveThreshold(imgWarpedColored, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
    # imgWarpedColored = cv2.dilate(imgWarpedColored, None, iterations=1)
    # imgWarpedColored = cv2.erode(imgWarpedColored, None, iterations=1)

#Split the image separately and find each digit available
    boxes = splitBoxes(imgWarpedColored)
# # # ---------------------------------------
    sudo_question = prediction(boxes, model)
    # print(sudo_question)
    sudo_question = np.array(np.reshape(sudo_question, (6, 6)))  # 轉成np.array才可以reshape
    question = sudo_question.copy()

    ###儲存圖片-----------------------------------------
    # saveImage = GeneImage.centralize(boxes[34])
    # GeneImage.writeImage(saveImage)
    ###-------------------------------------------------
    print(sudo_question)
    if solve(sudo_question):
        sudo_answer = sudo_question
        print(sudo_answer)
        pyautogui.leftClick(x, y)
        time.sleep(0.05)
        selectNumber(question, sudo_answer)
# # # ---------------------------------------
# imgArray = ([img, imgthreshold, imgContours, imgBigcontour],
#             [Imgblank, Imgblank, Imgblank, Imgblank])
#
# stackedImage = stackedImage(imgArray, 1)
#
# cv2.imshow("stackedImage",stackedImage)
# cv2.waitKey(0)
# #
#



# sudo_grid = [
#     [0,0,0,0,0,0],
#     [0,4,3,1,2,0],
#     [0,0,0,0,6,0],
#     [0,5,0,0,0,0],
#     [0,1,6,4,3,0],
#     [0,0,0,0,0,0]]

# sudo_grid = [
#     [5,3,0,0,7,0,0,0,0],
#     [6,0,0,1,9,5,0,0,0],
#     [0,9,8,0,0,0,0,6,0],
#     [8,0,0,0,6,0,0,0,3],
#     [4,0,0,8,0,3,0,0,1],
#     [7,0,0,0,2,0,0,0,6],
#     [0,6,0,0,0,0,2,8,0],
#     [0,0,0,4,1,9,0,0,5],
#     [0,0,0,0,8,0,0,7,9]]
import time
count = 0

def check_possible(sudo_grid,y,x,k):
    if k in sudo_grid[y]: #檢查Row橫的
        return False
    #不能寫if sudo_grid[y] == k , 這是一個list對比integer, 永遠不會回傳False
    for i in range(6): #9*9:9 6*6:6
        if sudo_grid[i][x] == k: #檢查Column直的
            return False
    x0 = x//3*3
    y0 = y//2*2 #9*9:3 6*6:2
    for i in range(3):
        for j in range(2): #9*9:3 6*6:2
            if sudo_grid[y0+j][x0+i] == k:
                return False
    return True

def check_empty(sudo_grid):
    for i in range(6): #9*9:9 6*6:6
        for j in range(6): #9*9:9 6*6:6
            if sudo_grid[i][j] == 0:
                return i,j
    return None

def solve(sudo_grid):
    global count
    t1 = time.time()
    result = check_empty(sudo_grid) #找下一個空格, 並回傳位置
    if result == None:
        t2 = time.time()
        print("總運算時間", t2 - t1)
        print("總退回次數", count)
        return True
    y,x = result

    for k in range(1,7): #9*9:10 6*6:7
        if check_possible(sudo_grid,y,x,k) == True: #如果跑了9個數字都沒找到, 會回傳False, 並跳回上一層嘗試的數字, 跟老鼠鑽迷宮一樣
            sudo_grid[y][x]=k

            if solve(sudo_grid) == True:
                return True

            sudo_grid[y][x]=0
            # for row in sudo_grid:
            #     print(row)
            # print("--------------")
            count += 1
    return False

# solve() #如果最外層 solve() 回傳 False, 那 sudo_grid 會被回溯成原狀











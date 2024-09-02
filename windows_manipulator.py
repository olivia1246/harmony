import win32api, win32con, win32gui, win32ui
import random
import time
import ctypes

ctypes.windll.shcore.SetProcessDpiAwareness(1)

#Prints all open window names, helpful when looking for true window name
def winEnumHandler(window_name, w_list):
    if win32gui.IsWindowVisible(window_name):
        str_w = win32gui.GetWindowText(window_name)
        if str_w != '' or str_w != ' ' or str_w != 'Windows Task Manager' or str_w != 'Settings':    
            w_list.append("{}".format(str_w))

#Calls EnumWindows
def printWindows():  
    win_list = []    
    win32gui.EnumWindows(winEnumHandler, win_list)
    return win_list
    
#Sets target window (hwnd)
#Parameters:
    #window_name: cell name of target window
        #may have to enum windows to find correct name
def getHwnd(window_name):
    hwnd = win32gui.FindWindow(None, window_name)
    if hwnd == None:
        print("Window Not Found.")
    return hwnd
        
#Forces target window (hwnd) to foreground
def activateWindow(hwnd):
    user32 = ctypes.windll.user32
    user32.SetForegroundWindow(hwnd)
    if user32.IsIconic(hwnd):
        user32.ShowWindow(hwnd, 9)

#Gets top left and bottom right coordinate of the target window
#for precise image capture and click mapping
def getWindow(hwnd):
    rect = win32gui.GetWindowRect(hwnd)
    x = rect[0]
    y = rect[1]
    x2 = rect[2]
    y2 = rect[3]
    
    return x, y, x2, y2

#Generates random float between low and high inclusive
#Parameters:
    #low: float for lowest possible value to generate
    #high: float for highest possible value to generate
def randNum(low, high):
    randNum = random.uniform(low, high)
    return randNum
    
def rightClick():
    win32api.mouse_event(win32con.MOUSEEVENTF_RIGHTDOWN,0,0)
    time.sleep(randNum(0.05,0.1))
    win32api.mouse_event(win32con.MOUSEEVENTF_RIGHTUP,0,0)
    

def click():
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN,0,0)
    time.sleep(randNum(0.05,0.1))
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP,0,0)
    
#clicks and drags mouse to x, y
def clickHold(x, y, s):
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN,0,0)
    moveMouse(x, y, s)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP,0,0)

#TODO: pass parameter for scroll amount
#Scroll up
def mouseScrollUp():
    win32api.mouse_event(win32con.MOUSEEVENTF_WHEEL, 0, 0, 500)

#scroll down
def mouseScrollDown():
    win32api.mouse_event(win32con.MOUSEEVENTF_WHEEL, 0, 0, -500)


#sleep for a random amount of time between floats low and high inclusive
def sleep(low, high):
    r_num = randNum(low, high)
    #print("Sleeping For {}".format(round(r_num, 2)))
    time.sleep(r_num)

#Moves mouse with upwards or downwards arc
#Parameters:
    #Takes x, y coordinates of point to move cursor to
    #s for speed, set to True for faster cursor movement
def moveMouse(x, y, s):  #TODO: add angle param to allow custom set arc heights and movements
    x1 = 0
    y1 = 0
        
    pos = win32api.GetCursorPos()
    orig_dest = [x, y]
    line = getLine(pos[0], pos[1], x+x1, y+y1)
    
    t = 0.0001
    if s:
        del line[::2]
        del line[::2]
        
    ctr = 0
    for i in line:
        ctr+=1
        
    s1 = ctr / 3
    s1 = int(s1)
    ctr = ctr - s1
    
    s2 = s1 + s1
    
    s3 = s2 + s1
    
    lines = []
    tmp = line[0:s1]
    lines.append(tmp)
    
    tmp = line[s1:s2]
    lines.append(tmp)
    
    tmp = line[s2:s3]
    lines.append(tmp)
    
    vert = random.randint(1,2)

    ctr = 0
    for point in lines[0]:
        x = point[0]
        y = point[1]
        y = y + ctr
        
        p = [x, y]
        win32api.SetCursorPos(p)
        
        if vert == 1:
            ctr += 1
        else:
            ctr -= 1
            
        time.sleep(t)
        
    for point in lines[1]:
        x, y = point
        y = y + ctr
        
        p = [x, y]
        win32api.SetCursorPos(p)
        time.sleep(t)
        
    for point in lines[2]:
        x = point[0]
        y = point[1]
        y = y + ctr
        
        p = [x, y]
        win32api.SetCursorPos(p)
        
        if vert == 1:
            ctr -= 1
        else:
            ctr += 1
            
        time.sleep(t)

#get every integer point between 2 points
#used in moveMouse function to make mouse movements more human
def getLine(x1, y1, x2, y2):
    rise = (y2 - y1)
    run = (x2 - x1)
    
    m = rise / run
    
    f = m * x1
    
    b = y1 - f
    
    line = []
    x = x1
    y = y1
    
    y_dif = y2 - y1
    if y_dif < 0:
        y_dif = y_dif * -1
        
    x_dif = x2 - x1
    if x_dif < 0:
        x_dif = x_dif * -1
                
    if x_dif > y_dif:
        if x < x2:
            while x != x2 and y != y2:
                x += 1
                y = m * x + b
                line.append([x, round(y)])
        else:
            while x != x2 and y != y2:
                x -= 1
                y = m * x + b
                line.append([x, round(y)])
    
    else:
        if y < y2:
            while x != x2 and y != y2:
                y += 1
                x = y / m - b / m
                line.append([round(x), y])
        else:
            while x != x2 and y != y2:
                y -= 1
                x = y / m - b / m
                line.append([round(x), y])
            
    return line

#Get screenshot of current window
def getScreenshot(path=None):
    try:
        x = 0
        y = 0
        
        x2 = win32api.GetSystemMetrics(0)
        y2 = win32api.GetSystemMetrics(1)
        
        W = x2 - x
        H = y2 - y
        
        #get image data
        wDC = win32gui.GetWindowDC(None)
        dcObj = win32ui.CreateDCFromHandle(wDC)
        cDC = dcObj.CreateCompatibleDC()
        dataBitMap = win32ui.CreateBitmap()
        dataBitMap.CreateCompatibleBitmap(dcObj, W, H)
        cDC.SelectObject(dataBitMap)
        cDC.BitBlt((0, 0), (W, H), dcObj, (0, 0), win32con.SRCCOPY)

        if path == None:
            dataBitMap.SaveBitmapFile(cDC, "C:\\Users\\Public\\Downloads\\Update.png")
        else:
            dataBitMap.SaveBitmapFile(cDC, path)

        #Free Resources
        dcObj.DeleteDC()
        cDC.DeleteDC()
        win32gui.ReleaseDC(None, wDC)
        win32gui.DeleteObject(dataBitMap.GetHandle())

        return True
    except:
        return False
        
#Get screenshot of specific window provided the hwnd
def getFocusScreenshot(hwnd, path=None):
    try:
        x, y, x2, y2 = getWindow(hwnd)
        
        W = x2 - x - 5
        H = y2 - y - 5
        
        #get image data
        wDC = win32gui.GetWindowDC(hwnd)
        dcObj = win32ui.CreateDCFromHandle(wDC)
        cDC = dcObj.CreateCompatibleDC()
        dataBitMap = win32ui.CreateBitmap()
        dataBitMap.CreateCompatibleBitmap(dcObj, W, H)
        cDC.SelectObject(dataBitMap)
        cDC.BitBlt((0, 0), (W, H), dcObj, (0, 0), win32con.SRCCOPY)

        if path == None:
            dataBitMap.SaveBitmapFile(cDC, "C:\\Users\\Public\\Downloads\\Update.png")
        else:
            dataBitMap.SaveBitmapFile(cDC, path)
            
        #Free Resources
        dcObj.DeleteDC()
        cDC.DeleteDC()
        win32gui.ReleaseDC(hwnd, wDC)
        win32gui.DeleteObject(dataBitMap.GetHandle())
        
        return True
    except:
        return False

def isAdmin():
    user = ''
    admins = ''
    platform = 'powershell.exe '
    admin_cmd = 'net localgroup administrators'
    admin_cmd = admin_cmd.split()
    
    for line in run_command('whoami'):
        user += line.decode()
    for line in run_command(admin_cmd):
        admins += line.decode()
        
    if '\\' in user:
        user = user.split('\\')[1]

    if 'Administrator' in admins:
        admins = admins.split('Administrator')[2]

    if user in admins:
        return True
        
    else:
        return False

def runCommand(command):
    p = subprocess.Popen(command, shell = True,
                         stdout=subprocess.PIPE,
                         stderr=subprocess.STDOUT)

    return iter(p.stdout.readline, b'')
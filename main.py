import os
from fastapi import FastAPI, Request
from dotenv import load_dotenv
import urllib.request
from urllib.parse import quote
from pathlib import Path
import brain
app = FastAPI()

# Save your config file as "telegram-bot-config.env" for recieving updates on Telegram
try:
    dotenv_path = Path('telegram-bot-config.env')
    load_dotenv(dotenv_path=dotenv_path)

    botToken = os.getenv('BOT_TOKEN')
    ownerId = os.getenv('OWNER_ID')
except:
    None


@app.post("/move")
async def handle_move(request: Request):
    data = await request.json()
    move = brain.generate_smart_move(data, "survival")
    return {"move": move}


@app.post("/start")
async def handle_start(request: Request):
    data = await request.json()
    print(f"Battle started!\n{data['game']}")
    try:
        snakesMessage = '\n<b>Snake details :</b>\n'
        for i in data['board']['snakes']:
            snakesMessage += f" - <code>{i['name']}</code>\n"
        message = f"<b>Battle started!</b>\n\n<b>Game ID :</b> <code>{data['game']['id']}</code>\n<b>Board :</b> <code>{data['board']['width']}x{data['board']['height']}</code>\n{snakesMessage}\n<a href='https://play.battlesnake.com/g/{data['game']['id']}'>View Match</a>"
        urllib.request.urlopen(
            f"https://api.telegram.org/bot{botToken}/sendMessage?text={quote(message)}&chat_id={ownerId}&parse_mode=HTML&disable_web_page_preview=True")
    except:
        None
    return "ok"


@app.get("/")
def handle_info():
    print("INFO Battlesnake information captured")
    return {
        "apiversion": "1",
        "author": "dvishal485",
        "color": "#3E338F",
        "head": "evil",
        "tail": "bolt",
    }


@app.post("/end")
async def end(request: Request):
    data = await request.json()
    print(f"Battle ended!")
    print(data)
    try:
        message = f"<b>Match ended!</b>\n<b>Game ID:</b> <code>{data['game']['id']}</code>"
        message += f"\n\n<a href='https://play.battlesnake.com/g/{data['game']['id']}'>View Match</a>"
        urllib.request.urlopen(
            f"https://api.telegram.org/bot{botToken}/sendMessage?text={quote(message)}&chat_id={ownerId}&parse_mode=HTML&disable_web_page_preview=True")
    except:
        None
    return "ok"

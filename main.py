from fastapi import FastAPI, Request
import brain
app = FastAPI()


@app.post("/move")
async def handle_move(request: Request):
    data = await request.json()
    move = brain.generate_smart_move(data, "survival")
    return {"move": move}


@app.post("/start")
async def handle_start(request: Request):
    data = await request.json()
    print(f"Battle started!\n{data['game']}")
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
    print(f"Battle ended!\n{data['game']}")
    return "ok"

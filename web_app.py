import asyncio
import json
import webbrowser
from queue import Queue
from threading import Thread

import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import StreamingResponse

import kiit_ultra_bot

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Global log queue for SSE
log_queue = Queue()

def ui_log_callback(status: str, message: str):
    # Pass event to the queue
    log_queue.put({"status": status, "message": message})

# Hook the callback into the bot
kiit_ultra_bot.UI_LOG_CALLBACK = ui_log_callback


@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/api/start")
async def start_bot(request: Request):
    data = await request.json()
    
    # Update config.json with user input
    cm = kiit_ultra_bot.ConfigManager()
    config = cm.config
    
    config["credentials"]["email"] = data.get("email", "")
    config["credentials"]["password"] = data.get("password", "")
    config["registration"]["sections"] = [s.strip() for s in data.get("sections", "").split(",")]
    config["registration"]["semester"] = data.get("semester", "3rd")
    
    # Run the bot in a separate thread so we don't block the API
    def run_bot():
        try:
            kiit_ultra_bot.execute_swarm(config)
            log_queue.put({"status": "done", "message": "Process Completed"})
        except Exception as e:
            log_queue.put({"status": "error", "message": str(e)})
            log_queue.put({"status": "done", "message": "Process Failed"})

    thread = Thread(target=run_bot)
    thread.start()
    
    return {"message": "Bot started"}


async def event_stream():
    """Server-Sent Events stream generator"""
    while True:
        if not log_queue.empty():
            log = log_queue.get()
            yield f"data: {json.dumps(log)}\n\n"
            if log["status"] == "done":
                break
        await asyncio.sleep(0.1)

@app.get("/stream")
async def stream():
    return StreamingResponse(event_stream(), media_type="text/event-stream")


def open_browser():
    import os
    if not os.environ.get("RENDER"):
        webbrowser.open("http://127.0.0.1:8000")

if __name__ == "__main__":
    # Open the browser shortly after starting
    Thread(target=lambda: (asyncio.run(asyncio.sleep(1.5)), open_browser())).start()
    uvicorn.run("web_app:app", host="127.0.0.1", port=8000, reload=False)

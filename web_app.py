import asyncio
import os
import uuid
import webbrowser
from threading import Thread

import uvicorn
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

import kiit_ultra_bot

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# In-memory session store (maps session_id -> KiitAgent instance)
# WARNING: This keeps a full Chrome instance open per session!
active_sessions = {}

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/api/login")
async def login(request: Request):
    data = await request.json()
    email = data.get("email")
    password = data.get("password")
    
    if not email or not password:
        raise HTTPException(status_code=400, detail="Missing credentials")
        
    session_id = str(uuid.uuid4())
    agent = kiit_ultra_bot.KiitAgent()
    active_sessions[session_id] = agent
    
    # Run login and scrape synchronously (can take 5-10 seconds)
    success = agent.login(email, password)
    
    if not success:
        agent.close()
        del active_sessions[session_id]
        raise HTTPException(status_code=401, detail="Login to SAP failed")
        
    dashboard_data = agent.scrape_dashboard()
    
    return {
        "message": "Login successful",
        "session_id": session_id,
        "data": dashboard_data
    }

@app.post("/api/submit_selection")
async def submit_selection(request: Request):
    data = await request.json()
    session_id = data.get("session_id")
    subject = data.get("subject")
    section = data.get("section")
    
    agent = active_sessions.get(session_id)
    if not agent:
        raise HTTPException(status_code=401, detail="Session expired or invalid")
        
    success = agent.submit_selection(subject, section)
    if success:
        return {"message": "Selection submitted successfully"}
    else:
        raise HTTPException(status_code=500, detail="Failed to submit selection")

@app.get("/api/download_demand_letter")
async def download_demand_letter(session_id: str):
    agent = active_sessions.get(session_id)
    if not agent:
        raise HTTPException(status_code=401, detail="Session expired or invalid")
        
    filepath = agent.download_demand_letter()
    if filepath and os.path.exists(filepath):
        return FileResponse(path=filepath, filename="Demand_Letter.pdf", media_type='application/pdf')
    else:
        raise HTTPException(status_code=500, detail="Failed to download demand letter")

@app.post("/api/logout")
async def logout(request: Request):
    data = await request.json()
    session_id = data.get("session_id")
    
    agent = active_sessions.get(session_id)
    if agent:
        agent.close()
        del active_sessions[session_id]
        
    return {"message": "Logged out successfully"}

def open_browser():
    if not os.environ.get("RENDER"):
        webbrowser.open("http://127.0.0.1:8000")

if __name__ == "__main__":
    Thread(target=lambda: (asyncio.run(asyncio.sleep(1.5)), open_browser())).start()
    uvicorn.run("web_app:app", host="0.0.0.0", port=8000, reload=False)

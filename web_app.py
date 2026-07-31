import asyncio
import os
import uuid
import time
import base64
import webbrowser
from threading import Thread

import uvicorn
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization, hashes
from starlette.middleware.base import BaseHTTPMiddleware

import kiit_ultra_bot

# --- 1. CRYPTO ENGINE (RAM ONLY) ---
private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
public_key = private_key.public_key()
public_pem = public_key.public_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PublicFormat.SubjectPublicKeyInfo
).decode('utf-8')

app = FastAPI()

# --- 2. CSP AND SECURITY HEADERS ARMOR ---
class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        response.headers["Content-Security-Policy"] = "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; font-src 'self' https://fonts.gstatic.com;"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        return response

app.add_middleware(SecurityHeadersMiddleware)

# --- 3. RATE LIMITING (3 STRIKES, 15 MIN BAN) ---
failed_attempts = {}
BAN_TIME = 900 # 15 minutes

def is_rate_limited(ip: str) -> bool:
    now = time.time()
    if ip in failed_attempts:
        attempts = [t for t in failed_attempts[ip] if now - t < BAN_TIME]
        failed_attempts[ip] = attempts
        if len(attempts) >= 3:
            return True
    return False

def record_failure(ip: str):
    now = time.time()
    if ip not in failed_attempts:
        failed_attempts[ip] = []
    failed_attempts[ip].append(now)

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

active_sessions = {}

@app.get("/api/public-key")
async def get_public_key():
    return {"public_key": public_pem}

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/api/login")
async def login(request: Request):
    client_ip = request.client.host
    if is_rate_limited(client_ip):
        raise HTTPException(status_code=429, detail="Too many failed attempts. You are locked out for 15 minutes.")

    data = await request.json()
    email = data.get("email")
    encrypted_password_b64 = data.get("password")
    
    if not email or not encrypted_password_b64:
        raise HTTPException(status_code=400, detail="Missing credentials")
        
    try:
        # Decrypt password using RAM-only private key
        encrypted_password = base64.b64decode(encrypted_password_b64)
        decrypted_password = private_key.decrypt(
            encrypted_password,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        ).decode('utf-8')
    except Exception as e:
        record_failure(client_ip)
        raise HTTPException(status_code=400, detail="Decryption failed. Security violation.")

    session_id = str(uuid.uuid4())
    agent = kiit_ultra_bot.KiitAgent()
    active_sessions[session_id] = agent
    
    # Run login and scrape synchronously
    success = agent.login(email, decrypted_password)
    
    # SECURITY OVERRIDE: Destroy sensitive data in memory immediately
    del decrypted_password
    del encrypted_password_b64
    del encrypted_password
    data.clear()
    
    if not success:
        agent.close()
        del active_sessions[session_id]
        record_failure(client_ip)
        raise HTTPException(status_code=401, detail="Login to SAP failed")
        
    dashboard_data = agent.scrape_dashboard()
    
    # Successful login, reset failed attempts
    if client_ip in failed_attempts:
        del failed_attempts[client_ip]
    
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

@app.get("/api/debug_html")
async def debug_html():
    # TEMPORARY ENDPOINT: Dumps HTML of the active session so we can calibrate the scraper
    if not active_sessions:
        return HTMLResponse("No active sessions")
    agent = list(active_sessions.values())[0]
    if agent.driver:
        html = "<html><body>"
        try:
            agent.driver.switch_to.default_content()
            html += f"<h2>Main Page</h2><textarea rows='10' cols='100'>{agent.driver.page_source}</textarea>"
            iframes = agent.driver.find_elements(By.TAG_NAME, "iframe")
            for i, frame in enumerate(iframes):
                try:
                    f_id = frame.get_attribute('id')
                    agent.driver.switch_to.frame(frame)
                    html += f"<h2>Iframe {i} ({f_id})</h2><textarea rows='10' cols='100'>{agent.driver.page_source}</textarea>"
                    nested = agent.driver.find_elements(By.TAG_NAME, "iframe")
                    for j, nframe in enumerate(nested):
                        try:
                            n_id = nframe.get_attribute('id')
                            agent.driver.switch_to.frame(nframe)
                            html += f"<h2>Nested {i}-{j} ({n_id})</h2><textarea rows='10' cols='100'>{agent.driver.page_source}</textarea>"
                            agent.driver.switch_to.parent_frame()
                        except: pass
                    agent.driver.switch_to.default_content()
                except: 
                    agent.driver.switch_to.default_content()
        except Exception as e:
            html += f"<p>Error: {str(e)}</p>"
        html += "</body></html>"
        return HTMLResponse(html)
    return HTMLResponse("No driver")

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

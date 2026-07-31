<div align="center">

# 🤖 KIIT Ultra Auto-Registration Bot v5.0 (Web Edition)

**Fully Automated Semester and Section Selection for KIIT SAP Portal**

[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.103.0-009688.svg?style=flat&logo=FastAPI&logoColor=white)](https://fastapi.tiangolo.com)
[![Selenium](https://img.shields.io/badge/Selenium-WebDriver-green.svg)](https://www.selenium.dev/)
[![Platform](https://img.shields.io/badge/platform-Cloud%20Ready-lightgrey.svg)]()
[![Security](https://img.shields.io/badge/Security-RSA--2048%20%7C%20TLS-red.svg)]()

This bot is designed to automate the process of semester and section selection on the KIIT SAP Portal. Version 5.0 introduces a fully responsive web dashboard, military-grade client-side encryption, and humanized behavioral stealth mechanisms.

</div>

---

## ✨ Key Features

- **🌐 Interactive Web Dashboard:** A sleek, dark-mode web interface replacing the old terminal prompts.
- **🚀 Automated Login:** Logs into the KIIT SAP Portal using provided credentials securely.
- **🎯 Section Selection Navigation:** Automatically navigates to the section selection page.
- **📅 Smart Selections:** Clicks the designated year, session, subject, and section dropdowns effortlessly.
- **⚡ Auto-Submission:** Automatically clicks "ADD" and "SUBMIT" buttons to finalize registration in milliseconds.
- **🛡️ Extreme Security (RSA-2048):** Your password is encrypted inside your browser using an RSA Public Key before transmission. The backend actively memory-wipes the credentials immediately after injection.
- **👻 Stealth & Humanization:** Employs advanced human-like typing simulation (randomized millisecond delays) and headless browser user-agent masking to remain completely undetectable to SAP behavioral monitoring.
- **☁️ Cloud Ready:** Pre-configured for seamless deployment on platforms like Render using Docker.

---

## 🔒 Security Architecture

The KIIT Ultra Bot v5.0 implements a zero-trust credential handling architecture:
1. **Client-Side Encryption:** When you hit "Connect", the JavaScript fetches an RSA-2048 Public Key from the server and encrypts your password *before* it leaves your computer.
2. **Memory Annihilation:** The Python backend receives the encrypted string, decrypts it in memory, uses it via Selenium, and immediately executes `secure_wipe_string()` followed by python's garbage collector `del` to permanently scrub the data from RAM.
3. **Session Tokens:** No passwords are saved in cookies. The dashboard uses randomized UUIDv4 session identifiers for subsequent interactions (like downloading demand letters).

---

## ⚠️ CRITICAL WARNING ⚠️

> **Using this bot violates KIIT's Terms of Service.** The bot AUTOMATICALLY interacts with the registration system, including clicking "ADD" and "SUBMIT" buttons programmatically.
>
> **YOU ARE SOLELY RESPONSIBLE FOR ANY CONSEQUENCES** that may arise from using this software, including but not limited to:
> - Disciplinary action from KIIT University.
> - Issues with your registration.
> - Any data discrepancies or errors.
>
> **Proceed at your own risk.**

---

## 🚀 Installation & Usage

1. **Clone the repository:**
   ```bash
   git clone https://github.com/nirmalya-ghosh/KIIT-Selection-Bot.git
   cd KIIT-Selection-Bot
   ```

2. **Install required Python packages:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Start the Web Server:**
   ```bash
   uvicorn web_app:app --host 0.0.0.0 --port 8000
   ```
   
4. **Access the Dashboard:**
   Open your web browser and navigate to `http://localhost:8000`.

---

## ☁️ Cloud Deployment (Render)

This bot is fully configured for cloud deployment. To deploy on Render:
1. Connect your GitHub repository to Render as a "Web Service".
2. Select **Docker** as the Runtime environment.
3. Render will automatically read the `Dockerfile` and build the lightweight container with headless Chrome and Python.
4. Access your live proxy dashboard from anywhere in the world.

---

## 🔧 Troubleshooting

| Issue | Solution |
| :--- | :--- |
| **"Login to SAP failed" alert** | Ensure your KIIT Email/Roll Number and Password are correct. The bot strips the domain to pass the raw Roll Number to SAP NetWeaver. |
| **"Server connection failed" alert** | Usually means the backend server crashed or is unavailable. Check the Render deployment logs or your terminal. |
| **Bot fails to find elements** | The KIIT SAP portal's structure might have changed. You may need to update the XPath or CSS selectors in `kiit_ultra_bot.py`. |

---

## ⚖️ Disclaimer

This project is provided for educational purposes only. The author is not responsible for any misuse, damage, or consequences resulting from the use of this software. By using this bot, you acknowledge and accept all risks associated with it.
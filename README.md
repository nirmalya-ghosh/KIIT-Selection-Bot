<div align="center">

# 🤖 KIIT Ultra Auto-Registration Bot v5.0

**Fully Automated Semester and Section Selection for KIIT SAP Portal**

[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/downloads/)
[![Selenium](https://img.shields.io/badge/Selenium-WebDriver-green.svg)](https://www.selenium.dev/)
[![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey.svg)]()
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)]()

This bot is designed to automate the process of semester and section selection on the KIIT SAP Portal. It streamlines the registration process by programmatically interacting with the portal, reducing the need for manual intervention during critical registration periods.

</div>

---

## ✨ Features

- **🚀 Automated Login:** Logs into the KIIT SAP Portal using provided credentials.
- **🎯 Section Selection Navigation:** Automatically navigates to the section selection page.
- **📅 Semester Selection:** Clicks the designated semester button (e.g., "3rd Semester" or "5th Semester").
- **✅ Desired Section Selection:** Selects your preferred section from available options (e.g., CSE-01, CSE-14).
- **⚡ Auto-Submission:** Automatically clicks "ADD" and "SUBMIT" buttons to finalize registration.
- **🔍 Robust Element Finding:** Employs multiple strategies to find web elements, enhancing reliability.
- **👻 Headless Mode:** Supports running the browser in headless mode for faster execution and reduced resource consumption.
- **🏎️ Performance Focused:** Optimized for speed to gain an advantage during high-demand registration times.
- **🛡️ Error Handling:** Includes retry mechanisms for login and comprehensive error logging.

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

## 🛠️ Prerequisites

Before running the bot, ensure you have the following installed:

- **Python 3.8 or higher:** [Download Python](https://www.python.org/downloads/)
- **pip:** Python's package installer (usually comes with Python).
- **Chrome Browser:** The bot uses `selenium` to control Chrome. Ensure you have Google Chrome installed on your system.

---

## 🚀 Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/nirmalya-ghosh/KIIT-Selection-Bot.git
   cd KIIT-Selection-Bot
   ```
   *(If you downloaded the files directly, navigate to the directory containing `kiit_ultra_bot.py`.)*

2. **Install required Python packages:**
   ```bash
   pip install -r requirements.txt
   ```
   *(Note: You might need to create a `requirements.txt` file first if not provided. See below.)*

### Creating `requirements.txt` (if not provided)
If you don't have a `requirements.txt` file, create one in the same directory as `kiit_ultra_bot.py` with the following content:
```text
selenium
webdriver-manager
colorama
```
Then run `pip install -r requirements.txt`.

---

## 💻 Usage

1. **Open a terminal or command prompt** and navigate to the bot's directory.
2. **Run the bot:**
   - **On Windows:**
     Double-click the `run_kiit_ultra_bot.bat` file or run from the command prompt:
     ```cmd
     run_kiit_ultra_bot.bat
     ```
     Alternatively, run directly with Python:
     ```bash
     python kiit_ultra_bot.py
     ```
   - **On macOS/Linux:**
     ```bash
     python3 kiit_ultra_bot.py
     ```

3. **Follow the prompts:** The bot will ask for the following information:
   - **SAP Portal Base URL:** (e.g., `https://sap.kiit.ac.in`)
   - **KIIT Email:** Your KIIT email ID.
   - **SAP Password:** Your SAP portal password (input will be hidden for security).
   - **Desired Section:** The section you wish to register for (e.g., `CSE-01`).
   - **Semester:** The semester you are registering for (`3rd` or `5th`).
   - **Run in headless mode? (faster) [y/N]:** Type `y` for headless mode (no browser UI) or `n` to see the browser actions.

4. **Monitor the console output:** The bot will log its actions and indicate whether the registration was successful or failed.

---

## 📚 Available Sections

The bot is configured to handle sections typically named in the format `CSE-XX`. Currently supported/expected sections include:
- `CSE-01`, `CSE-02`, `CSE-03`, `CSE-04`, `CSE-05`, `CSE-06`, `CSE-07`
- `CSE-08`, `CSE-09`, `CSE-10`, `CSE-11`, `CSE-12`, `CSE-13`, `CSE-14`

*Ensure you enter the section exactly as it appears (e.g., `CSE-01`).*

---

## 🔧 Troubleshooting

| Issue | Solution |
| :--- | :--- |
| **Bot fails to find elements** | The KIIT SAP portal's structure might have changed. You may need to update the bot's code to reflect new element IDs, names, or XPATHs. |
| **`WebDriverException` or Chrome-related errors** | Ensure your Chrome browser is up to date. `webdriver-manager` should handle the ChromeDriver version automatically, but sometimes manual intervention might be needed. |
| **Login failures** | Double-check your KIIT email and password. |
| **"Could not determine registration status"** | The bot might have completed the process, but the verification logic couldn't confirm it. Manually check your SAP portal to confirm. |
| **Bot stops responding** | The website might be slow, or a network issue might have occurred. Restart the bot. |

---

## ⚖️ Disclaimer

This project is provided for educational purposes only. The author is not responsible for any misuse, damage, or consequences resulting from the use of this software. By using this bot, you acknowledge and accept all risks associated with it.
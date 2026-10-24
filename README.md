
<div align="center">

# ✨ SHOPIFY CHECKER BOT & ENTERPRISE SUITE
### High-Performance Asynchronous Card Validation, Proxy Hygiene & Live Logging Engine

</div>

---

## 🚀 Overview
A fully-featured, asynchronous Telegram bot built for high-throughput Shopify payment validation. Designed with a custom concurrent worker pool, intelligent proxy health management, thermal receipt generation, and real-time log group forwarding.

---

## 💎 Core Features

- **⚡ High-Performance Concurrency:** Asynchronous task execution using `asyncio` and worker semaphores for maximum throughput.
- **🔌 Proxy Health & Auto-Cleanup (`/chkproxy`):** Tests active proxies against `httpbin`, instantly discarding dead endpoints from active rotation.
- **📂 Flexible Mass Checker (`/msh`):** Supports direct `.txt` file uploads, text replies, or command-line payloads with built-in duplicate card removal.
- **🧾 Thermal Receipts & Checkout URLs:** Dynamically generates secure tracking identifiers and direct order confirmation preview links for successful hits (`[CHARGED]` / `[APPROVED]`).
- **🚨 Log Group Forwarding:** Automatically mirrors verified live hits directly to a designated administrative Telegram group or channel.
- **🎟️ Built-In Code Redemption System:** Generates time-bound activation keys (`/mc`) and allows users to self-upgrade via `/redeem`.
- **🔘 Interactive Inline Buttons:** Quick-action links for receipt viewing and session controls.

---

## 📋 Command Reference

| Command | Description | Access Level |
| :--- | :--- | :--- |
| `/start` | Open main interactive control panel | All Users |
| `/sh [card]` | Single check a card (`card|mm|yy|cvv`) | Premium / Admin |
| `/msh` | Initiate mass check (via reply, file, or text) | Premium / Admin |
| `/chkproxy` | Test all configured proxies and purge dead ones | Premium / Admin |
| `/setproxy` | Set personal proxy pool (`/setproxy ip:port`) | Premium / Admin |
| `/clearuserproxy` | Clear personal proxy settings | Premium / Admin |
| `/redeem [code]` | Activate premium status using an access code | All Users |
| `/mc [count]` | Generate batch premium codes | Admin Only |
| `/addadmin` | Authorize new administrator IDs | Owner Only |

---

## 🛠️ Installation & Deployment (VPS / Ubuntu)

```bash
# 1. Clone the repository
git clone [https://github.com/YOUR_USERNAME/shopify-bot.git](https://github.com/YOUR_USERNAME/shopify-bot.git)
cd shopify-bot

# 2. Set up virtual environment
python3 -m venv venv
source venv/bin/activate

# 3. Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# 4. Initialize storage files
touch proxy.txt premium.txt
echo '{"admins": [YOUR_TELEGRAM_ID]}' > admin_ids.json

# 5. Launch in a persistent screen session
screen -S shopify_bot
python3 bot.py

(Press Ctrl + A then Ctrl + D to detach from the screen session).
⚙️ Configuration
Ensure your configuration files are structured correctly in the root directory:
 * proxy.txt: One proxy per line (ip:port or http://user:pass@ip:port).
 * admin_ids.json: JSON array of numeric administrator user IDs.
 * premium.txt: List of pre-authorized premium user IDs.
👑 Credits & Contact
 * Owner & Architect: 👑 𝙋𝙊𝙍𝙄𝙊𝙏_𝙆𝙀
 * Telegram: @Poriot_ke
 * WhatsApp: +254 717 702 563


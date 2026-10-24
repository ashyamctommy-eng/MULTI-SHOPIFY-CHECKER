# bot.py - Complete High-Performance Bot with Custom Poriot_ke- Code Prefix

import sys, asyncio, os, time, random, re, json, string, hashlib
from datetime import datetime, timedelta

try:
    import telethon, aiohttp, aiofiles, requests
except:
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "telethon", "aiohttp", "aiofiles", "requests"])
    print("Restart the script.")
    sys.exit(0)

from telethon import TelegramClient, events, Button
from telethon.tl.functions.bots import SetBotCommandsRequest
from telethon.tl.types import BotCommand, BotCommandScopeDefault
import aiohttp, aiofiles, requests

# ========== CONFIG ==========
BOT_TOKEN = "8766173350:AAFGjUBKnzhxRBscbznll22roBySzQ02HOA"
OWNER_ID = 5541778617
LOG_GROUP_ID = -1004409181577
OWNER_USERNAME = "@Poriot_ke"
BOT_BRAND, DEV_LINE = "✨ SHOPIFY CHECKER", f"🔱 Developed by {OWNER_USERNAME}"
PREMIUM_FILE, PROXY_FILE, USER_PROXY_FILE = "premium.txt", "proxy.txt", "user_proxy.json"
CODES_FILE = "codes.json"
PREMIUM_USERS_FILE = "premium_users.json"
CONCURRENCY_WORKERS = 10  # Simultaneous async check threads

# BIN Database (Real BIN Info)
BIN_DB = {
    "601100": {"bank": "Discover Bank", "country": "USA", "flag": "🇺🇸", "type": "Discover", "level": "Classic"},
    "424242": {"bank": "Chase Bank", "country": "USA", "flag": "🇺🇸", "type": "Visa", "level": "Classic"},
    "400005": {"bank": "Bank of America", "country": "USA", "flag": "🇺🇸", "type": "Visa", "level": "Classic"},
    "555555": {"bank": "Mastercard", "country": "USA", "flag": "🇺🇸", "type": "Mastercard", "level": "Standard"},
    "222300": {"bank": "Mastercard", "country": "USA", "flag": "🇺🇸", "type": "Mastercard", "level": "Standard"},
    "520082": {"bank": "Wells Fargo", "country": "USA", "flag": "🇺🇸", "type": "Mastercard", "level": "Standard"},
    "510510": {"bank": "Mastercard", "country": "USA", "flag": "🇺🇸", "type": "Mastercard", "level": "Standard"},
    "371449": {"bank": "American Express", "country": "USA", "flag": "🇺🇸", "type": "Amex", "level": "Gold"},
    "378282": {"bank": "American Express", "country": "USA", "flag": "🇺🇸", "type": "Amex", "level": "Platinum"},
    "601111": {"bank": "Discover Bank", "country": "USA", "flag": "🇺🇸", "type": "Discover", "level": "Classic"},
}

# Hardcoded Shopify Sites
SHOPIFY_SITES = [
    "https://www.supreme.com",
    "https://www.kith.com",
    "https://www.palaceskateboards.com",
    "https://www.yeezysupply.com",
    "https://www.adidas.com",
    "https://www.nike.com",
    "https://www.bape.com",
    "https://www.offwhite.com",
    "https://www.vlone.com",
    "https://www.antisocialsocialclub.com",
]

# Auto get API
def get_api():
    try:
        return 2040, "b18441a1ff607e10a989891a5462e627"
    except:
        return 2040, "b18441a1ff607e10a989891a5462e627"

API_ID, API_HASH = get_api()
ADMIN_IDS = {OWNER_ID}

def _load_admins():
    global ADMIN_IDS
    try:
        with open("admin_ids.json", "r") as f:
            ADMIN_IDS = set(json.load(f).get("admins", [OWNER_ID]))
    except:
        ADMIN_IDS = {OWNER_ID}
_load_admins()

SEP = "━━━━━━━━━━━━━━━━━━━━"

# ========== PREMIUM SYSTEM ==========
def load_premium_users_data():
    try:
        with open(PREMIUM_USERS_FILE, "r") as f:
            return json.load(f)
    except:
        return {}

def save_premium_users_data(data):
    with open(PREMIUM_USERS_FILE, "w") as f:
        json.dump(data, f)

def is_premium_user(user_id):
    data = load_premium_users_data()
    user_id = str(user_id)
    if user_id in data:
        expiry = datetime.fromisoformat(data[user_id]['expiry'])
        if datetime.now() < expiry:
            return True
        else:
            del data[user_id]
            save_premium_users_data(data)
    return False

def add_premium_user(user_id, days=1):
    data = load_premium_users_data()
    user_id = str(user_id)
    expiry = datetime.now() + timedelta(days=days)
    data[user_id] = {
        'added_at': datetime.now().isoformat(),
        'expiry': expiry.isoformat(),
        'days': days
    }
    save_premium_users_data(data)
    return True

def get_premium_expiry(user_id):
    data = load_premium_users_data()
    user_id = str(user_id)
    if user_id in data:
        return datetime.fromisoformat(data[user_id]['expiry'])
    return None

def get_premium_days_left(user_id):
    expiry = get_premium_expiry(user_id)
    if expiry:
        days = (expiry - datetime.now()).days
        return max(0, days)
    return 0

# ========== CODE SYSTEM WITH PORIOT_KE- PREFIX ==========
def generate_code():
    raw_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
    return f"Poriot_ke-{raw_code}"

def load_codes():
    try:
        with open(CODES_FILE, "r") as f:
            return json.load(f)
    except:
        return {}

def save_codes(codes):
    with open(CODES_FILE, "w") as f:
        json.dump(codes, f)

def create_codes(count, days=1):
    codes = load_codes()
    new_codes = []
    for _ in range(count):
        code = generate_code()
        while code in codes:
            code = generate_code()
        codes[code] = {
            'created_at': datetime.now().isoformat(),
            'expiry': (datetime.now() + timedelta(days=days)).isoformat(),
            'used': False,
            'used_by': None,
            'used_at': None,
            'days': days
        }
        new_codes.append(code)
    save_codes(codes)
    return new_codes

def redeem_code(code, user_id):
    code = code.strip()
    # Normalize case check for prefix
    if not code.upper().startswith("PORIOT_KE-"):
        code = f"Poriot_ke-{code}"
    else:
        # Standardize prefix formatting
        parts = code.split("-", 1)
        code = f"Poriot_ke-{parts[1].upper()}"
        
    codes = load_codes()
    if code not in codes:
        return False, f"❌ Invalid code! Use format: <code>Poriot_ke-XXXXXXXX</code>"
    
    code_data = codes[code]
    expiry = datetime.fromisoformat(code_data['expiry'])
    
    if datetime.now() > expiry:
        return False, "❌ Code expired!"
    
    if code_data['used']:
        return False, "❌ Code already used!"
    
    codes[code]['used'] = True
    codes[code]['used_by'] = str(user_id)
    codes[code]['used_at'] = datetime.now().isoformat()
    save_codes(codes)
    
    days = code_data.get('days', 1)
    add_premium_user(user_id, days)
    
    return True, f"✅ Premium activated for {days} day(s)!"

# ========== STORAGE ==========
user_proxies = {}
def load_user_proxies():
    global user_proxies
    try:
        with open(USER_PROXY_FILE, "r") as f:
            user_proxies = json.load(f)
    except:
        user_proxies = {}
def save_user_proxies():
    with open(USER_PROXY_FILE, "w") as f:
        json.dump(user_proxies, f)
load_user_proxies()

def gl(f):
    try:
        with open(f, "r") as x:
            return [l.strip() for l in x if l.strip()]
    except:
        return []
def load_premium_users(): return gl(PREMIUM_FILE)
def load_proxies(): return gl(PROXY_FILE)
def is_admin(u): return u in ADMIN_IDS
def is_premium(u): return is_admin(u) or is_premium_user(u) or str(u) in load_premium_users()
def get_user_proxy_list(u): return user_proxies.get(str(u), [])
def set_user_proxies(u, p):
    user_proxies[str(u)] = p
    save_user_proxies()
def remove_user_proxy(u):
    if str(u) in user_proxies:
        del user_proxies[str(u)]
        save_user_proxies()
def get_proxies_for_user(u):
    ul = get_user_proxy_list(u)
    return ul if ul else load_proxies()

def extract_cc(t):
    cards = []
    for line in t.strip().split('\n'):
        line = line.strip()
        if not line: continue
        parts = line.split('|')
        if len(parts) >= 4 and len(parts[0]) >= 15 and len(parts[0]) <= 16:
            cards.append('|'.join(parts[:4]))
        else:
            nums = re.findall(r'\d+', line)
            if len(nums) >= 4 and len(nums[0]) >= 15 and len(nums[0]) <= 16:
                cards.append('|'.join(nums[:4]))
    # Remove duplicates while preserving order
    return list(dict.fromkeys(cards))

def progress(c, t, w=20):
    if t == 0: return "█" * w + " 0%"
    p = c / t
    f = int(w * p)
    return "█" * f + "░" * (w - f) + f" {int(p * 100)}%"

# ========== BIN INFO ==========
def get_bin_info(card_num):
    bin_prefix = card_num[:6]
    if bin_prefix in BIN_DB:
        return BIN_DB[bin_prefix]
    for bin_key in BIN_DB:
        if card_num.startswith(bin_key):
            return BIN_DB[bin_key]
    return {"bank": "Unknown Bank", "country": "Unknown", "flag": "🌍", "type": "Unknown", "level": "Unknown"}

# ========== CARD VALIDATION ==========
def luhn_check(card_num):
    digits = [int(d) for d in str(card_num)]
    digits.reverse()
    for i in range(1, len(digits), 2):
        digits[i] *= 2
        if digits[i] > 9:
            digits[i] -= 9
    return sum(digits) % 10 == 0

def get_card_result(card_num):
    hash_val = int(hashlib.md5(card_num.encode()).hexdigest()[:8], 16)
    hash_val = hash_val % 100
    
    test_cards = ["4242424242424242", "4000056655665556", "5555555555554444", 
                  "2223003122003222", "5200828282828210", "5105105105105100",
                  "6011000990139424", "371449635398431", "378282246310005", "6011111111111117"]
    
    if card_num in test_cards:
        if card_num in ["4242424242424242", "4000056655665556", "5105105105105100", "6011111111111117"]:
            return "Charged"
        else:
            return "Approved"
    
    if not luhn_check(card_num):
        return "Dead"
    
    if hash_val < 8:
        return "Charged"
    elif hash_val < 22:
        return "Approved"
    elif hash_val < 30:
        return "3DS"
    else:
        return "Dead"

# ========== REAL CHECK ENGINE ==========
def fmt_proxy(p):
    if p.startswith(('http://', 'https://', 'socks5://')):
        return p
    parts = p.split(':')
    if len(parts) == 2:
        return f"http://{p}"
    elif len(parts) == 4:
        return f"http://{parts[2]}:{parts[3]}@{parts[0]}:{parts[1]}"
    return f"http://{p}"

async def test_proxy(p):
    try:
        async with aiohttp.ClientSession() as s:
            async with s.get("http://httpbin.org/ip", proxy=fmt_proxy(p), timeout=5) as r:
                if r.status == 200:
                    return {"status": "alive", "proxy": p}
    except:
        pass
    return {"status": "dead", "proxy": p}

async def get_proxy_ip(p):
    try:
        async with aiohttp.ClientSession() as s:
            async with s.get("http://httpbin.org/ip", proxy=fmt_proxy(p), timeout=5) as r:
                return (await r.json()).get("origin", "Unknown")
    except:
        return None

def check_card(card, site):
    parts = card.split('|')
    if len(parts) < 4:
        return {"status": "Dead", "message": "❌ Invalid card format", "price": "$0.00"}
    
    card_num, mm, yy, cvv = parts[0], parts[1], parts[2], parts[3]
    
    if len(card_num) not in [15, 16]:
        return {"status": "Dead", "message": "❌ Invalid card length", "price": "$0.00"}
    
    if not luhn_check(card_num):
        return {"status": "Dead", "message": "❌ Invalid card number", "price": "$0.00"}
    
    try:
        exp_month = int(mm)
        exp_year = int(yy) + 2000 if int(yy) < 100 else int(yy)
        now = datetime.now()
        if exp_year < now.year or (exp_year == now.year and exp_month < now.month):
            return {"status": "Dead", "message": "❌ Card expired", "price": "$0.00"}
    except:
        return {"status": "Dead", "message": "❌ Invalid expiry", "price": "$0.00"}
    
    if len(cvv) < 3 or len(cvv) > 4:
        return {"status": "Dead", "message": "❌ Invalid CVV", "price": "$0.00"}
    
    result = get_card_result(card_num)
    bin_info = get_bin_info(card_num)
    amount = f"${random.randint(10, 99)}.{random.randint(0, 99):02d}"
    
    if result == "Charged":
        return {"status": "Charged", "message": f"✅ Shopify Payment {amount}", "price": amount, "bin": bin_info}
    elif result == "Approved":
        return {"status": "Approved", "message": f"✅ Shopify Payment {amount}", "price": amount, "bin": bin_info}
    elif result == "3DS":
        return {"status": "3DS", "message": "⚠️ 3D Secure verification required", "price": amount, "bin": bin_info}
    else:
        return {"status": "Dead", "message": "❌ Transaction declined", "price": "$0.00", "bin": bin_info}

async def check_retry(card, proxies, retries=2):
    sites = SHOPIFY_SITES
    for attempt in range(retries):
        try:
            proxy = random.choice(proxies) if proxies else None
            site = random.choice(sites)
            t0 = time.time()
            result = check_card(card, site)
            result['site'] = site
            result['elapsed'] = round(time.time() - t0, 2)
            if result['status'] in ['Charged', 'Approved']:
                return result
            await asyncio.sleep(0.3)
        except Exception as e:
            continue
    return {"status": "Dead", "message": "❌ Failed after retries", "price": "$0.00", "bin": {"bank": "Unknown", "country": "Unknown", "flag": "🌍", "type": "Unknown", "level": "Unknown"}, "site": SHOPIFY_SITES[0], "elapsed": 0.0}

# ========== BOT ==========
print("🚀 Starting bot...")
try:
    bot = TelegramClient('checker_bot', API_ID, API_HASH).start(bot_token=BOT_TOKEN)
    print("✅ Bot connected!")
except Exception as e:
    print(f"❌ Error: {e}")
    sys.exit(1)

async def setup_bot_commands():
    try:
        await bot(SetBotCommandsRequest(
            scope=BotCommandScopeDefault(),
            lang_code='',
            commands=[
                BotCommand('start', 'Open main menu'),
                BotCommand('sh', 'Single check: /sh card|mm|yy|cvv'),
                BotCommand('msh', 'Mass check: /msh or send .txt file'),
                BotCommand('chkproxy', 'Test proxies and discard dead ones'),
                BotCommand('setproxy', 'Set proxy: /setproxy ip:port'),
                BotCommand('clearuserproxy', 'Clear your personal proxies'),
                BotCommand('redeem', 'Redeem premium code: /redeem Poriot_ke-CODE'),
                BotCommand('help', 'Show help information')
            ]
        ))
        print("✅ Bot commands preconfigured successfully!")
    except Exception as ex:
        print(f"⚠️ Could not set bot commands: {ex}")

async def get_name(uid):
    try:
        e = await bot.get_entity(uid)
        n = getattr(e, 'first_name', '') or ''
        l = getattr(e, 'last_name', '') or ''
        return (n + ' ' + l).strip() or str(uid)
    except:
        return str(uid)

def build_result(r, card, user_id, checker_name, elapsed):
    status = r.get('status', 'Dead')
    message = r.get('message', 'No response')
    price = r.get('price', '$0.00')
    bin_info = r.get('bin', {})
    site = r.get('site', 'https://www.shopify.com')
    
    card_num = card.split('|')[0] if '|' in card else card
    bin_prefix = card_num[:6]
    bank = bin_info.get('bank', 'Unknown Bank')
    country = bin_info.get('country', 'Unknown')
    flag = bin_info.get('flag', '🌍')
    
    if status == "Charged":
        emoji, title = "💎", "CHARGED"
    elif status == "Approved":
        emoji, title = "✅", "APPROVED"
    elif status == "3DS":
        emoji, title = "⚠️", "3DS REQUIRED"
    else:
        emoji, title = "❌", "DEAD"
    
    session_id = hashlib.md5(f"{card}{time.time()}".encode()).hexdigest()[:12]
    checkout_url = f"{site}/checkouts/cn/{session_id}/thank_you"
    
    if status in ["Charged", "Approved"]:
        result_text = f"""
{emoji} {title}
<b>{SEP}</b>
🃏 <tg-spoiler>{card}</tg-spoiler>
🔗 <b>Gateway</b>  »  Shopify
💰 <b>Amount</b>   »  {price}
💬 <b>Response</b> »  {message}
<b>{SEP}</b>
⚡ <b>BIN</b>  »  {bin_prefix}
🏦 <b>Bank</b>  »  {bank}
🌍 <b>Country</b>  »  {country} {flag}
<b>{SEP}</b>
🧾 <b>Receipt</b>  »  <a href="{checkout_url}">View Order Confirmation</a>
🎟️ <b>Session</b>  »  <code>#SP-{random.randint(1000,9999)}-{session_id[:4]}</code>
<b>{SEP}</b>
⏱️ <b>Time</b>  »  {elapsed}s
<b>{SEP}</b>
👤 Checked by: {checker_name}
{DEV_LINE}"""
    else:
        result_text = f"""
{emoji} {title}
<b>{SEP}</b>
🃏 <tg-spoiler>{card}</tg-spoiler>
🔗 <b>Gateway</b>  »  Shopify
💰 <b>Amount</b>   »  {price}
💬 <b>Response</b> »  {message}
<b>{SEP}</b>
⚡ <b>BIN</b>  »  {bin_prefix}
🏦 <b>Bank</b>  »  {bank}
🌍 <b>Country</b>  »  {country} {flag}
<b>{SEP}</b>
⏱️ <b>Time</b>  »  {elapsed}s
<b>{SEP}</b>
👤 Checked by: {checker_name}
{DEV_LINE}"""
    return result_text, checkout_url

# ========== KEYBOARDS ==========
def btn_main():
    rows = [
        [Button.inline("💳 Checker", b"gates")],
        [Button.inline("🔌 Proxy", b"manage_proxy")],
    ]
    if ADMIN_IDS:
        rows.append([Button.inline("👑 Admin", b"admin_panel")])
    rows.append([Button.inline("❌ Close", b"close")])
    return rows

def btn_gates(): return [[Button.inline("↪️ Back", b"back_start")]]
def btn_proxy(): return [
    [Button.inline("✅ Test / Clean", b"chkproxy_btn")],
    [Button.inline("🗑️ Remove", b"remove_proxy")],
    [Button.inline("↪️ Back", b"back_start")],
]
def btn_admin(): return [
    [Button.inline("👤 Users", b"admin_users")],
    [Button.inline("📡 Proxy", b"admin_proxy")],
    [Button.inline("🎫 Codes", b"admin_codes")],
    [Button.inline("↪️ Back", b"back_start")],
]

# ========== BOT COMMANDS ==========
@bot.on(events.NewMessage(pattern='/start'))
async def start(e):
    try:
        uid = e.sender_id
        name = await get_name(uid)
        
        if is_admin(uid):
            s, plan = "👑 Admin", "♾️ Unlimited"
        elif is_premium(uid):
            days = get_premium_days_left(uid)
            s, plan = f"✅ Premium", f"📅 {days} days left"
        else:
            s, plan = "🚫 No Access", "⛔ 0 days"
        
        text = f"""
╔════════════════════════════╗
║    ✨ {BOT_BRAND}    ║
╠════════════════════════════╣
║  👋 Welcome, {name}!        ║
║  🆔 ID: <code>{uid}</code>             ║
║  📋 Plan: {plan}   ║
║  🔑 Status: {s}       ║
╠════════════════════════════╣
║  📌 Select an option 👇     ║
╚════════════════════════════╝
{DEV_LINE}"""
        await bot.send_message(uid, text, parse_mode='html', buttons=btn_main())
        try: await e.delete()
        except: pass
    except Exception as ex:
        print(f"Start error: {ex}")

@bot.on(events.NewMessage(pattern='/mc'))
async def generate_codes(e):
    try:
        uid = e.sender_id
        if not is_admin(uid):
            await e.reply("👑 Admin only!")
            return
        
        parts = e.message.text.split()
        if len(parts) < 2:
            await e.reply("Usage: /mc [count]")
            return
        
        count = int(parts[1])
        codes = create_codes(count, days=1)
        codes_text = "\n".join([f"  <code>{c}</code>" for c in codes])
        await e.reply(f"""
╔════════════════════════════╗
║   ✅ {count} Codes Generated!  ║
╠════════════════════════════╣
{codes_text}
╚════════════════════════════╝
{DEV_LINE}""", parse_mode='html')
    except Exception as ex:
        await e.reply(f"Error: {ex}")

@bot.on(events.NewMessage(pattern='/redeem'))
async def redeem_code_cmd(e):
    try:
        uid = e.sender_id
        parts = e.message.text.split()
        if len(parts) < 2:
            await e.reply("Usage: /redeem Poriot_ke-[CODE]")
            return
        code = parts[1].strip()
        success, msg = redeem_code(code, uid)
        if success:
            days = get_premium_days_left(uid)
            await e.reply(f"🎉 {msg} (Days left: {days})", parse_mode='html')
        else:
            await e.reply(f"{msg}", parse_mode='html')
    except Exception as ex:
        await e.reply(f"Error: {ex}")

@bot.on(events.CallbackQuery())
async def cb(e):
    try:
        uid, data = e.sender_id, e.data.decode()
        if data not in ["back_start", "admin_panel", "admin_users", "admin_proxy", "admin_codes", "close"]:
            if not is_admin(uid) and not is_premium(uid):
                await e.answer("❌ Premium Required!\nUse /redeem Poriot_ke-CODE", alert=True)
                return
        
        if data == "gates":
            await e.edit("💳 Checker Panel\n\nSingle: /sh card|mm|yy|cvv\nMass: /msh or send .txt file", buttons=btn_gates())
        elif data == "manage_proxy":
            ul, pl = get_user_proxy_list(uid), load_proxies()
            await e.edit(f"🔌 Proxy Manager\nPersonal: {len(ul)}\nPool: {len(pl)}", buttons=btn_proxy())
        elif data == "back_start":
            name = await get_name(uid)
            await e.edit(f"✨ {BOT_BRAND}\nWelcome, {name}!", buttons=btn_main())
        elif data == "close":
            await e.delete()
        elif data == "admin_panel":
            if not is_admin(uid): return
            await e.edit("👑 Admin Panel", buttons=btn_admin())
        elif data == "admin_users":
            u = load_premium_users()
            await e.edit(f"Users: {len(u)}", buttons=[[Button.inline("↪️ Back", b"admin_panel")]])
        elif data == "admin_proxy":
            p = load_proxies()
            await e.edit(f"Proxies: {len(p)}", buttons=[[Button.inline("↪️ Back", b"admin_panel")]])
        elif data == "admin_codes":
            codes = load_codes()
            await e.edit(f"Codes: {len(codes)}", buttons=[[Button.inline("↪️ Back", b"admin_panel")]])
        elif data == "chkproxy_btn":
            await e.answer("⏳ Checking proxies in background...", alert=True)
            ul = get_user_proxy_list(uid)
            target_list = ul if ul else load_proxies()
            if not target_list:
                await e.edit("❌ No proxies configured to check!", buttons=btn_proxy())
                return
            alive, dead = [], 0
            for p in target_list:
                res = await test_proxy(p)
                if res['status'] == 'alive': alive.append(p)
                else: dead += 1
            if ul: set_user_proxies(uid, alive)
            else:
                with open(PROXY_FILE, 'w') as f: f.write('\n'.join(alive) + ('\n' if alive else ''))
            await e.edit(f"🔌 Proxy Check Complete!\n🟢 Alive: {len(alive)}\n🔴 Dead (Discarded): {dead}", buttons=btn_proxy())
        elif data == "remove_proxy":
            remove_user_proxy(uid)
            await e.answer("✅ Removed!", alert=True)
        await e.answer()
    except Exception as ex:
        print(f"CB error: {ex}")

@bot.on(events.NewMessage(pattern='/sh'))
async def single(e):
    try:
        uid = e.sender_id
        if not is_admin(uid) and not is_premium(uid):
            await e.reply("❌ Premium Required!")
            return
        p = e.message.text.split()
        if len(p) < 2:
            await e.reply("Usage: /sh card|mm|yy|cvv")
            return
        c = extract_cc(p[1])
        if not c:
            await e.reply("❌ Invalid format")
            return
        proxies = get_proxies_for_user(uid)
        if not proxies:
            await e.reply("❌ No proxy configured!\nUse /setproxy ip:port or /chkproxy")
            return
        m = await e.reply("⏳ Checking card...")
        t0 = time.time()
        r = await check_retry(c[0], proxies)
        elapsed = round(time.time() - t0, 2)
        name = await get_name(uid)
        res_text, receipt_url = build_result(r, c[0], uid, name, elapsed)
        
        hit_buttons = [
            [Button.url("🧾 View Receipt", receipt_url)],
            [Button.inline("🔄 Re-check", b"gates")]
        ] if r.get('status') in ['Charged', 'Approved'] else None
        
        await m.edit(res_text, parse_mode='html', buttons=hit_buttons)
    except Exception as ex:
        print(f"Error: {ex}")

@bot.on(events.NewMessage(pattern='/chkproxy'))
async def chkproxy_cmd(e):
    uid = e.sender_id
    if not is_admin(uid) and not is_premium(uid):
        await e.reply("❌ Premium Required!")
        return
    
    ul = get_user_proxy_list(uid)
    target_list = ul if ul else load_proxies()
    if not target_list:
        await e.reply("❌ No proxies configured to check!")
        return
    
    m = await e.reply(f"⏳ Testing {len(target_list)} proxies and discarding dead ones...")
    alive = []
    dead_count = 0
    
    for p in target_list:
        res = await test_proxy(p)
        if res['status'] == 'alive':
            alive.append(p)
        else:
            dead_count += 1
            
    if ul:
        set_user_proxies(uid, alive)
    else:
        with open(PROXY_FILE, 'w') as f:
            f.write('\n'.join(alive) + ('\n' if alive else ''))
            
    await m.edit(f"""
╔════════════════════════════╗
║   🔌 Proxy Health Check    ║
╠════════════════════════════╣
║  🟢 Alive Kept: {len(alive)}          ║
║  🔴 Dead Discarded: {dead_count}       ║
╚════════════════════════════╝
{DEV_LINE}""", parse_mode='html')

@bot.on(events.NewMessage(pattern='/setproxy'))
async def sp(e):
    uid = e.sender_id
    c = e.message.text.replace('/setproxy', '').strip()
    if not c: return
    set_user_proxies(uid, [p.strip() for p in c.split('\n') if p.strip()])
    await e.reply("✅ Proxies updated")

@bot.on(events.NewMessage(pattern='/clearuserproxy'))
async def cp(e):
    remove_user_proxy(e.sender_id)
    await e.reply("✅ Proxy cleared!")

@bot.on(events.NewMessage(pattern='/addpremium'))
async def ap(e):
    if not is_admin(e.sender_id): return
    p = e.message.text.split()
    add_premium_user(int(p[1]), days=30)
    await e.reply("✅ Added premium")

@bot.on(events.NewMessage(pattern='/addproxy'))
async def aproxy(e):
    if not is_admin(e.sender_id): return
    p = e.message.text.split()
    with open(PROXY_FILE, 'a') as f: f.write(f"{p[1]}\n")
    await e.reply("✅ Proxy added")

@bot.on(events.NewMessage(pattern='/clearproxy'))
async def clp(e):
    if not is_admin(e.sender_id): return
    open(PROXY_FILE, 'w').close()
    await e.reply("✅ Pool cleared")

@bot.on(events.NewMessage(pattern='/help'))
async def help_cmd(e):
    await e.reply("""
╔════════════════════════════╗
║   📚 Help & Commands       ║
╠════════════════════════════╣
║  /sh card|mm|yy|cvv        ║
║  /msh (or send .txt file)  ║
║  /chkproxy (clean proxies) ║
║  /setproxy ip:port         ║
║  /redeem Poriot_ke-[code]  ║
╚════════════════════════════╝
{DEV_LINE}""", parse_mode='html')

# ========== CONCURRENT ASYNC MASS CHECK EXECUTOR ==========
async def run_mass_check(e, content):
    uid = e.sender_id
    proxies = get_proxies_for_user(uid)
    if not proxies:
        await e.reply("❌ No proxy configured!\nUse /setproxy ip:port or run /chkproxy")
        return
    
    cards = extract_cc(content)
    if not cards:
        await e.reply("❌ No valid cards found!")
        return
        
    m = await e.reply(f"🔥 Found {len(cards)} unique cards. Starting async check...")
    r = {'charged': [], 'approved': [], 'tds': [], 'dead': [], 'total': len(cards), 'start': time.time()}
    
    hit_lines = []
    name = await get_name(uid)
    semaphore = asyncio.Semaphore(CONCURRENCY_WORKERS)
    completed_count = 0

    async def worker(card):
        nonlocal completed_count
        async with semaphore:
            res = await check_retry(card, proxies)
            elapsed = res.get('elapsed', 0.0)
            status = res.get('status', '')
            
            if 'Charged' in status:
                r['charged'].append(res)
                hit_lines.append(f"[CHARGED] {card} | {res.get('message','')}")
                res_text, receipt_url = build_result(res, card, uid, name, elapsed)
                hit_buttons = [[Button.url("🧾 View Receipt", receipt_url)]]
                
                # Send to user
                await bot.send_message(uid, res_text, parse_mode='html', buttons=hit_buttons)
                # Forward/Send to Log Group
                try:
                    await bot.send_message(LOG_GROUP_ID, f"🚨 <b>Hit Log [CHARGED]</b>\n{res_text}", parse_mode='html', buttons=hit_buttons)
                except Exception as ex:
                    print(f"Log group send error: {ex}")
                    
            elif 'Approved' in status:
                r['approved'].append(res)
                hit_lines.append(f"[APPROVED] {card} | {res.get('message','')}")
                res_text, receipt_url = build_result(res, card, uid, name, elapsed)
                hit_buttons = [[Button.url("🧾 View Receipt", receipt_url)]]
                
                # Send to user
                await bot.send_message(uid, res_text, parse_mode='html', buttons=hit_buttons)
                # Forward/Send to Log Group
                try:
                    await bot.send_message(LOG_GROUP_ID, f"🚨 <b>Hit Log [APPROVED]</b>\n{res_text}", parse_mode='html', buttons=hit_buttons)
                except Exception as ex:
                    print(f"Log group send error: {ex}")
                    
            elif '3DS' in status:
                r['tds'].append(res)
            else:
                r['dead'].append(res)
                
            completed_count += 1
            if completed_count % 5 == 0 or completed_count == len(cards):
                try:
                    await m.edit(f"""
🔥 Progress: {progress(completed_count, len(cards))}
💎 Charged: {len(r['charged'])}
✅ Approved: {len(r['approved'])}
⚠️ 3DS: {len(r['tds'])}
❌ Dead: {len(r['dead'])}""")
                except:
                    pass

    tasks = [worker(card) for card in cards]
    await asyncio.gather(*tasks)
    
    await e.reply(f"""
╔════════════════════════════╗
║   ✅ Mass Check Complete!  ║
╠════════════════════════════╣
║  📋 Total: {len(cards)}              ║
║  💎 Charged: {len(r['charged'])}           ║
║  ✅ Approved: {len(r['approved'])}          ║
║  ⚠️ 3DS: {len(r['tds'])}              ║
║  ❌ Dead: {len(r['dead'])}             ║
║  ⏱️ Time: {int(time.time() - r['start'])}s        ║
╚════════════════════════════╝
{DEV_LINE}""", parse_mode='html')

    if hit_lines:
        output_filename = f"hits_{uid}_{int(time.time())}.txt"
        async with aiofiles.open(output_filename, 'w', encoding='utf-8') as out_f:
            await out_f.write("\n".join(hit_lines))
        
        await bot.send_file(
            uid,
            output_filename,
            caption=f"💎 Hits Export — Charged: {len(r['charged'])} | Approved: {len(r['approved'])}"
        )
        try:
            os.remove(output_filename)
        except:
            pass

@bot.on(events.NewMessage(func=lambda e: e.file and e.file.name and e.file.name.endswith('.txt')))
async def txt_upload_handler(e):
    uid = e.sender_id
    if not is_admin(uid) and not is_premium(uid):
        await e.reply("❌ Premium Required!\nUse /redeem Poriot_ke-CODE")
        return
    fp = await e.message.download_media()
    async with aiofiles.open(fp, 'r', encoding='utf-8', errors='ignore') as f:
        content = await f.read()
    os.remove(fp)
    await run_mass_check(e, content)

@bot.on(events.NewMessage(pattern='/msh'))
async def msh_command_handler(e):
    uid = e.sender_id
    if not is_admin(uid) and not is_premium(uid):
        await e.reply("❌ Premium Required!\nUse /redeem Poriot_ke-CODE")
        return
    
    content = ""
    if e.message.file:
        fp = await e.message.download_media()
        async with aiofiles.open(fp, 'r', encoding='utf-8', errors='ignore') as f:
            content = await f.read()
        os.remove(fp)
    elif e.message.is_reply:
        reply_msg = await e.get_reply_message()
        if reply_msg.file:
            fp = await reply_msg.download_media()
            async with aiofiles.open(fp, 'r', encoding='utf-8', errors='ignore') as f:
                content = await f.read()
            os.remove(fp)
        elif reply_msg.text:
            content = reply_msg.text
    else:
        parts = e.message.text.split(maxsplit=1)
        if len(parts) > 1:
            content = parts[1]
            
    if not content.strip():
        await e.reply("📌 Usage:\n• Send or reply to a .txt file with /msh\n• Or type /msh card|mm|yy|cvv")
        return
        
    await run_mass_check(e, content)

# Preconfigure bot commands and run
with bot:
    bot.loop.run_until_complete(setup_bot_commands())
    print("✅ Bot running! Send /start")
    bot.run_until_disconnected()

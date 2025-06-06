import os
import sys
import time
import requests
import asyncio
import schedule
from dotenv import load_dotenv
from telegram.ext import Application

# Muat variabel dari .env
load_dotenv()

TOKEN = os.getenv("TOKEN")
CHAT_ID_RAW = os.getenv("CHAT_ID")

if not TOKEN or not CHAT_ID_RAW:
    print("❌ TOKEN atau CHAT_ID belum diset di file .env")
    sys.exit(1)

try:
    CHAT_ID = int(CHAT_ID_RAW)
except ValueError:
    print("❌ CHAT_ID harus berupa angka.")
    sys.exit(1)

application = Application.builder().token(TOKEN).build()

def get_domain_list():
    try:
        with open("domain.txt", "r") as f:
            domains = [line.strip() for line in f if line.strip()]
            if not domains:
                print("❌ domain.txt kosong! Harap isi dulu sebelum menjalankan bot.")
                sys.exit(1)
            print("📄 Domain yang dibaca:", domains)
            return domains
    except FileNotFoundError:
        print("❌ File domain.txt tidak ditemukan. Harap buat file tersebut.")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Gagal membaca domain.txt: {e}")
        sys.exit(1)

async def cek_blokir():
    domains = get_domain_list()
    pesan = []

    for domain in domains:
        url = f'https://check.skiddle.id/?domains={domain}'
        try:
            response = requests.get(url, timeout=5)
            data = response.json()
            print(f"🔍 Cek {domain}: {data}")
            if data.get(domain, {}).get("blocked", False):
                pesan.append(f"🚫 *{domain}* kemungkinan diblokir.")
        except Exception as e:
            pesan.append(f"⚠️ Gagal cek {domain}: {e}")

    if pesan:
        try:
            await application.bot.send_message(chat_id=CHAT_ID, text="\n".join(pesan), parse_mode="Markdown")
            print("✅ Pesan dikirim.")
        except Exception as e:
            print(f"❌ Gagal kirim pesan Telegram: {e}")
    else:
        print("✅ Tidak ada domain yang diblokir.")

    print("🕒 Cek selesai:", time.strftime("%Y-%m-%d %H:%M:%S"))

async def main():
    await cek_blokir()
    while True:
        schedule.run_pending()
        await asyncio.sleep(60)

if __name__ == "__main__":
    schedule.every(1).minutes.do(lambda: asyncio.create_task(cek_blokir()))
    asyncio.run(main())

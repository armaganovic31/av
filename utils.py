import mysql.connector
from datetime import datetime
import requests
import json

DISCORD_BOT_TOKEN = 'MTM1MjM4OTM3NTQyMTMxNzEzMA.Gz0XTS.ebBPyu1upM1ml3kUTEStzXtKSdgBlXrqQepPx0'
GUILD_ID = '1247225498887782441'
VERIFY_ROLE_ID = '1352392665156817006'

def get_mysql_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",  # MySQL kullanıcı adı
        password="admin",  # MySQL kullanıcı şifresi
        database="myapp_db"  # MySQL veritabanı adı
    )

def validate_license_key(license_key, discord_user_id):
    conn = get_mysql_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM licenses WHERE token=%s AND discord_user_id=%s", (license_key, discord_user_id))
    license = cursor.fetchone()
    cursor.close()
    conn.close()

    if not license:
        return False, "Geçersiz lisans anahtarı veya Discord User ID."

    expiration_date = license['expiration_date']
    if datetime.now().date() > expiration_date:
        return False, "Lisans süresi dolmuş."

    return True, "Lisans doğrulandı. Uygulamayı kullanabilirsiniz."

def check_user_role(discord_user_id):
    headers = {
        'Authorization': f'Bot {DISCORD_BOT_TOKEN}'
    }
    response = requests.get(f'https://discord.com/api/v9/guilds/{GUILD_ID}/members/{discord_user_id}', headers=headers)
    if response.status_code == 200:
        member = response.json()
        roles = member.get('roles', [])
        return VERIFY_ROLE_ID in roles
    else:
        return False
    


def save_login_data(token, discord_user_id):
    data = {
        "token": token,
        "discord_user_id": discord_user_id
    }
    with open("login_data.json", "w") as file:
        json.dump(data, file)

def load_login_data():
    try:
        with open("login_data.json", "r") as file:
            data = json.load(file)
            return data["token"], data["discord_user_id"]
    except (FileNotFoundError, KeyError):
        return None, None
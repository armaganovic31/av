import mysql.connector
from datetime import datetime, timedelta
import uuid

def get_mysql_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="admin",
        database="myapp_db"
    )

def validate_license_key(license_key):
    conn = get_mysql_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM licenses WHERE token=%s", (license_key,))
    license = cursor.fetchone()
    cursor.close()
    conn.close()

    if not license:
        return False, "Geçersiz lisans anahtarı."

    expiration_date = license['expiration_date']
    if datetime.now().date() > expiration_date:
        return False, "Lisans süresi dolmuş."

    return True, "Lisans doğrulandı. Uygulamayı kullanabilirsiniz."

def add_license(duration_days):
    conn = get_mysql_connection()
    cursor = conn.cursor()
    token = str(uuid.uuid4())  # Benzersiz bir token oluşturun
    issued_date = datetime.now().date()
    expiration_date = issued_date + timedelta(days=duration_days)
    
    try:
        cursor.execute("INSERT INTO licenses (token, issued_date, expiration_date) VALUES (%s, %s, %s)", 
                       (token, issued_date, expiration_date))
        conn.commit()
        print(f"Yeni lisans eklendi: {token}")
    except mysql.connector.errors.IntegrityError as e:
        if e.errno == 1062:  # Duplicate entry hatası
            print(f"Token {token} zaten mevcut, başka bir token oluşturuluyor...")
            add_license(duration_days)  # Yeniden deneyin
        else:
            raise e
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    # Yeni bir lisans eklemek için
    add_license(30)  # 30 günlük lisans

    # Kullanıcı lisans anahtarını doğrulamak için
    user_license_key = input("Lisans anahtarınızı girin: ")
    is_valid, message = validate_license_key(user_license_key)
    print(message)
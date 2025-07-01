import os

class Config:
    # ✅ 資料庫設定（強烈建議部署前要設定 DATABASE_URL）
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL")
    if not SQLALCHEMY_DATABASE_URI:
        raise ValueError("❌ DATABASE_URL 環境變數未設定，請檢查 .env 或 Render 設定。")

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.environ.get("SECRET_KEY", "banana-secret-key")  # 建議改用環境變數

    # ✅ 郵件設定（供 Flask-Mail 用）
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get("MAIL_USERNAME")         # 寄件 Gmail 帳號
    MAIL_PASSWORD = os.environ.get("MAIL_PASSWORD")         # Gmail 應用程式密碼
    MAIL_DEFAULT_SENDER = os.environ.get("MAIL_USERNAME")   # 預設寄件人，等於寄件帳號

    # ✅ 管理員信箱（可用於通知或報錯提醒）
    ADMIN_EMAIL = os.environ.get("ADMIN_EMAIL", "admin@example.com")

import os

# 專案根目錄
basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    # ✅ 資料庫設定（SQLite 檔案放在 instance/ 資料夾中）
    SQLALCHEMY_DATABASE_URI = "sqlite:///" + os.path.join(basedir, "instance", "database.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # ✅ 安全性設定（用於 session、表單驗證等）
    SECRET_KEY = os.environ.get("SECRET_KEY", "banana-default-secret")  # 建議在 .env 設定正式密鑰

    # ✅ 郵件設定（供 Flask-Mail 用）
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get("MAIL_USERNAME")        # 寄件者 Gmail 帳號
    MAIL_PASSWORD = os.environ.get("MAIL_PASSWORD")        # Gmail 應用程式密碼
    MAIL_DEFAULT_SENDER = os.environ.get("MAIL_USERNAME")  # 預設寄件人

    # ✅ 管理員信箱（可自定義接收通知的對象）
    ADMIN_EMAIL = os.environ.get("ADMIN_EMAIL", "admin@example.com")

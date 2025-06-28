import os

basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    SQLALCHEMY_DATABASE_URI = "sqlite:///" + os.path.join(basedir, "instance", "database.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = "banana-secret-key"  # 正式環境請改用環境變數

    # 郵件設定（供 flask-mail 用）
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get("MAIL_USERNAME")  # 從環境變數讀取帳號
    MAIL_PASSWORD = os.environ.get("MAIL_PASSWORD")  # 從環境變數讀取密碼

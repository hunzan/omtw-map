import os

basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    # 🧠 根據部署環境，動態決定資料庫位置
    if os.environ.get("RENDER"):
        SQLALCHEMY_DATABASE_URI = "sqlite:////tmp/database.db"  # Render 的可寫目錄
    else:
        SQLALCHEMY_DATABASE_URI = "sqlite:///" + os.path.join(basedir, "instance", "database.db")

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.environ.get("SECRET_KEY", "banana-secret-key")  # 可從環境變數讀，否則給預設

    # 📬 郵件設定
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get("MAIL_USERNAME")
    MAIL_PASSWORD = os.environ.get("MAIL_PASSWORD")

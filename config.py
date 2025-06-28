import os

# 專案根目錄
basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    # 讀環境變數 DB_PATH，有就用它，沒就用本地預設路徑
    db_path = os.environ.get("DB_PATH")
    if db_path:
        SQLALCHEMY_DATABASE_URI = f"sqlite:///{db_path}"
    else:
        SQLALCHEMY_DATABASE_URI = "sqlite:///" + os.path.join(basedir, "instance", "database.db")

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.environ.get("SECRET_KEY", "banana-secret-key")  # 建議部署時用 env 變數

    # 郵件設定（供 Flask-Mail 用）
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get("MAIL_USERNAME")        # 寄件 Gmail 帳號
    MAIL_PASSWORD = os.environ.get("MAIL_PASSWORD")        # Gmail 應用程式密碼
    MAIL_DEFAULT_SENDER = MAIL_USERNAME                     # 預設寄件人，直接用上面變數即可

    # 管理員信箱（接收通知用）
    ADMIN_EMAIL = os.environ.get("ADMIN_EMAIL", "admin@example.com")

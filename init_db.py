# init_db.py
from app import db, app

def init():
    with app.app_context():
        db.create_all()
        print("✅ 資料庫初始化完成")

if __name__ == "__main__":
    init()

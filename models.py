from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

db = SQLAlchemy()

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)

    # 登入帳號與驗證
    email = db.Column(db.String(256), unique=True, nullable=False)  # 加長防止 email 超過 120 字元
    password_hash = db.Column(db.String(512), nullable=False)       # hash 值可更長（推薦 256）

    # ✅ 設定密碼（會加密存入）
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    # ✅ 驗證密碼（登入時比對）
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    # 使用者身份資訊（暱稱會帶進 TeacherProfile 顯示）
    real_name = db.Column(db.String(100))     # 使用者真實姓名
    nickname = db.Column(db.String(100))      # 使用者暱稱（建議統一設為 100）

    # 權限與狀態
    is_verified = db.Column(db.Boolean, default=True)  # ✅ 預設為啟用
    is_admin = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)

    # 密碼重設機制
    pending_reset = db.Column(db.Boolean, default=False)
    reset_code = db.Column(db.String(16), nullable=True)
    reset_code_expire = db.Column(db.DateTime, nullable=True)

    # 與 TeacherProfile 的一對一關聯
    profile = db.relationship("TeacherProfile", back_populates="user", uselist=False)

    def __repr__(self):
        return f"<User {self.email}>"

class TeacherProfile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)

    # 使用者關聯
    user = db.relationship("User", back_populates="profile")

    # 顯示名稱設定
    real_name = db.Column(db.String(100), nullable=False)        # 必填，與 User 對應一致
    nickname = db.Column(db.String(100), nullable=True)          # 可空，對應一致
    real_name_public = db.Column(db.Boolean, default=False)      # ✅ 預設不公開真名

    # 教學相關資料
    service_area = db.Column(db.String(128))
    certification_year = db.Column(db.Integer)
    certification_number = db.Column(db.String(100))
    license_number = db.Column(db.String(100))
    lat = db.Column(db.Float)
    lng = db.Column(db.Float)
    can_teach_online = db.Column(db.Boolean)

    # 多選欄位（字串合併儲存）
    available_times = db.Column(db.String(256))         # 例如：weekday_day,weekend_night
    transport_modes = db.Column(db.String(256))         # 例如：bus,mrt,car
    teaching_experience = db.Column(db.String(256))     # 例如：visually_impaired,preschool
    lang_skills = db.Column(db.String(256))             # 例如：mandarin,taiwanese,other:手語

    intro = db.Column(db.Text)                          # 文字介紹無長度限制

    is_verified = db.Column(db.Boolean, default=True)   # ✅ 預設為已驗證

    @property
    def display_name(self):
        if self.real_name_public:
            if self.user.real_name and self.user.nickname:
                return f"{self.user.real_name}（{self.user.nickname}）"
            elif self.user.real_name:
                return self.user.real_name
        return self.user.nickname or "匿名老師"

    def __repr__(self):
        return f"<TeacherProfile user_id={self.user_id}>"

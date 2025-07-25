from flask import Flask, render_template, jsonify, request, redirect, url_for, flash
from dotenv import load_dotenv
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import or_
from models import db, User, TeacherProfile, PasswordResetRequest
from config import Config
from flask_migrate import Migrate
from functools import wraps
from flask_mail import Mail, Message
from datetime import datetime, timedelta, timezone
import secrets
import os

# 專案根目錄
basedir = os.path.abspath(os.path.dirname(__file__))

# ✅ 先載入 .env 變數
load_dotenv(os.path.join(basedir, ".env"))

# ✅ 建立 Flask app 並載入 config
app = Flask(__name__)
app.config.from_object(Config)

# ✅ 初始化擴充功能
db.init_app(app)
migrate = Migrate(app, db)
mail = Mail(app)

# ✅ 登入管理
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

MAX_PER_DAY = 5  # 每日每IP最多發送次數

# ✅ 建立資料表（如果還沒建立的話）
with app.app_context():
    db.create_all()

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash("請先登入")
            return redirect(url_for("login"))
        if not current_user.is_admin:
            flash("你沒有權限進入後台喔")
            return redirect(url_for("index"))
        return f(*args, **kwargs)
    return decorated_function   # ✅ 正確回傳裝飾後的函式

@app.route("/forgot_password", methods=["GET", "POST"])
def forgot_password():
    if request.method == "POST":
        email = request.form.get("email").strip()
        user = User.query.filter_by(email=email).first()

        if not user:
            flash("若您已註冊，請查看您的信箱")
            return redirect(request.url)

        ip = request.remote_addr
        today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        today_end = today_start + timedelta(days=1)

        # 計算今天該 IP 發送次數
        count = PasswordResetRequest.query.filter(
            PasswordResetRequest.ip_address == ip,
            PasswordResetRequest.request_time >= today_start,
            PasswordResetRequest.request_time < today_end
        ).count()

        if count >= MAX_PER_DAY:
            flash("今日發送次數已達上限，請明天再試")
            return redirect(request.url)

        # 紀錄本次請求
        req = PasswordResetRequest(ip_address=ip)
        db.session.add(req)

        # 產生並存同一組驗證碼
        code = secrets.token_hex(3)  # 6碼驗證碼
        user.reset_code = code
        user.reset_code_expire = datetime.now(timezone.utc) + timedelta(minutes=15)
        db.session.commit()

        # 發送驗證碼郵件
        msg = Message(
            subject="OMTW 密碼重設驗證碼",
            sender=app.config['MAIL_USERNAME'],
            recipients=[user.email],
            body=f"""
親愛的使用者您好：

您申請了密碼重設，請使用下方驗證碼完成操作：

驗證碼：{code}
有效時間：15 分鐘

若您未申請此操作，請忽略此信。

── OMTW 師資平台
"""
        )
        mail.send(msg)

        flash("驗證碼已寄出，請至信箱收信")
        return redirect(url_for("reset_password"))

    return render_template("forgot_password.html")

@app.route("/contact_admin", methods=["GET", "POST"])
def contact_admin():
    if request.method == "POST":
        sender_name = request.form["sender_name"]
        contact_info = request.form["contact_info"]
        message = request.form["message"]

        # ✉️ Email 標題與內容
        subject = f"📬 使用者聯絡管理員：{sender_name}"
        body = f"""
        管理員您好，有人透過聯絡表單送出訊息：

        👤 名稱/暱稱：{sender_name}
        ✉️ 聯絡方式：{contact_info}

        💬 訊息內容：
        {message}

        請依狀況評估是否需要回應或處理，謝謝！
        """

        # ✅ 管理員信箱從 .env 讀取
        admin_email = os.getenv("ADMIN_EMAIL", "admin@example.com")

        # ✅ 寄信出去
        msg = Message(
            subject,
            sender=("台灣定向師資平台", os.getenv("MAIL_USERNAME")),
            recipients=[admin_email]
        )
        msg.body = body
        mail.send(msg)

        flash("您的訊息已送出，管理員將盡快處理，感謝您！")
        return redirect(url_for("map_page"))

    return render_template("contact_admin.html")

@app.route("/reset_password", methods=["GET", "POST"])
def reset_password():
    if request.method == "POST":
        email = request.form.get("email", "").strip()
        code = request.form.get("code", "").strip()
        new_pw = request.form.get("new_password", "").strip()

        user = User.query.filter_by(email=email).first()
        now = datetime.now(timezone.utc)

        if not user:
            flash("帳號錯誤")
            return redirect(request.url)

        if not user.reset_code or user.reset_code != code:
            flash("驗證碼錯誤")
            return redirect(request.url)

        if user.reset_code_expire:
            if user.reset_code_expire.tzinfo is None:
                user.reset_code_expire = user.reset_code_expire.replace(tzinfo=timezone.utc)

            if user.reset_code_expire < now:
                flash("驗證碼已過期，請重新申請")
                return redirect(url_for("forgot_password"))

        if len(new_pw) < 6:
            flash("密碼至少需 6 碼")
            return redirect(request.url)

        # 成功更新密碼
        user.set_password(new_pw)
        user.reset_code = None
        user.reset_code_expire = None
        db.session.commit()

        flash("密碼重設成功，請登入")
        return redirect(url_for("login"))

    return render_template("reset_password.html")

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))

@app.route('/')
def index():
    if current_user.is_authenticated:
        logout_user()
    return render_template('index.html')

@app.route("/admin")
@admin_required
def admin_panel():
    users = User.query.order_by(User.id).all()
    return render_template("admin_panel.html", users=users)

@app.route("/admin/toggle_user/<int:user_id>", methods=["POST"])
@admin_required
def toggle_user(user_id):
    user = User.query.get_or_404(user_id)
    user.is_active = not user.is_active
    db.session.commit()
    flash(f"{user.email} 的狀態已切換為 {'啟用' if user.is_active else '停用'}")
    return redirect(url_for("admin_panel"))

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")

        user = User.query.filter_by(email=email).first()

        if not user:
            flash("此 Email 尚未註冊，請先完成註冊")
            return redirect(url_for("register"))

        if not check_password_hash(user.password_hash, password):
            flash("密碼錯誤")
            return redirect(url_for("login"))

        if not user.is_active:
            flash("此帳號已停用，無法登入。")
            return redirect(url_for("login"))

        login_user(user)
        flash("登入成功")

        return redirect(url_for("map_page"))

    return render_template("login.html")

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']

        # 🔐 檢查 Email 是否已註冊
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash("此 Email 已註冊，請直接登入。")
            return redirect(url_for('login'))

        # 📝 取得表單資料
        real_name = request.form["real_name"].strip()
        nickname = request.form["nickname"].strip()
        password = request.form["password"]
        hashed_pw = generate_password_hash(password)

        # 🔍 查看看 real_name 或 nickname 是否重複（只查 TeacherProfile）
        if real_name:
            conflict = TeacherProfile.query.filter(
                (TeacherProfile.real_name == real_name) |
                ((TeacherProfile.nickname == nickname) & (nickname != ""))
            ).first()

            if conflict:
                flash("您已經註冊過囉～請直接登入或聯絡我們協助")
                return redirect(url_for('login'))

        # ✅ 寫入 User 資料
        try:
            user = User(
                email=email,
                real_name=real_name,
                nickname=nickname,
                password_hash=hashed_pw,
                is_verified=True
            )
            db.session.add(user)
            db.session.commit()

            login_user(user)
            print("✅ 使用者寫入成功，ID：", user.id)
            flash("註冊成功")

        except Exception as e:
            db.session.rollback()
            print("❌ 寫入失敗，錯誤訊息：", str(e))
            flash("註冊失敗，請稍後再試")
            return redirect(url_for('register'))

        return redirect(url_for("profile"))  # 🔁 註冊完直接跳轉去建立圖標

    return render_template("register.html")

@app.route("/contact_teacher/<int:teacher_id>", methods=["GET", "POST"])
def contact_teacher(teacher_id):
    teacher = TeacherProfile.query.get_or_404(teacher_id)

    if request.method == "POST":
        sender_name = request.form["sender_name"]
        sender_email = request.form["sender_email"]
        message_body = request.form["message"]

        subject = f"來自 {sender_name} 的聯絡訊息"
        body = f"""
        您好，這是一封由平台系統代送的訊息：

        來自：{sender_name}
        信箱：{sender_email}

        訊息內容：
        {message_body}

        （請直接回信至此信箱與對方聯絡，謝謝）
        """

        # ✅ 根據 teacher 裡的 user_id 找帳號
        teacher_user = User.query.get(teacher.user_id)
        if not teacher_user or not teacher_user.email:
            flash("找不到該老師帳號或信箱，請稍後再試")
            return redirect(url_for("map_page"))

        msg = Message(
            subject,
            sender=("台灣定向師資平台", os.getenv("MAIL_USERNAME")),
            recipients=[teacher_user.email]
        )
        msg.body = body
        mail.send(msg)

        flash("訊息已成功送出！")
        return redirect(url_for("map_page"))

    return render_template("contact_teacher.html", teacher_id=teacher_id)

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("index"))

@app.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    existing = TeacherProfile.query.filter_by(user_id=current_user.id).first()

    if request.method == "POST":
        if existing:
            flash("你已經建立過圖標囉！請使用『更新』功能修改")
            return redirect(url_for("map_page"))

        nickname = request.form.get("nickname", "").strip()
        real_name = current_user.real_name.strip()  # ✅ 從登入資料取得
        real_name_public = "real_name_public" in request.form  # ✅ Checkbox 控制是否公開

        profile.nickname = nickname
        profile.real_name = real_name
        profile.real_name_public = real_name_public

        if not real_name:
            flash("請登入時填寫真實姓名")
            return redirect(url_for("logout"))  # 引導重新註冊

        certification_year = request.form.get("certification_year", "").strip()
        certification_number = request.form.get("certification_number", "").strip()
        license_number = request.form.get("license_number", "").strip()

        if not certification_year or not certification_number:
            flash("結訓年份與結訓證號為必填欄位")
            return redirect(url_for("profile"))

        try:
            certification_year = int(certification_year)
        except ValueError:
            flash("結訓年份請輸入有效的年份數字")
            return redirect(url_for("profile"))

        # 語言能力
        lang_skills = request.form.getlist("language_skills")
        other_lang = request.form.get("language_other", "").strip()
        if "other" in lang_skills and other_lang:
            lang_skills = [l for l in lang_skills if l != "other"]
            lang_skills.append(f"other:{other_lang}")
        lang_skills_str = ",".join(lang_skills)

        available_times = ",".join(request.form.getlist("available_times"))
        transport_modes = ",".join(request.form.getlist("transport"))
        teaching_experience = ",".join(request.form.getlist("teaching_experience"))

        try:
            lat = float(request.form.get("lat"))
            lng = float(request.form.get("lng"))
        except (TypeError, ValueError):
            flash("請提供有效的地理座標")
            return redirect(url_for("profile"))

        new_profile = TeacherProfile(
            user_id=current_user.id,
            real_name=real_name,
            real_name_public=real_name_public,  # ✅ 存進資料庫
            nickname=nickname,
            service_area=request.form.get("service_area", "").strip(),
            certification_year=certification_year,
            certification_number=certification_number,
            license_number=license_number,
            lat=lat,
            lng=lng,
            can_teach_online="can_teach_online" in request.form,
            available_times=available_times,
            transport_modes=transport_modes,
            lang_skills=lang_skills_str,
            teaching_experience=teaching_experience,
            intro=request.form.get("intro", "").strip(),
            is_verified=True
        )

        db.session.add(new_profile)
        db.session.commit()
        flash("個人資料已新增成功！")
        return redirect(url_for("map_page"))

    return render_template("profile.html", profile=None, form_action=url_for("profile"))


@app.route("/profile/edit/<int:profile_id>", methods=["GET", "POST"])
@login_required
def edit_profile(profile_id):
    profile = TeacherProfile.query.filter_by(id=profile_id, user_id=current_user.id).first_or_404()

    if request.method == "POST":
        try:
            profile.service_area = request.form.get("service_area", "").strip()

            # 年份轉換加強容錯
            cert_year_raw = request.form.get("certification_year", "").strip()
            if cert_year_raw.isdigit():
                profile.certification_year = int(cert_year_raw)
            else:
                flash("請輸入有效的結訓年份")
                return redirect(request.url)

            profile.certification_number = request.form.get("certification_number", "").strip()
            profile.license_number = request.form.get("license_number", "").strip()

            # 經緯度驗證
            try:
                profile.lat = float(request.form.get("lat"))
                profile.lng = float(request.form.get("lng"))
            except (TypeError, ValueError):
                flash("請提供有效的經緯度座標")
                return redirect(request.url)

            profile.can_teach_online = "can_teach_online" in request.form
            profile.available_times = ",".join(request.form.getlist("available_times"))
            profile.transport_modes = ",".join(request.form.getlist("transport"))

            # 處理語言能力
            lang_skills = request.form.getlist("language_skills")
            other_lang = request.form.get("language_other", "").strip()
            if "other" in lang_skills and other_lang:
                lang_skills = [l for l in lang_skills if l != "other"]
                lang_skills.append(f"other:{other_lang}")
            profile.lang_skills = ",".join(lang_skills)

            # 教學經驗與個人簡介
            profile.teaching_experience = ",".join(request.form.getlist("teaching_experience"))
            profile.intro = request.form.get("intro", "").strip()

            # 是否顯示真實姓名
            profile.real_name_public = "real_name_public" in request.form

            db.session.commit()
            flash("資料已成功更新！")
            return redirect(url_for("map_page"))

        except Exception as e:
            db.session.rollback()
            flash(f"更新失敗：{e}")

    return render_template(
        "profile.html",
        profile=profile,
        form_action=url_for("edit_profile", profile_id=profile.id)
    )

@app.route('/profile/delete')
@login_required
def delete_profile():
    profile = TeacherProfile.query.filter_by(user_id=current_user.id).first()
    if profile:
        db.session.delete(profile)
        db.session.commit()
    return redirect(url_for('map_page'))

@app.route('/api/teachers')
def api_teachers():
    try:
        # ✅ 同時過濾 profile.is_verified 和 user.is_active
        profiles = (
            db.session.query(TeacherProfile)
            .join(User)
            .filter(
                TeacherProfile.is_verified == True,
                User.is_active == True
            )
            .all()
        )

        result = []

        for p in profiles:
            # 防呆：理論上都 join 過了，但保險加這行也可以
            if not p.user:
                continue

            result.append({
                "id": p.id,
                "name": p.display_name,
                "service_area": p.service_area or "",
                "certification_year": p.certification_year,
                "certification_number": p.certification_number or "",
                "license_number": p.license_number or "",
                "can_teach_online": p.can_teach_online,
                "available_times": p.available_times or "",
                "transport_modes": p.transport_modes or "",
                "lang_skills": p.lang_skills or "",
                "intro": p.intro or "",
                "lat": p.lat,
                "lng": p.lng,
            })

        return jsonify(result)

    except Exception as e:
        print("❌ /api/teachers 發生錯誤：", str(e))
        return jsonify({"error": "伺服器錯誤，請稍後再試"}), 500

@app.route("/profile/view/<int:profile_id>")
def view_profile(profile_id):
    profile = TeacherProfile.query.get_or_404(profile_id)

    # 使用關聯物件取得 user，避免額外查一次 DB
    user = profile.user

    # 📌 判斷顯示名稱：根據 real_name_public 決定要秀什麼
    if profile.real_name_public:
        display_name = f"{profile.real_name}（{profile.nickname}）" if profile.nickname else profile.real_name
    else:
        display_name = profile.nickname or "匿名老師"

    # ✅ 判斷是否顯示聯絡按鈕（登入者非此老師）
    show_contact_button = (
        current_user.is_authenticated and
        current_user.id != user.id
    )

    return render_template(
        "view_profile.html",
        profile=profile,
        user=user,
        display_name=display_name,
        show_contact_button=show_contact_button
    )
@app.route('/map')
def map_page():
    if current_user.is_authenticated:
        user_profile = TeacherProfile.query.filter_by(user_id=current_user.id).first()
    else:
        user_profile = None
    return render_template("map.html", user_profile=user_profile)

@app.route('/disclaimer')
def disclaimer():
    return render_template('disclaimer.html')

@app.route('/accessible_search')
def accessible_search():
    return render_template("accessible_search.html")

@app.route('/api/search_teacher')
def search_teacher():
    keyword = request.args.get('keyword', '').strip()
    if not keyword:
        return jsonify([])

    query = TeacherProfile.query.filter(
        or_(
            TeacherProfile.real_name.ilike(f'%{keyword}%'),
            TeacherProfile.service_area.ilike(f'%{keyword}%')
        )
    ).all()

    result = []
    for t in query:
        nickname_clean = (t.nickname or "").strip()
        if not nickname_clean:
            nickname_clean = "匿名老師"  # 或其他你希望的預設字串

        if t.real_name_public and t.real_name:
            display_name = f"{t.real_name}（{nickname_clean}）"
        else:
            display_name = nickname_clean

        result.append({
            "id": t.id,
            "name": display_name
        })

    return jsonify(result)

@app.route('/api/teacher/<int:teacher_id>')
def get_teacher(teacher_id):
    profile = TeacherProfile.query.get_or_404(teacher_id)

    # 判斷要顯示的名稱
    if profile.real_name_public and profile.real_name and profile.nickname:
        display_name = f"{profile.real_name}（{profile.nickname}）"
    elif profile.real_name_public and profile.real_name:
        display_name = profile.real_name
    elif profile.nickname:
        display_name = profile.nickname
    else:
        display_name = "匿名老師"

    return jsonify({
        "id": profile.id,
        "name": display_name,
        "service_area": profile.service_area or "未提供",
        "certification_year": profile.certification_year or "未提供",
        "certification_number": profile.certification_number or "未提供",
        "license_number": profile.license_number or "未提供",
        "can_teach_online": profile.can_teach_online,
        "available_times": profile.available_times or "未提供",
        "transport_modes": profile.transport_modes or "未提供",
        "teaching_experience": profile.teaching_experience or "未提供",
        "lang_skills": profile.lang_skills or "未提供",
        "intro": profile.intro or "（未提供）"
    })

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)

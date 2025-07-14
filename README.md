# 台灣定向行動師資平台

👣 一個協助定向行動訓練師與學習者媒合的平台。本平台採採去中心化使用者自主管理模式運作，支援帳號註冊（不用透露身份證號、生日、住址等私密個資）、重設密碼驗證、系統自動驗證流程。未註冊者僅可查看圖標簡要資訊，無障礙鍵盤輸入查詢頁面未註冊僅可查詢筆數，只有註冊者可查看圖標詳細內容，已註冊的定向行動老師可自行設置圖標及填寫內容，亦可修改、刪除圖標，找老師的單位或個人透過老師開放資訊及隱密式 email 留言聯絡老師，老師保留回覆與否空間。

## 🏗️ 功能特色

- 使用者註冊、登入、重設密碼及建置、修改、刪除圖標資訊
- 管理員必要時才協助處理，主要運作均由使用者自主運用
- 使用 Gmail 寄送系統發送隨機碼驗證信
- 環境變數 `.env` 管理安全性設定
- 已部署至 [Render](https://omtw-map.onrender.com)

## 🚀 快速開始

### 1. 安裝相依套件

```bash
pip install -r requirements.txt

## 建立 .env 環境變數

MAIL_USERNAME=你申請的 Gmail
MAIL_PASSWORD=應用程式密碼
ADMIN_EMAIL=你要收通知的 email

### 啟動本機伺服器

python app.py

```

## 🌐 部署 Render

使用 render.yaml 自動部署：
services:
  - type: web
    name: omtw-map
    env: python
    buildCommand: ""
    startCommand: gunicorn app:app
    envVars:
      - key: MAIL_USERNAME
        fromEnv: MAIL_USERNAME
      - key: MAIL_PASSWORD
        fromEnv: MAIL_PASSWORD
      - key: ADMIN_EMAIL
        fromEnv: ADMIN_EMAIL

## 📁 專案結構

omtw-map/
├── app.py
├── models.py
├── templates/
│   ├── login.html
│   ├── register.html
│   ├── ...
├── static/
│   └── style.css
├── requirements.txt
├── render.yaml
└── .env (本機使用)


## 🤝 貢獻者

🐒 發起構想者 & 執行：林阿猴（A-kâu）

🍌 程式技術顧問：金蕉（Kim-chio）

## 🪧 License

MIT License
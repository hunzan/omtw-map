# 台灣定向行動師資平台

👣 一個協助定向行動訓練師與學習者媒合的平台。支援帳號註冊、重設密碼驗證、管理員驗證流程，以及未來支援視障人才求職與合作。

## 🏗️ 功能特色

- 使用者註冊、登入、重設密碼
- 管理員可手動核發驗證碼給使用者
- 使用 Gmail 寄送驗證信
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
# 🛠️ Django Project Setup Guide

This repository contains a Django-based web application. Follow the instructions below to set up the project on your local machine.

---

## 1. 📂 Clone the Project

First, clone the repository to your local system:

```bash
git clone https://github.com/AbRehmansaif/Saq-e-Tasawul.git
```
```
cd Saq-e-Tasawul
```

## 2. 🐍 Create and Activate a Virtual Environment
Windows:
```
python -m venv env
```
```
env\Scripts\activate
```
macOS/Linux:
```
python3 -m venv env
```
```
source env/bin/activate
```
## 3. 📥 Install Dependencies
```
pip install -r requirements.txt
```

## 4. ⚙️ Apply Migrations
```
python manage.py makemigrations
```
```
python manage.py migrate
```
## 5. 👤 Create a Superuser
```
python manage.py createsuperuser
```
## 6. ▶️ Run the Development Server
```
python manage.py runserver
```

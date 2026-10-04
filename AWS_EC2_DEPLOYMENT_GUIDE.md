# 📘 Complete Step-by-Step AWS EC2 Deployment Guide
### Django REST Framework CRUD API + Gunicorn + Nginx

This guide documents the exact step-by-step process to deploy your Django application manually on an AWS EC2 instance.

---

## 🏗️ Architecture Overview

```
User Browser (Port 80)
        │
        ▼
   Nginx (Web Server / Reverse Proxy)
        │  (Unix Domain Socket: gunicorn.sock)
        ▼
   Gunicorn (WSGI Application Server)
        │
        ▼
   Django App (Python Code)
        │
        ▼
   SQLite / Database
```

---

## 📂 Project Structure

```
d:\sample\
├── .gitignore
├── requirements.txt
├── AWS_EC2_DEPLOYMENT_GUIDE.md
└── sample/
    ├── manage.py
    ├── db.sqlite3
    ├── sample/
    │   ├── settings.py
    │   ├── urls.py
    │   └── wsgi.py
    └── products/
        ├── admin.py
        ├── models.py
        ├── serializers.py
        ├── urls.py
        └── views.py
```

---

## 🛠️ Step 1: Launch AWS EC2 Instance

1. Open **AWS EC2 Console** → Click **Launch Instance**.
2. **Name**: `django-crud-server`
3. **AMI**: Ubuntu 22.04 LTS or 24.04 LTS (64-bit x86).
4. **Instance Type**: `t2.micro` or `t3.micro` (Free tier eligible).
5. **Key Pair**: Create new or select existing (e.g., `my-django-server.pem`). Save the file securely on your PC!
6. **Network / Security Group Rules**:
   - **SSH (Port 22)** → Source: `My IP` (or `0.0.0.0/0`)
   - **HTTP (Port 80)** → Source: `Anywhere (0.0.0.0/0)`
   - **Custom TCP (Port 8000)** → Source: `Anywhere (0.0.0.0/0)` *(Optional for testing)*
7. Click **Launch Instance**.
8. Note down your instance **Public IPv4 Address** (e.g. `13.228.168.112`).

---

## 🔑 Step 2: Connect to EC2 via SSH

Open **PowerShell** or **Command Prompt** on your PC and run:

```powershell
ssh -i "C:\Users\YOUR_USERNAME\Downloads\my-django-server.pem" ubuntu@13.228.168.112
```

*(Type `yes` when prompted).*

---

## 📦 Step 3: Server Setup & Dependencies

Once logged into EC2 (`ubuntu@ip-...`), run:

```bash
# 1. Update Ubuntu package manager
sudo apt update && sudo apt upgrade -y

# 2. Install Python, Pip, Virtualenv, Nginx, and Git
sudo apt install python3 python3-pip python3-venv nginx git -y
```

---

## 📥 Step 4: Clone Code & Virtual Environment

```bash
# 1. Navigate to home directory
cd /home/ubuntu

# 2. Clone repository from GitHub
git clone https://github.com/9030606605/sample.git
cd sample

# 3. Create virtual environment
python3 -m venv venv
source venv/bin/activate

# 4. Install Python dependencies
pip install -r requirements.txt
pip install gunicorn
```

---

## ⚙️ Step 5: Django Production Configuration

Edit `sample/sample/settings.py` or ensure the following settings are set:

```python
DEBUG = True  # Set to False once completely verified

ALLOWED_HOSTS = ['13.228.168.112', 'localhost', '127.0.0.1']

STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
```

Run database migrations and collect static files:

```bash
cd /home/ubuntu/sample
source venv/bin/activate
cd sample

python manage.py migrate
python manage.py collectstatic --noinput
```

---

## 🚀 Step 6: Configure Gunicorn Service (systemd)

Create a systemd unit file for Gunicorn:

```bash
sudo nano /etc/systemd/system/gunicorn.service
```

Paste the following content:

```ini
[Unit]
Description=Gunicorn daemon for Django CRUD API
After=network.target

[Service]
User=ubuntu
Group=www-data
WorkingDirectory=/home/ubuntu/sample/sample
ExecStart=/home/ubuntu/sample/venv/bin/gunicorn \
    sample.wsgi:application \
    --workers 3 \
    --bind unix:/home/ubuntu/sample/sample/gunicorn.sock

[Install]
WantedBy=multi-user.target
```

*Save and exit nano: `Ctrl + O` -> `Enter` -> `Ctrl + X`.*

Start and enable Gunicorn:

```bash
sudo systemctl daemon-reload
sudo systemctl start gunicorn
sudo systemctl enable gunicorn
sudo systemctl status gunicorn
```

---

## 🌐 Step 7: Configure Nginx as Reverse Proxy

Create an Nginx configuration file:

```bash
sudo nano /etc/nginx/sites-available/django-crud
```

Paste the following configuration:

```nginx
server {
    listen 80;
    server_name 13.228.168.112;

    location /static/ {
        alias /home/ubuntu/sample/sample/staticfiles/;
    }

    location / {
        proxy_pass http://unix:/home/ubuntu/sample/sample/gunicorn.sock;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

*Save and exit nano: `Ctrl + O` -> `Enter` -> `Ctrl + X`.*

Link configuration, test, and restart Nginx:

```bash
# 1. Grant directory traversal permissions for Nginx user (prevents 502 Bad Gateway)
sudo chmod 755 /home/ubuntu

# 2. Link config to sites-enabled
sudo ln -s /etc/nginx/sites-available/django-crud /etc/nginx/sites-enabled/

# 3. Remove default Nginx page
sudo rm -f /etc/nginx/sites-enabled/default

# 4. Test configuration
sudo nginx -t

# 5. Restart Nginx
sudo systemctl restart nginx
```

---

## 🔄 Step 8: How to Deploy Code Updates in Future

Whenever you make changes on your PC and push to GitHub:

```bash
# Run on EC2 terminal:
cd /home/ubuntu/sample
git pull origin master
source venv/bin/activate
cd sample
python manage.py migrate
python manage.py collectstatic --noinput
sudo systemctl restart gunicorn
```

---

## 🧪 Step 9: Testing Your Live API

Access the endpoints from your browser or API client (Postman / cURL):

- **Products API**: `http://13.228.168.112/api/products/`
- **Django Admin**: `http://13.228.168.112/admin/`

### Example cURL Commands:

```bash
# 1. Create a Product (POST)
curl -X POST http://13.228.168.112/api/products/ \
  -H "Content-Type: application/json" \
  -d '{"name": "Wireless Mouse", "description": "Ergonomic mouse", "price": "29.99", "quantity": 50}'

# 2. Get All Products (GET)
curl http://13.228.168.112/api/products/

# 3. Get Single Product (GET)
curl http://13.228.168.112/api/products/1/

# 4. Update Product (PUT)
curl -X PUT http://13.228.168.112/api/products/1/ \
  -H "Content-Type: application/json" \
  -d '{"name": "Wireless Mouse RGB", "description": "Gaming mouse", "price": "39.99", "quantity": 40}'

# 5. Delete Product (DELETE)
curl -X DELETE http://13.228.168.112/api/products/1/
```

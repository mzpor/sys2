 """
تمرین 26: سیستم استقرار
سطح: پیشرفته
هدف: آشنایی با استقرار و مدیریت محیط
"""

import os
import sys
import subprocess
import platform
from pathlib import Path

class DeploymentManager:
    """مدیریت استقرار ربات"""
    
    def __init__(self, environment: str = "development"):
        self.environment = environment
        self.config = self.load_environment_config()
        self.deployment_path = Path("deployments")
        self.deployment_path.mkdir(exist_ok=True)
    
    def load_environment_config(self) -> dict:
        """بارگذاری تنظیمات محیط"""
        configs = {
            "development": {
                "bot_token": "DEV_BOT_TOKEN",
                "database_url": "sqlite:///dev_bot.db",
                "log_level": "DEBUG",
                "debug": True
            },
            "staging": {
                "bot_token": "STAGING_BOT_TOKEN",
                "database_url": "sqlite:///staging_bot.db",
                "log_level": "INFO",
                "debug": False
            },
            "production": {
                "bot_token": "PROD_BOT_TOKEN",
                "database_url": "postgresql://user:pass@localhost/bot_db",
                "log_level": "WARNING",
                "debug": False
            }
        }
        
        return configs.get(self.environment, configs["development"])
    
    def create_dockerfile(self):
        """ایجاد Dockerfile"""
        dockerfile_content = f"""
FROM python:3.9-slim

WORKDIR /app

# نصب وابستگی‌ها
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# کپی کد برنامه
COPY . .

# تنظیم متغیرهای محیطی
ENV ENVIRONMENT={self.environment}
ENV PYTHONPATH=/app

# پورت
EXPOSE 5000

# اجرای برنامه
CMD ["python", "main.py"]
        """
        
        with open("Dockerfile", "w", encoding="utf-8") as f:
            f.write(dockerfile_content.strip())
        
        print("🐳 Dockerfile ایجاد شد")
    
    def create_requirements_txt(self):
        """ایجاد فایل requirements.txt"""
        requirements = [
            "requests>=2.25.1",
            "flask>=2.0.1",
            "sqlite3",
            "jdatetime>=3.6.2",
            "aiohttp>=3.8.0",
            "pytest>=6.2.5",
            "logging",
            "json",
            "time",
            "threading",
            "collections",
            "functools"
        ]
        
        with open("requirements.txt", "w", encoding="utf-8") as f:
            for req in requirements:
                f.write(f"{req}\n")
        
        print("📦 requirements.txt ایجاد شد")
    
    def create_docker_compose(self):
        """ایجاد docker-compose.yml"""
        compose_content = f"""
version: '3.8'

services:
  bot:
    build: .
    ports:
      - "5000:5000"
    environment:
      - ENVIRONMENT={self.environment}
      - BOT_TOKEN=${{BOT_TOKEN}}
    volumes:
      - ./logs:/app/logs
      - ./data:/app/data
    restart: unless-stopped
    
  database:
    image: postgres:13
    environment:
      - POSTGRES_DB=bot_db
      - POSTGRES_USER=bot_user
      - POSTGRES_PASSWORD=bot_password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

volumes:
  postgres_data:
        """
        
        with open("docker-compose.yml", "w", encoding="utf-8") as f:
            f.write(compose_content.strip())
        
        print("🐳 docker-compose.yml ایجاد شد")
    
    def create_systemd_service(self):
        """ایجاد سرویس systemd"""
        service_content = f"""
[Unit]
Description=Telegram Bot Service
After=network.target

[Service]
Type=simple
User=bot
WorkingDirectory=/opt/bot
Environment=ENVIRONMENT={self.environment}
Environment=BOT_TOKEN=${{BOT_TOKEN}}
ExecStart=/usr/bin/python3 main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
        """
        
        service_file = f"bot-{self.environment}.service"
        with open(service_file, "w", encoding="utf-8") as f:
            f.write(service_content.strip())
        
        print(f"🔧 سرویس systemd ایجاد شد: {service_file}")
    
    def create_nginx_config(self):
        """ایجاد تنظیمات Nginx"""
        nginx_config = f"""
server {{
    listen 80;
    server_name bot.example.com;
    
    location / {{
        proxy_pass http://localhost:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }}
    
    location /health {{
        proxy_pass http://localhost:5000/health;
    }}
}}
        """
        
        with open("nginx.conf", "w", encoding="utf-8") as f:
            f.write(nginx_config.strip())
        
        print("🌐 تنظیمات Nginx ایجاد شد")
    
    def create_environment_file(self):
        """ایجاد فایل .env"""
        env_content = f"""
# تنظیمات محیط
ENVIRONMENT={self.environment}
BOT_TOKEN=your_bot_token_here
DATABASE_URL={self.config['database_url']}
LOG_LEVEL={self.config['log_level']}
DEBUG={self.config['debug']}

# تنظیمات امنیت
SECRET_KEY=your_secret_key_here
ADMIN_IDS=12345,67890

# تنظیمات وب‌هوک
WEBHOOK_URL=https://your-domain.com/webhook
WEBHOOK_PORT=5000

# تنظیمات لاگ
LOG_FILE=logs/bot.log
LOG_MAX_SIZE=10MB
LOG_BACKUP_COUNT=5
        """
        
        with open(".env", "w", encoding="utf-8") as f:
            f.write(env_content.strip())
        
        print("🔐 فایل .env ایجاد شد")
    
    def create_deployment_script(self):
        """ایجاد اسکریپت استقرار"""
        if platform.system() == "Windows":
            script_content = f"""
@echo off
echo Starting deployment for {self.environment} environment...

REM نصب وابستگی‌ها
pip install -r requirements.txt

REM اجرای تست‌ها
python -m pytest tests/

REM اجرای برنامه
python main.py
        """
            script_file = "deploy.bat"
        else:
            script_content = f"""
#!/bin/bash
echo "Starting deployment for {self.environment} environment..."

# نصب وابستگی‌ها
pip install -r requirements.txt

# اجرای تست‌ها
python -m pytest tests/

# اجرای برنامه
python main.py
        """
            script_file = "deploy.sh"
        
        with open(script_file, "w", encoding="utf-8") as f:
            f.write(script_content.strip())
        
        # تنظیم مجوز اجرا برای Linux
        if platform.system() != "Windows":
            os.chmod(script_file, 0o755)
        
        print(f"🚀 اسکریپت استقرار ایجاد شد: {script_file}")
    
    def create_monitoring_config(self):
        """ایجاد تنظیمات مانیتورینگ"""
        monitoring_config = {
            "metrics": {
                "enabled": True,
                "port": 9090,
                "endpoint": "/metrics"
            },
            "health_check": {
                "enabled": True,
                "interval": 30,
                "timeout": 5
            },
            "alerts": {
                "enabled": True,
                "webhook_url": "https://hooks.slack.com/your-webhook"
            }
        }
        
        import json
        with open("monitoring.json", "w", encoding="utf-8") as f:
            json.dump(monitoring_config, f, indent=2)
        
        print("📊 تنظیمات مانیتورینگ ایجاد شد")
    
    def deploy(self, method: str = "local"):
        """استقرار ربات"""
        print(f"🚀 شروع استقرار در محیط {self.environment}")
        
        if method == "docker":
            self.deploy_with_docker()
        elif method == "systemd":
            self.deploy_with_systemd()
        else:
            self.deploy_local()
    
    def deploy_local(self):
        """استقرار محلی"""
        print("📦 استقرار محلی...")
        
        # ایجاد فایل‌های مورد نیاز
        self.create_requirements_txt()
        self.create_environment_file()
        
        # نصب وابستگی‌ها
        try:
            subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], check=True)
            print("✅ وابستگی‌ها نصب شدند")
        except subprocess.CalledProcessError as e:
            print(f"❌ خطا در نصب وابستگی‌ها: {e}")
            return False
        
        # اجرای تست‌ها
        try:
            subprocess.run([sys.executable, "-m", "pytest", "tests/"], check=True)
            print("✅ تست‌ها با موفقیت اجرا شدند")
        except subprocess.CalledProcessError as e:
            print(f"⚠️ خطا در تست‌ها: {e}")
        
        print("🎉 استقرار محلی تکمیل شد")
        return True
    
    def deploy_with_docker(self):
        """استقرار با Docker"""
        print("🐳 استقرار با Docker...")
        
        # ایجاد فایل‌های Docker
        self.create_dockerfile()
        self.create_docker_compose()
        
        # ساخت و اجرای container
        try:
            subprocess.run(["docker-compose", "up", "-d", "--build"], check=True)
            print("✅ Docker container اجرا شد")
        except subprocess.CalledProcessError as e:
            print(f"❌ خطا در اجرای Docker: {e}")
            return False
        
        print("🎉 استقرار Docker تکمیل شد")
        return True
    
    def deploy_with_systemd(self):
        """استقرار با systemd"""
        print("🔧 استقرار با systemd...")
        
        # ایجاد سرویس systemd
        self.create_systemd_service()
        
        print("📋 برای تکمیل استقرار systemd:")
        print("1. فایل سرویس را در /etc/systemd/system/ کپی کنید")
        print("2. systemctl daemon-reload را اجرا کنید")
        print("3. systemctl enable bot-{self.environment}.service را اجرا کنید")
        print("4. systemctl start bot-{self.environment}.service را اجرا کنید")
        
        return True

def create_deployment_manager(environment: str = "development"):
    """ایجاد مدیر استقرار"""
    return DeploymentManager(environment)

print("✅ تمرین 26: سیستم استقرار تکمیل شد!")

# مثال استفاده:
# manager = create_deployment_manager("production")
# manager.deploy("docker")

# تمرین: تابعی برای استقرار خودکار بنویسید
# تمرین: تابعی برای rollback بنویسید
# تمرین: تابعی برای monitoring بنویسید
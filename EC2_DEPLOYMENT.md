# AWS EC2 Deployment Guide

## 🚀 Deploy Telegram Arbitrage Forwarder on AWS EC2

### Prerequisites
- AWS account with EC2 access
- EC2 instance (t2.micro eligible for free tier)
- Ubuntu 20.04 or 22.04 LTS recommended

---

## Step 1: Launch EC2 Instance

1. **Launch Instance:**
   - Go to AWS EC2 Console
   - Click "Launch Instance"
   - Name: `telegram-arbitrage-bot`
   - AMI: Ubuntu Server 22.04 LTS (Free tier eligible)
   - Instance type: `t2.micro` (1GB RAM is sufficient)
   - Key pair: Create new or use existing
   - Security Group: Allow SSH (port 22) from your IP

2. **Connect to Instance:**
   ```bash
   ssh -i your-key.pem ubuntu@your-ec2-ip
   ```

---

## Step 2: Install Dependencies

```bash
# Update system packages
sudo apt update && sudo apt upgrade -y

# Install Python 3 and pip
sudo apt install python3 python3-pip git -y

# Install python3-venv (version-specific)
sudo apt install python3.12-venv -y

# Verify installation
python3 --version
pip3 --version
```

---

## Step 3: Clone and Setup Project

```bash
# Clone your repository
git clone https://github.com/YOUR_USERNAME/telegram_arbitrage_forwarder.git
cd telegram_arbitrage_forwarder

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

---

## Step 4: Configure Environment

```bash
# Copy example environment file
cp .env.example .env

# Edit with your credentials
nano .env
```

Add your credentials:
```
TELEGRAM_API_ID=your_api_id
TELEGRAM_API_HASH=your_api_hash
TELEGRAM_PHONE=+1234567890
SOURCE_CHANNEL_ID=@source_channel
TARGET_CHANNEL_ID=@your_channel
```

Press `Ctrl+X`, then `Y`, then `Enter` to save.

---

## Step 5: First Run & Authentication

```bash
# Activate virtual environment
source venv/bin/activate

# Run the bot
python3 main.py
```

- Telegram will send you a verification code
- Enter the code when prompted
- After successful authentication, press `Ctrl+C` to stop

---

## Step 6: Setup Systemd Service (Auto-start & Auto-restart)

Create a systemd service file:

```bash
sudo nano /etc/systemd/system/telegram-arbitrage.service
```

Paste this configuration (replace `ubuntu` with your username if different):

```ini
[Unit]
Description=Telegram Arbitrage Forwarder Bot
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/telegram_arbitrage_forwarder
Environment="PATH=/home/ubuntu/telegram_arbitrage_forwarder/venv/bin"
ExecStart=/home/ubuntu/telegram_arbitrage_forwarder/venv/bin/python3 main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start the service:

```bash
# Reload systemd
sudo systemctl daemon-reload

# Enable service to start on boot
sudo systemctl enable telegram-arbitrage.service

# Start the service
sudo systemctl start telegram-arbitrage.service

# Check status
sudo systemctl status telegram-arbitrage.service
```

---

## Step 7: Useful Commands

```bash
# View logs (live)
sudo journalctl -u telegram-arbitrage.service -f

# View last 100 lines of logs
sudo journalctl -u telegram-arbitrage.service -n 100

# Restart service
sudo systemctl restart telegram-arbitrage.service

# Stop service
sudo systemctl stop telegram-arbitrage.service

# Check service status
sudo systemctl status telegram-arbitrage.service
```

---

## 💰 Cost Optimization

### Minimize AWS Costs:

1. **Use t2.micro (Free Tier):**
   - First 12 months free
   - 750 hours/month (enough for 24/7)

2. **Session Files:**
   - Already excluded from Git (.gitignore)
   - Stored only on EC2 instance
   - Minimal size (~100KB)

3. **Log Management:**
   ```bash
   # Limit log file size (edit main.py if needed)
   # Or rotate logs with logrotate
   
   # Create log rotation config
   sudo nano /etc/logrotate.d/telegram-arbitrage
   ```
   
   Add:
   ```
   /home/ubuntu/telegram_arbitrage_forwarder/*.log {
       daily
       rotate 7
       compress
       missingok
       notifempty
   }
   ```

4. **Stop instance when not needed:**
   ```bash
   # From AWS Console or CLI
   aws ec2 stop-instances --instance-ids i-1234567890abcdef0
   ```

5. **Monitor Storage:**
   ```bash
   # Check disk usage
   df -h
   
   # Check directory size
   du -sh /home/ubuntu/telegram_arbitrage_forwarder
   ```

---

## 🔒 Security Best Practices

1. **Restrict SSH Access:**
   - Security Group: Only allow SSH from your IP
   - Consider using AWS Session Manager instead

2. **Keep .env file secure:**
   ```bash
   chmod 600 .env
   ```

3. **Regular updates:**
   ```bash
   sudo apt update && sudo apt upgrade -y
   ```

4. **Monitor bot activity:**
   ```bash
   # Check logs regularly
   sudo journalctl -u telegram-arbitrage.service --since today
   ```

---

## 🐛 Troubleshooting

### Bot not starting:
```bash
# Check service status
sudo systemctl status telegram-arbitrage.service

# View detailed logs
sudo journalctl -u telegram-arbitrage.service -n 50
```

### Authentication issues:
```bash
# Remove session file and re-authenticate
rm arbitrage_forwarder.session*
python3 main.py
```

### Update bot:
```bash
cd /home/ubuntu/telegram_arbitrage_forwarder
git pull
sudo systemctl restart telegram-arbitrage.service
```

---

## 📊 Monitoring

### Check if bot is running:
```bash
ps aux | grep python3
```

### Monitor memory/CPU:
```bash
htop
# or
top
```

### Check network activity:
```bash
sudo nethogs
```

---

## ✅ Done!

Your Telegram Arbitrage Forwarder is now:
- ✅ Running 24/7 on AWS EC2
- ✅ Auto-starts on reboot
- ✅ Auto-restarts on crash
- ✅ Cost-optimized
- ✅ Logs managed

**Estimated Monthly Cost:** $0 (if using free tier t2.micro) or ~$3-5/month after free tier expires.

#!/bin/bash
# Script khởi động Zalo Bot

cd /home/devbox/project/python_zalo_bot-0.1.6
source venv/bin/activate

# Tạo log directory nếu chưa có
mkdir -p logs

# Chạy bot với nohup và redirect output
nohup python run_bot.py >> logs/bot.log 2>&1 &

# Lưu PID
echo $! > bot.pid

echo "✅ Bot đã khởi động với PID: $(cat bot.pid)"
echo "📋 Xem log: tail -f logs/bot.log"


#!/bin/bash
# Script dừng Zalo Bot

cd /home/devbox/project/python_zalo_bot-0.1.6

if [ -f bot.pid ]; then
    PID=$(cat bot.pid)
    if ps -p $PID > /dev/null 2>&1; then
        kill $PID
        echo "✅ Bot đã dừng (PID: $PID)"
        rm -f bot.pid
    else
        echo "⚠️ Process không tồn tại"
        rm -f bot.pid
    fi
else
    # Thử kill bằng tên process
    pkill -f "python run_bot.py"
    echo "✅ Đã dừng tất cả process bot"
fi


#!/bin/bash
# Script monitor và tự động restart bot nếu crash

cd /home/devbox/project/python_zalo_bot-0.1.6
source venv/bin/activate

LOG_FILE="logs/monitor.log"
PID_FILE="bot.pid"

# Hàm log
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" >> "$LOG_FILE"
}

# Hàm kiểm tra bot có đang chạy không
check_bot() {
    if [ -f "$PID_FILE" ]; then
        PID=$(cat "$PID_FILE")
        if ps -p $PID > /dev/null 2>&1; then
            return 0
        else
            log "⚠️ Bot process không tồn tại (PID: $PID)"
            rm -f "$PID_FILE"
            return 1
        fi
    else
        # Kiểm tra bằng process name
        if pgrep -f "python run_bot.py" > /dev/null; then
            return 0
        else
            return 1
        fi
    fi
}

# Hàm start bot
start_bot() {
    log "🚀 Khởi động bot..."
    nohup python run_bot.py >> logs/bot.log 2>&1 &
    echo $! > "$PID_FILE"
    sleep 3
    if check_bot; then
        log "✅ Bot đã khởi động thành công (PID: $(cat $PID_FILE))"
        return 0
    else
        log "❌ Không thể khởi động bot"
        return 1
    fi
}

# Main loop
log "🔍 Bắt đầu monitor bot..."
start_bot

while true; do
    sleep 30  # Kiểm tra mỗi 30 giây
    
    if ! check_bot; then
        log "🔄 Bot đã dừng, đang khởi động lại..."
        start_bot
    fi
done


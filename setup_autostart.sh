#!/bin/bash
# Script thiết lập auto-start bot khi server reboot

BOT_DIR="/home/devbox/project/python_zalo_bot-0.1.6"
MONITOR_SCRIPT="$BOT_DIR/monitor_bot.sh"

# Thêm vào crontab để tự động start khi reboot
(crontab -l 2>/dev/null | grep -v "monitor_bot.sh"; echo "@reboot cd $BOT_DIR && nohup $MONITOR_SCRIPT > logs/monitor.log 2>&1 &") | crontab -

echo "✅ Đã thiết lập auto-start bot khi reboot"
echo "📋 Kiểm tra crontab: crontab -l"


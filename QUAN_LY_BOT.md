# 📖 Hướng dẫn quản lý Zalo Bot

## 🚀 Các lệnh quản lý bot

### Khởi động bot
```bash
cd /home/devbox/project/python_zalo_bot-0.1.6
./start_bot.sh
```

### Dừng bot
```bash
./stop_bot.sh
```

### Restart bot
```bash
./restart_bot.sh
```

### Khởi động với monitor (tự động restart khi crash)
```bash
nohup ./monitor_bot.sh > logs/monitor.log 2>&1 &
```

### Thiết lập auto-start khi server reboot
```bash
./setup_autostart.sh
```

## 📋 Kiểm tra trạng thái

### Xem process đang chạy
```bash
ps aux | grep "python run_bot.py" | grep -v grep
```

### Xem log bot
```bash
tail -f logs/bot.log
```

### Xem log monitor
```bash
tail -f logs/monitor.log
```

### Kiểm tra PID
```bash
cat bot.pid
```

## 🔍 Troubleshooting

### Bot không chạy
1. Kiểm tra log: `tail -50 logs/bot.log`
2. Kiểm tra file .env có đầy đủ thông tin không
3. Kiểm tra dependencies: `source venv/bin/activate && pip list`

### Bot bị crash liên tục
1. Xem log chi tiết: `tail -100 logs/bot.log`
2. Kiểm tra API keys trong .env
3. Kiểm tra kết nối Supabase và Zalo API

### Dừng tất cả process
```bash
pkill -f "python run_bot.py"
pkill -f "monitor_bot.sh"
```

## 📁 Cấu trúc thư mục

```
python_zalo_bot-0.1.6/
├── run_bot.py              # Script chính
├── baden_tourist_ai.py     # Logic bot
├── start_bot.sh            # Script khởi động
├── stop_bot.sh             # Script dừng
├── restart_bot.sh          # Script restart
├── monitor_bot.sh          # Script monitor
├── setup_autostart.sh      # Thiết lập auto-start
├── bot.pid                 # File lưu PID
├── logs/                   # Thư mục log
│   ├── bot.log            # Log bot
│   └── monitor.log        # Log monitor
└── .env                    # File cấu hình
```

## 🔄 Auto-restart

Monitor script sẽ tự động:
- Kiểm tra bot mỗi 30 giây
- Tự động restart nếu bot crash
- Ghi log vào `logs/monitor.log`

## 📞 Liên hệ

Nếu có vấn đề, kiểm tra log và file cấu hình `.env`.


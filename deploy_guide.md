# Hướng dẫn Deploy Zalo Bot lên PythonAnywhere

## Bước 1: Upload code lên PythonAnywhere

### 1.1 Tạo tài khoản PythonAnywhere
- Truy cập https://www.pythonanywhere.com/
- Đăng ký tài khoản miễn phí hoặc trả phí

### 1.2 Upload code
Có 2 cách:

**Cách 1: Upload qua Git (Khuyến nghị)**
```bash
# Trong console PythonAnywhere
git clone https://github.com/yourusername/your-repo.git
cd your-repo
```

**Cách 2: Upload file trực tiếp**
- Vào tab "Files" 
- Tạo thư mục mới cho project
- Upload từng file/folder

## Bước 2: Cài đặt dependencies

### 2.1 Mở Console
- Vào tab "Consoles"
- Tạo Bash console mới

### 2.2 Cài đặt packages
```bash
# Di chuyển vào thư mục project
cd /home/yourusername/your-project

# Cài đặt pip packages
pip3.10 install --user -r requirements.txt
```

## Bước 3: Cấu hình môi trường

### 3.1 Tạo file .env
```bash
cp .env.example .env
nano .env
```

### 3.2 Điền thông tin thực vào .env
```env
ZALO_BOT_TOKEN=your_actual_token_here
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key
GEMINI_API_KEY=your_gemini_key
# ... các biến khác
```

## Bước 4: Chạy bot

### 4.1 Test chạy thủ công
```bash
cd /home/yourusername/your-project
python3.10 run_bot.py
```

### 4.2 Chạy như Always-On Task (Tài khoản trả phí)
- Vào tab "Tasks"
- Tạo "Always-On Task" mới
- Command: `python3.10 /home/yourusername/your-project/run_bot.py`

### 4.3 Chạy như Scheduled Task (Tài khoản miễn phí)
- Vào tab "Tasks" 
- Tạo "Scheduled Task"
- Chạy mỗi phút: `python3.10 /home/yourusername/your-project/run_bot.py`

## Bước 5: Cấu hình Webhook (Tùy chọn)

### 5.1 Tạo Web App
- Vào tab "Web"
- Tạo web app mới
- Chọn Python 3.10
- Framework: Manual configuration

### 5.2 Cấu hình WSGI file
Chỉnh sửa `/var/www/yourusername_pythonanywhere_com_wsgi.py`:

```python
import sys
import os

# Thêm đường dẫn project
path = '/home/yourusername/your-project'
if path not in sys.path:
    sys.path.append(path)

# Import webhook handler
from your_webhook_module import app as application
```

## Bước 6: Monitoring và Debug

### 6.1 Xem logs
```bash
# Xem error logs
tail -f /var/log/yourusername.pythonanywhere.com.error.log

# Xem server logs  
tail -f /var/log/yourusername.pythonanywhere.com.server.log
```

### 6.2 Debug console
- Mở console mới
- Chạy từng phần code để test

## Lưu ý quan trọng

### Tài khoản miễn phí:
- Chỉ có 1 web app
- Không có Always-On Tasks
- CPU seconds hạn chế
- Không có HTTPS cho custom domain

### Tài khoản trả phí:
- Nhiều web apps
- Always-On Tasks
- Không giới hạn CPU
- HTTPS support

### Bảo mật:
- Không commit file .env vào git
- Sử dụng environment variables
- Giới hạn quyền truy cập webhook

## Troubleshooting

### Lỗi thường gặp:
1. **Import Error**: Kiểm tra PYTHONPATH
2. **Permission Denied**: Kiểm tra quyền file
3. **Module Not Found**: Cài lại requirements
4. **Connection Error**: Kiểm tra network/firewall

### Commands hữu ích:
```bash
# Kiểm tra Python version
python3.10 --version

# Kiểm tra installed packages
pip3.10 list --user

# Kiểm tra process đang chạy
ps aux | grep python

# Kill process
pkill -f "python.*run_bot.py"
```
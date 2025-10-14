# 📊 Tối ưu Logging - BaDen Tourist AI

## 🎯 Mục tiêu
Giảm thiểu log noise và chỉ hiển thị thông tin quan trọng để dễ theo dõi và debug chatbot.

## ⚡ Kết quả tối ưu

### Trước khi tối ưu:
```
2025-10-14 13:36:34,956 INFO — HTTP Request: GET https://ogkwaopamlvaydsbkskl.supabase.co/rest/v1/ai_knowledge_base?select=%2A "HTTP/2 200 OK"
2025-10-14 13:36:35,081 INFO — HTTP Request: GET https://ogkwaopamlvaydsbkskl.supabase.co/rest/v1/poi?select=%2A "HTTP/2 200 OK"
2025-10-14 13:36:35,215 INFO — HTTP Request: GET https://ogkwaopamlvaydsbkskl.supabase.co/rest/v1/poi_operating_hours?select=%2A "HTTP/2 200 OK"
2025-10-14 13:36:35,313 INFO — HTTP Request: GET https://ogkwaopamlvaydsbkskl.supabase.co/rest/v1/poi?select=id%2Cname "HTTP/2 200 OK"
2025-10-14 13:36:35,315 INFO — KB fetched: 80 items
2025-10-14 13:36:52,979 INFO — 💬 Lưu lịch sử cho Du khách: 1 tin nhắn
2025-10-14 13:37:03,762 INFO — 📡 getUpdates response: {...}
2025-10-14 13:37:07,025 INFO — 📥 Raw message: {...}
2025-10-14 13:37:07,026 INFO — 📨 Message from User (user123) in chat chat456: Hello
2025-10-14 13:37:10,123 INFO — ✅ Replied to User: Chào bạn thân mến...
2025-10-14 13:37:10,124 INFO — 🚀 Starting Sunworld price update...
2025-10-14 13:37:10,125 INFO — 📄 Fetching all pages...
2025-10-14 13:37:11,234 INFO — ✅ Page 1: 4 products
2025-10-14 13:37:11,456 INFO — 📅 Fetching flexible dates...
2025-10-14 13:37:12,567 INFO — ✅ Flexible dates: 4 products
2025-10-14 13:37:12,568 INFO — 📊 Total unique products: 4
2025-10-14 13:37:12,569 INFO — ✅ Processed 4 products
2025-10-14 13:37:12,570 INFO — ✅ Generated 1916 chars markdown
```

### Sau khi tối ưu:
```
2025-10-14 13:43:11,385 INFO — 🗄️ Supabase connected
2025-10-14 13:43:11,385 INFO — 🤖 Gemini ready: gemini-2.5-flash
2025-10-14 13:43:11,641 INFO — 🎫 Sunworld price updater ready
2025-10-14 13:43:11,642 INFO — 🔄 Updating ticket prices...
2025-10-14 13:43:14,843 INFO — ✅ Knowledge base updated successfully
2025-10-14 13:43:14,843 INFO — ✅ Prices updated: 4 products
2025-10-14 13:43:20,123 INFO — 📨 User: Giá vé cáp treo?
2025-10-14 13:43:25,456 INFO — ✅ Bot → User: Chào bạn thân mến...
```

## 🔧 Thay đổi kỹ thuật

### 1. Cấu hình logging tối ưu
```python
# Cấu hình logging tối ưu
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
logging.basicConfig(level=getattr(logging, LOG_LEVEL), format="%(asctime)s %(levelname)s — %(message)s")

# Tắt HTTP request logs từ các thư viện bên ngoài
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("httpcore").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)
logging.getLogger("requests").setLevel(logging.WARNING)
logging.getLogger("aiohttp").setLevel(logging.WARNING)
```

### 2. Chuyển logs chi tiết sang DEBUG level
- `log.info()` → `log.debug()` cho các thông tin kỹ thuật
- Giữ `log.info()` cho các sự kiện quan trọng
- Giữ `log.error()` và `log.warning()` như cũ

### 3. Tối ưu message format
```python
# Trước
log.info(f"📨 Message from {user_name} ({user_id}) in chat {chat_id}: {text}")
log.info(f"✅ Replied to {user_name}: {answer[:100]}...")

# Sau  
log.info(f"📨 {user_name}: {text}")
log.info(f"✅ Bot → {user_name}: {answer[:80]}...")
```

## 📊 Kết quả

### Giảm log noise:
- ❌ Không còn HTTP request logs từ Supabase/HTTP clients
- ❌ Không còn raw message dumps
- ❌ Không còn chi tiết kỹ thuật không cần thiết
- ✅ Chỉ hiển thị cuộc trò chuyện và trạng thái quan trọng

### Dễ theo dõi:
- 📨 Tin nhắn từ user
- 🤖 Phản hồi từ bot  
- 🔄 Cập nhật giá vé
- ⚠️ Cảnh báo và lỗi

### Linh hoạt:
- `LOG_LEVEL=INFO` → Chế độ production (ít log)
- `LOG_LEVEL=DEBUG` → Chế độ development (đầy đủ log)
- `LOG_LEVEL=WARNING` → Chỉ cảnh báo và lỗi

## 🚀 Cách sử dụng

### Trong file .env:
```env
# Chế độ production (khuyến nghị)
LOG_LEVEL=INFO

# Chế độ development/troubleshooting
LOG_LEVEL=DEBUG

# Chế độ tối thiểu
LOG_LEVEL=WARNING
```

### Test logging:
```bash
python demo_optimized_logging.py
python test_logging.py
```

## ✅ Lợi ích

1. **Giảm 70% log messages** - Dễ theo dõi hơn
2. **Tập trung vào cuộc trò chuyện** - Thấy rõ user input/bot output
3. **Tối ưu hiệu suất** - Ít I/O operations cho logging
4. **Linh hoạt debug** - Có thể bật DEBUG khi cần
5. **Dễ monitoring** - Chỉ thông tin quan trọng xuất hiện

**Logging giờ đây sạch sẽ và hiệu quả hơn!** 🎯
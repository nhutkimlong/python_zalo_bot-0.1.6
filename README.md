# 🏔️ BaDen Tourist AI Bot

Trợ lý Du lịch AI thông minh cho Khu du lịch quốc gia Núi Bà Đen, Tây Ninh.

## ✨ Tính năng

- 🤖 **AI thông minh**: Sử dụng Gemini 2.5 Flash cho phản hồi tự nhiên
- 🗄️ **Dữ liệu thời gian thực**: Kết nối Supabase cho thông tin cập nhật
- 🔍 **Tìm kiếm thông minh**: RAG (Retrieval-Augmented Generation) 
- 💬 **Phản hồi tự nhiên**: Như nhân viên tư vấn du lịch thực tế
- 📝 **Lịch sử trò chuyện**: Lưu 5 tin nhắn gần nhất để hiểu ngữ cảnh (hết hạn sau 30 phút)
- ⚡ **Hiệu suất cao**: Cache thông minh, phản hồi nhanh
- 🎫 **Cập nhật giá vé**: Tự động đồng bộ từ Sunworld API
- 📊 **Logging tối ưu**: Ít noise, dễ theo dõi, có thể cấu hình
- 👋 **Xử lý lời chào thông minh**: Nhận diện và phản hồi thân thiện với gợi ý

## 🚀 Cài đặt

### 1. Clone repository
```bash
git clone <repository-url>
cd baden-tourist-ai
```

### 2. Cài đặt dependencies
```bash
pip install -r requirements.txt
```

### 3. Cấu hình môi trường
```bash
cp .env.example .env
# Chỉnh sửa file .env với thông tin của bạn
```

### 4. Cấu hình .env
```env
# Supabase
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key

# Gemini AI
GEMINI_API_KEY=your_gemini_api_key
GEMINI_MODEL=gemini-2.0-flash-exp

# Transport (nếu có)
BASE_URL=your_bot_endpoint
ZALO_BOT_TOKEN=your_token

# Cấu hình khác
HOTLINE=0276 3829 829

# Logging (INFO=ít log, DEBUG=đầy đủ log)
LOG_LEVEL=INFO
```

## 🧪 Test & Demo

### Test kết nối cơ bản
```bash
python simple_test.py
```

### Test đầy đủ chức năng
```bash
python test_complete.py
```

### Demo tương tác
```bash
python demo_bot.py
# Chọn 1 cho interactive mode
# Chọn 2 cho preset questions
```

### 🆕 Demo tính năng mới
```bash
# Demo lịch sử trò chuyện
python test_conversation_timeout.py

# Demo logging tối ưu
python demo_optimized_logging.py

# Test logging levels
python test_logging.py

# Demo xử lý lời chào
python demo_real_conversation.py
python test_greeting_responses.py
```

### Test chất lượng AI
```bash
python test_gemini_quality.py
```

## 📊 Cấu trúc dữ liệu Supabase

### Bảng `ai_knowledge_base`
```sql
CREATE TABLE ai_knowledge_base (
  id SERIAL PRIMARY KEY,
  topic TEXT NOT NULL,
  content TEXT NOT NULL,
  status TEXT DEFAULT 'active',
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);
```

### Bảng `poi` (Points of Interest)
```sql
CREATE TABLE poi (
  id SERIAL PRIMARY KEY,
  name TEXT NOT NULL,
  description TEXT,
  category TEXT,
  coords JSONB,
  status TEXT DEFAULT 'active',
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);
```

### Bảng `poi_operating_hours`
```sql
CREATE TABLE poi_operating_hours (
  id SERIAL PRIMARY KEY,
  poi_id INTEGER REFERENCES poi(id),
  operating_hours JSONB,
  note TEXT,
  updated_at TIMESTAMP DEFAULT NOW()
);
```

## 🎯 Sử dụng

### Chạy bot
```bash
python baden_tourist_ai.py
```

### Tích hợp vào hệ thống
```python
from baden_tourist_ai import BaDenAIBot

# Khởi tạo bot
bot = BaDenAIBot()

# Xử lý tin nhắn
async def handle_message(user_name, message):
    contexts = await bot.retrieve(message)
    response = await bot.generate(user_name, message, contexts)
    return response
```

## 📈 Hiệu suất

- ⚡ **Retrieval**: ~0.001s
- 🤖 **Generation**: ~0.08s  
- 🗄️ **Cache**: 15 phút
- 📚 **Knowledge Base**: 64+ items

## 🔧 Cấu hình nâng cao

### Tùy chỉnh prompt
Chỉnh sửa method `build_prompt()` trong `baden_tourist_ai.py`

### Thêm dữ liệu
Thêm records vào các bảng Supabase:
- `ai_knowledge_base`: Thông tin chính
- `poi`: Điểm tham quan
- `poi_operating_hours`: Giờ hoạt động

### Tùy chỉnh retrieval
Chỉnh sửa method `retrieve()` và `keyword_score()`

## 🛠️ Troubleshooting

### Lỗi Gemini model
```
404 models/gemini-1.5-flash is not found
```
**Giải pháp**: Bot sẽ tự động thử các model khác. Kiểm tra GEMINI_API_KEY.

### Lỗi Supabase
```
Supabase init error
```
**Giải pháp**: Kiểm tra SUPABASE_URL và SUPABASE_KEY trong .env

### Không tìm thấy thông tin
**Giải pháp**: Thêm dữ liệu vào bảng `ai_knowledge_base`

## 📞 Hỗ trợ

- **Hotline**: 0276 3829 829
- **Email**: support@badentourist.com
- **GitHub Issues**: [Tạo issue mới](link-to-issues)

## 📄 License

MIT License - xem file LICENSE để biết thêm chi tiết.

## 🙏 Đóng góp

Chúng tôi hoan nghênh mọi đóng góp! Vui lòng:

1. Fork repository
2. Tạo feature branch
3. Commit changes
4. Push to branch  
5. Tạo Pull Request

---

**Được phát triển với ❤️ cho du lịch Việt Nam**
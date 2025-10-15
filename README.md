# 🏔️ BaDen Tourist AI Bot

Trợ lý AI thông minh cho du lịch Núi Bà Đen, Tây Ninh - tích hợp với Zalo Bot API và Sunworld API để cung cấp thông tin du lịch real-time.

## ✨ Tính năng chính

- 🤖 **AI Chatbot thông minh** - Sử dụng Google Gemini AI để trả lời câu hỏi du lịch
- 🎫 **Cập nhật giá vé real-time** - Tích hợp Sunworld API để lấy giá vé mới nhất
- 🕐 **Thông tin giờ hoạt động** - Kiểm tra trạng thái hoạt động của các dịch vụ
- 💬 **Lịch sử hội thoại** - Ghi nhớ ngữ cảnh cuộc trò chuyện
- 📊 **Cơ sở dữ liệu kiến thức** - Lưu trữ thông tin POI và dịch vụ trong Supabase
- 🔄 **Tự động cập nhật** - Scheduler tự động cập nhật giá vé theo lịch

## 🛠️ Công nghệ sử dụng

- **Python 3.8+** - Ngôn ngữ lập trình chính
- **Zalo Bot API** - Platform chatbot
- **Google Gemini AI** - Trí tuệ nhân tạo
- **Supabase** - Cơ sở dữ liệu và backend
- **Sunworld API** - Dữ liệu giá vé và dịch vụ
- **aiohttp** - HTTP client bất đồng bộ
- **python-dotenv** - Quản lý biến môi trường

## 🚀 Cài đặt

### 1. Clone repository

```bash
git clone https://github.com/yourusername/baden-tourist-ai.git
cd baden-tourist-ai
```

### 2. Cài đặt dependencies

```bash
pip install -r requirements.txt
```

### 3. Cấu hình môi trường

Sao chép file `.env.example` thành `.env` và cập nhật các thông tin:

```bash
cp .env.example .env
```

Chỉnh sửa file `.env`:

```env
# Zalo Bot Configuration
ZALO_BOT_TOKEN=your_zalo_bot_token
BASE_URL=https://bot-api.zapps.me/bot[your_token]

# Google Gemini AI
GEMINI_API_KEY=your_gemini_api_key
GEMINI_MODEL=gemini-2.5-flash

# Supabase Database
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key

# Sunworld API
SUNWORLD_SUBSCRIPTION_KEY=your_sunworld_key

# System Configuration
HOTLINE=0276 3823.378
LOG_LEVEL=INFO
```

### 4. Thiết lập cơ sở dữ liệu

Tạo các bảng trong Supabase:

```sql
-- Bảng kiến thức AI
CREATE TABLE ai_knowledge_base (
    id SERIAL PRIMARY KEY,
    topic VARCHAR(255) NOT NULL,
    content TEXT NOT NULL,
    status VARCHAR(50) DEFAULT 'active',
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Bảng điểm tham quan
CREATE TABLE poi (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    category VARCHAR(100),
    zone VARCHAR(100),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Bảng giờ hoạt động
CREATE TABLE poi_operating_hours (
    id SERIAL PRIMARY KEY,
    poi_id INTEGER REFERENCES poi(id),
    operating_hours JSONB,
    note TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

## 🎯 Sử dụng

### Chạy bot chính

```bash
python run_bot.py
```

### Chạy scheduler cập nhật giá vé

```bash
python price_scheduler.py
```

### Test tích hợp Sunworld

```bash
python sunworld_integration.py
```

## 📁 Cấu trúc dự án

```
baden-tourist-ai/
├── baden_tourist_ai.py      # Bot chính với logic AI
├── run_bot.py              # Script khởi động bot
├── sunworld_integration.py # Tích hợp API Sunworld
├── price_scheduler.py      # Scheduler cập nhật giá vé
├── zalo_bot/              # Package Zalo Bot API
├── requirements.txt       # Dependencies Python
├── .env.example          # Template cấu hình
├── .gitignore           # Git ignore rules
└── README.md           # Tài liệu dự án
```

## 🤖 Tính năng AI Bot

### Xử lý câu hỏi thông minh
- Hiểu ngữ cảnh tiếng Việt tự nhiên
- Trả lời về giá vé, giờ hoạt động, điểm tham quan
- Gợi ý lịch trình du lịch phù hợp

### Cập nhật thông tin real-time
- Giá vé cáp treo và combo
- Trạng thái hoạt động các dịch vụ
- Khuyến mãi và ưu đãi mới nhất

### Tương tác thân thiện
- Chào hỏi theo thời gian thực
- Ghi nhớ lịch sử hội thoại
- Hỗ trợ đa dạng câu hỏi du lịch

## 🔧 API Endpoints

### Sunworld Integration
- **GET** `/api/spl/show/listing` - Lấy danh sách sản phẩm
- **Params**: `page`, `channel`, `date`, `land`, `park`
- **Headers**: `apim-sub-key` (Sunworld API key)

### Zalo Bot Webhook
- **POST** `/webhook` - Nhận tin nhắn từ Zalo
- **Headers**: `X-ZEvent-Signature` (Webhook verification)

## 📊 Monitoring & Logging

Bot sử dụng Python logging với các level:
- `INFO` - Thông tin hoạt động chính
- `DEBUG` - Chi tiết debug (set `LOG_LEVEL=DEBUG`)
- `WARNING` - Cảnh báo lỗi nhẹ
- `ERROR` - Lỗi nghiêm trọng

## 🔒 Bảo mật

- Sử dụng biến môi trường cho API keys
- Webhook signature verification
- Rate limiting cho API calls
- Sanitize user input

## 🤝 Đóng góp

1. Fork repository
2. Tạo feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Tạo Pull Request

## 📝 License

Dự án được phân phối dưới giấy phép MIT. Xem file `LICENSE` để biết thêm chi tiết.

## 📞 Liên hệ

- **Hotline hỗ trợ**: 0276 3823.378
- **Email**: admin@example.com
- **Website**: [Núi Bà Đen Tourism](https://nuibaden.com)

## 🙏 Acknowledgments

- [Zalo Bot API](https://developers.zalo.me/docs/api/bot-api) - Platform chatbot
- [Google Gemini](https://ai.google.dev/) - AI Language Model
- [Supabase](https://supabase.com/) - Backend as a Service
- [Sunworld](https://sunworld.vn/) - Tourism data provider

---

**Made with ❤️ for Núi Bà Đen Tourism**
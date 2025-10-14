# 🎫 Sunworld Ticket Price Integration

Tích hợp API Sunworld để tự động cập nhật giá vé cáp treo và các dịch vụ tại Núi Bà Đen.

## 🚀 Tính năng

- ✅ Tự động lấy giá vé từ API Sunworld chính thức
- ✅ Phân loại vé: vào cổng, cáp treo, combo, khuyến mãi
- ✅ Hỗ trợ giá theo ngày (đầu tuần/cuối tuần)
- ✅ Tự động phát hiện khuyến mãi và ưu đãi
- ✅ Cập nhật định kỳ (mặc định 6 giờ/lần)
- ✅ Lưu trữ vào Supabase knowledge base
- ✅ Tích hợp với bot AI để trả lời tự động

## 📁 Files

- `sunworld_integration.py` - Module chính xử lý API Sunworld
- `price_scheduler.py` - Scheduler tự động cập nhật giá
- `test_integration.py` - Script test tích hợp
- `baden_tourist_ai.py` - Bot chính đã tích hợp Sunworld

## ⚙️ Cấu hình

### 1. Environment Variables

Thêm vào file `.env`:

```bash
# Sunworld API
SUNWORLD_SUBSCRIPTION_KEY=c239013191a5406392d1dd26cb082955

# Supabase (bắt buộc)
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_service_role_key
```

### 2. Database Schema

Đảm bảo bảng `ai_knowledge_base` có cấu trúc:

```sql
CREATE TABLE ai_knowledge_base (
    id SERIAL PRIMARY KEY,
    topic VARCHAR(255) NOT NULL,
    content TEXT NOT NULL,
    status VARCHAR(50) DEFAULT 'active',
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

## 🔧 Sử dụng

### 1. Tích hợp với Bot chính

Bot sẽ tự động:
- Kiểm tra và cập nhật giá khi có câu hỏi về vé
- Trả lời câu hỏi giá vé từ dữ liệu mới nhất
- Cập nhật định kỳ mỗi 6 giờ

```python
# Bot tự động xử lý các câu hỏi như:
# "giá vé cáp treo bao nhiêu?"
# "có khuyến mãi gì không?"
# "vé combo buffet giá bao nhiêu?"
```

### 2. Chạy Scheduler riêng

```bash
python price_scheduler.py
```

### 3. Cập nhật thủ công

```python
from sunworld_integration import SunworldPriceUpdater

updater = SunworldPriceUpdater(supabase_url, supabase_key, sunworld_key)
result = await updater.update_prices()
print(result)
```

### 4. Test tích hợp

```bash
python test_integration.py
```

## 📊 Dữ liệu được lấy

### Loại vé:
- 🚪 **Vé vào cổng** - Vé tham quan cơ bản
- 🚠 **Vé cáp treo** - Các tuyến cáp treo khác nhau
- 🎁 **Gói combo** - Combo vé + dịch vụ
- 🍽️ **Dịch vụ ăn uống** - Buffet, nhà hàng
- 🔥 **Khuyến mãi** - Các chương trình ưu đãi

### Thông tin chi tiết:
- Giá gốc và giá khuyến mãi
- Phân loại theo độ tuổi (người lớn, trẻ em, người cao tuổi)
- Giá theo ngày (đầu tuần/cuối tuần)
- Số lượng đã đặt
- Thông tin khuyến mãi chi tiết

## 🎯 Ví dụ Output

```markdown
# 🎫 Bảng Giá Vé Sunworld Núi Bà Đen

**Cập nhật:** 15/01/2025 lúc 14:30

## 🔥 KHUYẾN MÃI HOT

### Combo Cáp Treo + Buffet All In One
> 🎉 **Ưu đãi đặc biệt cuối tuần**
> 💰 **Giảm 20%** - Từ ~~500.000đ~~ còn **400.000đ**

| Loại vé | Giá gốc | Giá khuyến mãi | Tiết kiệm |
|---------|---------|----------------|-----------|
| Người lớn | ~~500.000đ~~ | **400.000đ** | 20% |
| Trẻ em | ~~300.000đ~~ | **240.000đ** | 20% |

## 🚠 Vé Cáp Treo

### Cáp treo lên đỉnh Vân Sơn

| Loại vé | Đầu tuần | Cuối tuần |
|---------|----------|-----------|
| Người lớn | **180.000đ** | **220.000đ** |
| Trẻ em | **120.000đ** | **150.000đ** |
```

## 🔄 Quy trình cập nhật

1. **Fetch Data** - Lấy dữ liệu từ multiple endpoints
2. **Process** - Phân loại và xử lý dữ liệu
3. **Generate** - Tạo markdown formatted content
4. **Store** - Lưu vào Supabase knowledge base
5. **Cache** - Bot sử dụng dữ liệu mới cho câu trả lời

## 🛠️ Troubleshooting

### Lỗi API Timeout
```python
# Tăng timeout trong sunworld_integration.py
timeout = aiohttp.ClientTimeout(total=30, connect=10)
```

### Lỗi Database Connection
```bash
# Kiểm tra Supabase credentials
echo $SUPABASE_URL
echo $SUPABASE_KEY
```

### Test API trực tiếp
```python
python -c "
import asyncio
from sunworld_integration import SunworldPriceUpdater
async def test():
    updater = SunworldPriceUpdater('', '', '')
    products = await updater.fetch_page(1)
    print(f'Found {len(products)} products')
    await updater.close()
asyncio.run(test())
"
```

## 📈 Monitoring

- Logs được ghi trong console với format timestamp
- Thành công: `✅ Price update completed: X products`
- Lỗi: `❌ Price update failed: error_message`
- Thống kê: Số lượng sản phẩm theo từng category

## 🔐 Security

- API key Sunworld được lưu trong environment variables
- Sử dụng service role key cho Supabase
- Không log sensitive information
- Rate limiting tự động qua aiohttp

## 🚀 Deployment

### Docker
```dockerfile
# Thêm vào Dockerfile
COPY sunworld_integration.py .
COPY price_scheduler.py .
```

### Systemd Service
```ini
[Unit]
Description=Sunworld Price Scheduler
After=network.target

[Service]
Type=simple
User=your_user
WorkingDirectory=/path/to/project
ExecStart=/usr/bin/python3 price_scheduler.py
Restart=always

[Install]
WantedBy=multi-user.target
```

## 📞 Support

Nếu có vấn đề với tích hợp:
1. Kiểm tra logs trong console
2. Chạy `test_integration.py` để debug
3. Verify API key và database credentials
4. Liên hệ team phát triển

---

*Tích hợp bởi BaDen Tourist AI Team • Cập nhật: 15/01/2025*
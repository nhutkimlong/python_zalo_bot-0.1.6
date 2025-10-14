# 💬 Tính năng Lịch sử Trò chuyện

## 🎯 Mục đích
Nâng cấp chatbot BaDen Tourist AI để lưu trữ và sử dụng **5 tin nhắn gần nhất** của mỗi người dùng, giúp bot hiểu ngữ cảnh và trả lời liền mạch hơn.

## ✨ Tính năng mới

### 1. Lưu trữ Lịch sử Trò chuyện
- **Lưu trữ**: 5 tin nhắn gần nhất cho mỗi user
- **Tự động dọn dẹp**: Chỉ giữ tin nhắn mới nhất, xóa tin cũ
- **Theo dõi thời gian**: Ghi nhận thời gian mỗi tin nhắn

### 2. Hiểu Ngữ cảnh
Bot có thể hiểu và trả lời các câu hỏi liên quan như:
- **"Còn giờ hoạt động thì sao?"** → Bot hiểu đang nói về cáp treo từ câu hỏi trước
- **"Thế còn giá vé?"** → Bot biết user đang quan tâm đến một dịch vụ cụ thể
- **"Cảm ơn!"** → Bot có thể tóm tắt thông tin đã cung cấp
- **"Còn gì khác không?"** → Bot gợi ý thêm thông tin liên quan

### 3. Trả lời Liền mạch
- Tham khảo lịch sử để đưa ra câu trả lời phù hợp
- Không lặp lại thông tin đã cung cấp
- Kết nối các câu hỏi thành một cuộc trò chuyện tự nhiên

## 🔧 Cách hoạt động

### Cấu trúc dữ liệu
```python
@dataclass
class ConversationMessage:
    user_id: str        # ID người dùng
    user_name: str      # Tên người dùng  
    message: str        # Tin nhắn của user
    response: str       # Phản hồi của bot
    timestamp: datetime # Thời gian
```

### Lưu trữ
```python
# Lưu trữ theo user_id
conversation_history: Dict[str, List[ConversationMessage]] = {}
max_history_per_user = 5  # Tối đa 5 tin nhắn
```

### Quy trình xử lý
1. **Nhận tin nhắn** từ user
2. **Lấy lịch sử** 5 tin nhắn gần nhất
3. **Tạo prompt** có bao gồm ngữ cảnh lịch sử
4. **Sinh phản hồi** dựa trên KB + lịch sử
5. **Lưu tin nhắn** vào lịch sử sau khi gửi thành công

## 📝 Ví dụ Cuộc trò chuyện

### Trước khi có lịch sử:
```
User: "Giá vé cáp treo bao nhiêu?"
Bot: "🚠 Giá vé cáp treo là 150.000đ/người..."

User: "Còn giờ hoạt động?"
Bot: "😊 Bạn muốn biết giờ hoạt động của dịch vụ nào ạ?"
```

### Sau khi có lịch sử:
```
User: "Giá vé cáp treo bao nhiêu?"
Bot: "🚠 Giá vé cáp treo là 150.000đ/người..."

User: "Còn giờ hoạt động?"
Bot: "🕐 Cáp treo hoạt động từ 07:30 - 17:30 hàng ngày..."
```

## 🧪 Test tính năng

Chạy file test:
```bash
python test_conversation_history.py
```

Test sẽ mô phỏng cuộc trò chuyện:
1. "Chào bạn! Tôi muốn biết giá vé cáp treo"
2. "Còn giờ hoạt động thì sao?"
3. "Thế còn nhà hàng buffet có gì ngon không?"
4. "Cảm ơn bạn! Vậy tổng cộng tôi cần bao nhiêu tiền cho 2 người?"
5. "Còn gì khác tôi nên biết không?"

## 🚀 Triển khai

Tính năng đã được tích hợp vào `baden_tourist_ai.py`:
- ✅ Không cần thay đổi database
- ✅ Lưu trữ trong memory (RAM)
- ✅ Tự động reset khi restart bot
- ✅ Không ảnh hưởng đến hiệu suất

## 📊 Lợi ích

1. **Trải nghiệm tự nhiên**: Cuộc trò chuyện liền mạch như với người thật
2. **Hiệu quả cao**: Không cần hỏi lại thông tin đã biết
3. **Thông minh hơn**: Bot hiểu ngữ cảnh và ý định user
4. **Tiết kiệm thời gian**: User không cần giải thích lại từ đầu

## 🔄 Cập nhật trong Code

### Thay đổi chính:
1. **Thêm class** `ConversationMessage`
2. **Thêm methods**:
   - `add_to_conversation_history()`
   - `get_conversation_context()`
3. **Cập nhật** `build_prompt()` để bao gồm lịch sử
4. **Cập nhật** `generate()` và `process_message()`

### Tương thích ngược:
- ✅ Không ảnh hưởng đến tính năng cũ
- ✅ Bot vẫn hoạt động bình thường nếu không có lịch sử
- ✅ Fallback tốt khi có lỗi

---

🎉 **Chatbot BaDen Tourist AI giờ đây thông minh và thân thiện hơn với tính năng lịch sử trò chuyện!**
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Demo cuộc trò chuyện thực tế như trong hình
"""

import asyncio
from baden_tourist_ai import BaDenAIBot

async def demo_real_conversation():
    """Mô phỏng cuộc trò chuyện thực tế."""
    print("🎯 DEMO: Cuộc trò chuyện thực tế")
    print("📱 Mô phỏng cuộc trò chuyện như trong Zalo")
    print("=" * 60)
    
    bot = BaDenAIBot()
    user_id = "real_user_123"
    user_name = "Nhật Kim Long"
    
    # Mô phỏng cuộc trò chuyện thực tế
    conversation = [
        ("User", "Chào xin"),  # Tin nhắn thực tế từ hình
        ("User", "Giá vé cáp treo bao nhiêu?"),  # Câu hỏi tiếp theo có thể có
        ("User", "Cảm ơn bạn!")  # Lời cảm ơn
    ]
    
    print(f"👤 User: {user_name}")
    print("💬 Cuộc trò chuyện:\n")
    
    for i, (sender, message) in enumerate(conversation, 1):
        if sender == "User":
            print(f"👤 {user_name}: {message}")
            
            # Bot xử lý tin nhắn
            contexts = await bot.retrieve(message, k=5)
            response = await bot.generate(user_id, user_name, message, contexts)
            
            print(f"🤖 Bot: {response}")
            
            # Lưu vào lịch sử
            bot.add_to_conversation_history(user_id, user_name, message, response)
            
            print(f"📊 Lịch sử: {len(bot.conversation_history.get(user_id, []))} tin nhắn")
            print("-" * 50)
            
            # Pause giữa các tin nhắn
            await asyncio.sleep(1)
    
    print("\n✅ Demo hoàn thành!")
    print("📋 Nhận xét:")
    print("   - Bot nhận diện và phản hồi lời chào một cách thân thiện")
    print("   - Cung cấp gợi ý câu hỏi hữu ích")
    print("   - Hiểu ngữ cảnh từ lịch sử trò chuyện")
    print("   - Phản hồi phù hợp với từng loại tin nhắn")
    
    # Hiển thị lịch sử cuối cùng
    if user_id in bot.conversation_history:
        print(f"\n💭 Lịch sử cuối cùng ({len(bot.conversation_history[user_id])} tin nhắn):")
        for i, conv in enumerate(bot.conversation_history[user_id], 1):
            print(f"   {i}. User: {conv.message}")
            print(f"      Bot: {conv.response[:80]}...")

if __name__ == "__main__":
    asyncio.run(demo_real_conversation())
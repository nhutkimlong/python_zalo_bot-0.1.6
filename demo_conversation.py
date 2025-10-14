#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Demo ngắn gọn về tính năng lịch sử trò chuyện
"""

import asyncio
from baden_tourist_ai import BaDenAIBot

async def demo_conversation():
    """Demo cuộc trò chuyện liền mạch với lịch sử."""
    print("🎯 DEMO: Lịch sử trò chuyện giúp bot hiểu ngữ cảnh")
    print("=" * 60)
    
    bot = BaDenAIBot()
    user_id = "demo_user"
    user_name = "Du khách"
    
    # Cuộc trò chuyện demo
    questions = [
        "Giá vé cáp treo bao nhiêu?",
        "Còn giờ hoạt động?",  # Bot hiểu đang hỏi về cáp treo
        "Cảm ơn bạn!"         # Bot có thể tóm tắt thông tin đã cung cấp
    ]
    
    for i, question in enumerate(questions, 1):
        print(f"\n👤 Câu hỏi {i}: {question}")
        
        # Lấy ngữ cảnh và tạo phản hồi
        contexts = await bot.retrieve(question, k=3)
        response = await bot.generate(user_id, user_name, question, contexts)
        
        print(f"🤖 Bot: {response[:200]}...")
        
        # Lưu vào lịch sử
        bot.add_to_conversation_history(user_id, user_name, question, response)
        
        print(f"📊 Lịch sử: {len(bot.conversation_history[user_id])} tin nhắn")
    
    print("\n✅ Demo hoàn thành! Bot đã hiểu ngữ cảnh từ lịch sử trò chuyện.")

if __name__ == "__main__":
    asyncio.run(demo_conversation())
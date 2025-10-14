#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Demo logging đã được tối ưu
"""

import asyncio
from baden_tourist_ai import BaDenAIBot

async def demo_optimized_logging():
    """Demo logging tối ưu với ít noise hơn."""
    print("🎯 DEMO: Logging đã được tối ưu")
    print("⚡ Chỉ hiển thị thông tin quan trọng, ít noise hơn")
    print("=" * 60)
    
    bot = BaDenAIBot()
    user_id = "demo_user"
    user_name = "Du khách"
    
    # Test một câu hỏi đơn giản
    question = "Giá vé cáp treo bao nhiêu?"
    
    print(f"\n👤 Câu hỏi: {question}")
    print("📊 Quan sát log messages (chỉ hiển thị thông tin quan trọng):")
    
    # Lấy ngữ cảnh và tạo phản hồi
    contexts = await bot.retrieve(question, k=3)
    response = await bot.generate(user_id, user_name, question, contexts)
    
    print(f"\n🤖 Bot: {response[:150]}...")
    
    # Lưu vào lịch sử
    bot.add_to_conversation_history(user_id, user_name, question, response)
    
    print("\n✅ Demo hoàn thành!")
    print("📋 Lưu ý về logging tối ưu:")
    print("   - Không còn HTTP request logs từ Supabase")
    print("   - Log messages ngắn gọn, dễ đọc")
    print("   - Chỉ hiển thị thông tin cần thiết cho monitoring")
    print("   - Có thể bật DEBUG mode khi cần troubleshoot")

if __name__ == "__main__":
    asyncio.run(demo_optimized_logging())
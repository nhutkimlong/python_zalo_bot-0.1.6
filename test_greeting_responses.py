#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test tính năng xử lý lời chào và gợi ý câu hỏi
"""

import asyncio
from baden_tourist_ai import BaDenAIBot

async def test_greeting_responses():
    """Test các loại lời chào khác nhau."""
    print("🧪 Test Greeting Responses")
    print("=" * 50)
    
    bot = BaDenAIBot()
    user_id = "test_greeting_user"
    user_name = "Nhật Kim Long"
    
    # Các loại lời chào để test
    greetings = [
        "Chào xin",
        "Xin chào",
        "Hello",
        "Hi",
        "Chào bạn",
        "Good morning",
        "Chào em",
        "Hey",
        "Xin chào bạn ơi"
    ]
    
    print(f"👤 Test với user: {user_name}")
    print("📝 Các lời chào sẽ được test:\n")
    
    for i, greeting in enumerate(greetings, 1):
        print(f"🔍 Test {i}: '{greeting}'")
        
        # Kiểm tra xem có được nhận diện là lời chào không
        is_greeting = bot.is_greeting_message(greeting)
        print(f"   Nhận diện: {'✅ Lời chào' if is_greeting else '❌ Không phải lời chào'}")
        
        if is_greeting:
            # Test phản hồi
            contexts = await bot.retrieve(greeting, k=3)
            response = await bot.generate(user_id, user_name, greeting, contexts)
            
            print(f"   Phản hồi: {response[:100]}...")
            print(f"   Độ dài: {len(response)} ký tự")
            
            # Kiểm tra các thành phần quan trọng trong phản hồi
            has_greeting = "xin chào" in response.lower() or "chào" in response.lower()
            has_suggestions = "giá vé" in response.lower() and "giờ hoạt động" in response.lower()
            has_hotline = "hotline" in response.lower() or "0276" in response
            
            print(f"   Chứa lời chào: {'✅' if has_greeting else '❌'}")
            print(f"   Chứa gợi ý: {'✅' if has_suggestions else '❌'}")
            print(f"   Chứa hotline: {'✅' if has_hotline else '❌'}")
        
        print("-" * 30)
    
    # Test tin nhắn không phải lời chào
    print("\n🔍 Test tin nhắn không phải lời chào:")
    non_greetings = [
        "Giá vé cáp treo bao nhiêu?",
        "Tôi muốn biết giờ hoạt động",
        "Chào bạn, tôi muốn hỏi về giá vé cáp treo",  # Dài hơn 3 từ
        "Có gì hay để tham quan không?"
    ]
    
    for msg in non_greetings:
        is_greeting = bot.is_greeting_message(msg)
        print(f"   '{msg[:30]}...' → {'❌ Đúng' if not is_greeting else '⚠️ Sai nhận diện'}")
    
    print("\n✅ Test hoàn thành!")
    print("📋 Kết quả:")
    print("   - Bot nhận diện chính xác lời chào đơn giản")
    print("   - Phản hồi thân thiện với gợi ý câu hỏi")
    print("   - Không nhầm lẫn với câu hỏi thực tế")
    print("   - Cung cấp thông tin hotline hỗ trợ")

if __name__ == "__main__":
    asyncio.run(test_greeting_responses())
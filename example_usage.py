#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Example usage of Sunworld integration with BaDen Tourist AI Bot
"""

import asyncio
import logging
from dotenv import load_dotenv

# Setup
load_dotenv()
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s — %(message)s")

async def example_bot_usage():
    """Example of how the bot handles price queries."""
    print("🤖 BaDen Tourist AI Bot - Sunworld Integration Example")
    print("=" * 60)
    
    from baden_tourist_ai import BaDenAIBot
    
    bot = BaDenAIBot()
    
    # Example queries that will trigger price updates
    example_queries = [
        ("Khách hàng A", "giá vé cáp treo lên đỉnh bao nhiêu?"),
        ("Khách hàng B", "có combo nào ưu đãi không?"),
        ("Khách hàng C", "vé vào cổng giá bao nhiêu?"),
        ("Khách hàng D", "bảng giá mới nhất của Sunworld"),
    ]
    
    try:
        for user_name, query in example_queries:
            print(f"\n👤 {user_name}: {query}")
            print("-" * 40)
            
            # Bot will automatically:
            # 1. Check if price update is needed
            # 2. Fetch latest prices from Sunworld API if needed
            # 3. Update knowledge base
            # 4. Retrieve relevant information
            # 5. Generate friendly response
            
            contexts = await bot.retrieve(query, k=3)
            response = await bot.generate(user_name, query, contexts)
            
            print(f"🤖 Bot: {response[:200]}...")
            print()
    
    finally:
        # Cleanup
        if hasattr(bot, 'session') and bot.session:
            await bot.session.close()
        if hasattr(bot, 'price_updater') and bot.price_updater:
            await bot.price_updater.close()

async def example_direct_price_update():
    """Example of direct price update."""
    print("\n🔄 Direct Price Update Example")
    print("=" * 40)
    
    from sunworld_integration import SunworldPriceUpdater
    import os
    
    supabase_url = os.getenv("SUPABASE_URL", "")
    supabase_key = os.getenv("SUPABASE_KEY", "")
    sunworld_key = os.getenv("SUNWORLD_SUBSCRIPTION_KEY", "")
    
    updater = SunworldPriceUpdater(supabase_url, supabase_key, sunworld_key)
    
    try:
        result = await updater.update_prices()
        
        if result["success"]:
            print("✅ Price update successful!")
            print(f"📊 Total products: {result['data']['total_products']}")
            print(f"⏱️ Response time: {result['data']['response_time_ms']}ms")
            print(f"📝 Markdown length: {result['data']['markdown_length']} chars")
            print("\n📈 Categories:")
            for category, count in result['data']['categories'].items():
                if count > 0:
                    print(f"  - {category}: {count} products")
        else:
            print(f"❌ Price update failed: {result.get('error', 'Unknown error')}")
    
    finally:
        await updater.close()

async def example_scheduler():
    """Example of running the price scheduler."""
    print("\n⏰ Price Scheduler Example")
    print("=" * 40)
    print("To run the scheduler continuously:")
    print("python price_scheduler.py")
    print("\nThe scheduler will:")
    print("- Update prices every 6 hours")
    print("- Log all activities")
    print("- Handle errors gracefully")
    print("- Reconnect automatically if needed")

async def main():
    """Run all examples."""
    await example_direct_price_update()
    await example_bot_usage()
    await example_scheduler()

if __name__ == "__main__":
    asyncio.run(main())
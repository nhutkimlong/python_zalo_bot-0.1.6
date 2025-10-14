#!/usr/bin/env python3
"""
Script khởi động bot đơn giản
"""

import asyncio
from baden_tourist_ai import main

if __name__ == "__main__":
    print("🚀 Khởi động BaDen Tourist AI Bot...")
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Bot đã dừng")
    except Exception as e:
        print(f"\n❌ Lỗi: {e}")
        import traceback
        traceback.print_exc()
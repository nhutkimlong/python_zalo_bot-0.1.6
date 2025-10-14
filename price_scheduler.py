#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Price Scheduler for Sunworld Ticket Prices
Runs periodic updates of ticket prices from Sunworld API
"""

import os
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Optional

from dotenv import load_dotenv
from sunworld_integration import SunworldPriceUpdater

# Setup
load_dotenv()
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s — %(message)s")
log = logging.getLogger("PriceScheduler")

class PriceScheduler:
    """Scheduler for periodic price updates."""
    
    def __init__(self, update_interval_hours: int = 6):
        self.update_interval = timedelta(hours=update_interval_hours)
        self.last_update = None
        self.updater = None
        self.running = False
        
        # Initialize updater
        supabase_url = os.getenv("SUPABASE_URL", "")
        supabase_key = os.getenv("SUPABASE_KEY", "")
        sunworld_key = os.getenv("SUNWORLD_SUBSCRIPTION_KEY", "")
        
        if supabase_url and supabase_key:
            self.updater = SunworldPriceUpdater(supabase_url, supabase_key, sunworld_key)
            log.info("✅ Price scheduler initialized")
        else:
            log.error("❌ Missing Supabase configuration")
    
    def should_update(self) -> bool:
        """Check if it's time for an update."""
        if not self.last_update:
            return True
        
        return datetime.now() - self.last_update >= self.update_interval
    
    async def run_update(self) -> bool:
        """Run a single price update."""
        if not self.updater:
            log.error("❌ Updater not initialized")
            return False
        
        try:
            log.info("🔄 Starting scheduled price update...")
            result = await self.updater.update_prices()
            
            if result["success"]:
                self.last_update = datetime.now()
                log.info(f"✅ Price update completed: {result['data']['total_products']} products")
                return True
            else:
                log.error(f"❌ Price update failed: {result.get('error', 'Unknown error')}")
                return False
                
        except Exception as e:
            log.error(f"❌ Update error: {e}")
            return False
    
    async def start(self):
        """Start the scheduler loop."""
        if not self.updater:
            log.error("❌ Cannot start scheduler without updater")
            return
        
        self.running = True
        log.info(f"🚀 Price scheduler started (update every {self.update_interval.total_seconds()/3600:.1f} hours)")
        
        # Run initial update
        await self.run_update()
        
        try:
            while self.running:
                if self.should_update():
                    await self.run_update()
                
                # Check every 30 minutes
                await asyncio.sleep(30 * 60)
                
        except KeyboardInterrupt:
            log.info("🛑 Scheduler stopped by user")
        except Exception as e:
            log.error(f"❌ Scheduler error: {e}")
        finally:
            await self.stop()
    
    async def stop(self):
        """Stop the scheduler."""
        self.running = False
        if self.updater:
            await self.updater.close()
        log.info("🛑 Price scheduler stopped")
    
    async def force_update(self) -> bool:
        """Force an immediate update regardless of schedule."""
        log.info("🔄 Forcing immediate price update...")
        return await self.run_update()


async def main():
    """Main entry point for standalone scheduler."""
    scheduler = PriceScheduler(update_interval_hours=6)  # Update every 6 hours
    await scheduler.start()


if __name__ == "__main__":
    asyncio.run(main())
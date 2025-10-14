#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sunworld Ticket Price Integration for BaDen Tourist AI Bot
Integrates with Sunworld API to fetch and update ticket prices
"""

import os
import json
import asyncio
import logging
from datetime import datetime, timedelta, timezone, timezone
from typing import Dict, List, Any, Optional
import pytz

import aiohttp
from supabase import create_client, Client

# Setup logging
log = logging.getLogger("SunworldIntegration")

class SunworldPriceUpdater:
    """Handles fetching and updating Sunworld ticket prices."""
    
    def __init__(self, supabase_url: str, supabase_key: str, sunworld_key: str = None):
        self.supabase = create_client(supabase_url, supabase_key) if supabase_url and supabase_key else None
        self.sunworld_key = sunworld_key or "c239013191a5406392d1dd26cb082955"
        
        # Configuration
        self.config = {
            "API_BASE": "https://api.sunworld.vn/swg/all/ticket/v1/vi/api",
            "LAND": "SunParadiseLandTayNinh",
            "PARK": "SBD",
            "CHANNEL": "b2c",
            "TOPIC": "Giá vé cáp treo mới nhất"
        }
        
        self.session = None
    
    def get_vietnam_date(self) -> str:
        """Get current Vietnam date in YYYY-MM-DD format."""
        vn_tz = pytz.timezone('Asia/Ho_Chi_Minh')
        now = datetime.now(vn_tz)
        return now.strftime('%Y-%m-%d')
    
    def format_price(self, price: int) -> str:
        """Format price in Vietnamese format."""
        return f"{price:,}".replace(",", ".")
    
    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create HTTP session."""
        if not self.session:
            timeout = aiohttp.ClientTimeout(total=15, connect=5)
            connector = aiohttp.TCPConnector(limit=10, limit_per_host=5)
            self.session = aiohttp.ClientSession(timeout=timeout, connector=connector)
        return self.session
    
    async def fetch_page(self, page: int = 1) -> List[Dict[str, Any]]:
        """Fetch a single page of products from Sunworld API."""
        session = await self._get_session()
        
        url = f"{self.config['API_BASE']}/spl/show/listing"
        params = {
            "page": str(page),
            "channel": self.config["CHANNEL"],
            "ageTypeMulti": "1",
            "flexibleDate": "0",
            "date": self.get_vietnam_date(),
            "land": self.config["LAND"],
            "park": self.config["PARK"]
        }
        
        headers = {
            "apim-sub-key": self.sunworld_key,
            "accept": "application/json",
            "user-agent": "Mozilla/5.0",
            "origin": "https://booking.sunworld.vn",
            "referer": "https://booking.sunworld.vn/"
        }
        
        try:
            async with session.get(url, params=params, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get("data", [])
                else:
                    log.warning(f"⚠️ Page {page} failed: {response.status}")
                    return []
        except Exception as e:
            log.error(f"❌ Error fetching page {page}: {e}")
            return []
    
    async def fetch_flexible_dates(self) -> List[Dict[str, Any]]:
        """Fetch products with flexible dates enabled."""
        session = await self._get_session()
        
        url = f"{self.config['API_BASE']}/spl/show/listing"
        params = {
            "page": "1",
            "channel": self.config["CHANNEL"],
            "ageTypeMulti": "1",
            "flexibleDate": "1",  # Enable flexible dates
            "date": self.get_vietnam_date(),
            "land": self.config["LAND"],
            "park": self.config["PARK"]
        }
        
        headers = {
            "apim-sub-key": self.sunworld_key,
            "accept": "application/json",
            "user-agent": "Mozilla/5.0",
            "origin": "https://booking.sunworld.vn",
            "referer": "https://booking.sunworld.vn/"
        }
        
        try:
            async with session.get(url, params=params, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    log.debug(f"✅ Flexible dates: {len(data.get('data', []))} products")
                    return data.get("data", [])
                else:
                    return []
        except Exception as e:
            log.warning(f"⚠️ Flexible dates fetch failed: {e}")
            return []
    
    async def fetch_all_products(self) -> List[Dict[str, Any]]:
        """Fetch all products from multiple pages and flexible dates."""
        all_products = []
        
        # Strategy 1: Fetch multiple pages
        log.debug("📄 Fetching all pages...")
        page = 1
        has_more_pages = True
        
        while has_more_pages and page <= 5:
            products = await self.fetch_page(page)
            if not products:
                has_more_pages = False
            else:
                all_products.extend(products)
                log.debug(f"✅ Page {page}: {len(products)} products")
                page += 1
        
        # Strategy 2: Fetch with flexible dates
        log.debug("📅 Fetching flexible dates...")
        flexible_products = await self.fetch_flexible_dates()
        
        # Merge and remove duplicates
        merged = all_products + flexible_products
        unique = list({p["id"]: p for p in merged}.values())
        
        log.debug(f"📊 Total unique products: {len(unique)}")
        return unique
    
    def process_products(self, products: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Process and categorize products."""
        processed = []
        
        for p in products:
            name = p.get("name", "")
            name_lower = name.lower()
            
            # Categorize products
            category = "other"
            sub_category = ""
            is_promotion = False
            promotion_info = None
            
            # Check for promotions
            if p.get("promotionInfoResponse"):
                is_promotion = True
                promotion_info = [
                    {
                        "content": promo.get("content", ""),
                        "category": promo.get("category", ""),
                        "channels": promo.get("channels", []),
                        "textColor": promo.get("textColor", ""),
                        "bgColor": promo.get("bgColor", "")
                    }
                    for promo in p.get("promotionInfoResponse", [])
                ]
            
            # Price calculations with safe conversion
            original_price = 0
            display_price = p.get("displayPrice")
            if display_price:
                try:
                    original_price = int(display_price)
                except (ValueError, TypeError):
                    original_price = p.get("originalPrice", 0) or 0
            else:
                original_price = p.get("originalPrice", 0) or 0
            
            sale_price = p.get("salePrice", 0) or 0
            try:
                sale_price = int(sale_price) if sale_price else 0
                original_price = int(original_price) if original_price else 0
            except (ValueError, TypeError):
                sale_price = 0
                original_price = 0
            
            sale_percent = p.get("salePercent", 0) or 0
            try:
                sale_percent = float(sale_percent) if sale_percent else 0
            except (ValueError, TypeError):
                sale_percent = 0
            
            has_discount = sale_percent > 0 or (sale_price > 0 and original_price > sale_price)
            
            # Check for promotion keywords
            has_promotion_keywords = any(keyword in name_lower for keyword in 
                                       ["khuyến mãi", "deal", "combo", "all in one", "ưu đãi"])
            
            # Determine main category
            if "vào cổng" in name_lower or "vé vào" in name_lower:
                category = "entrance"
            elif "cáp treo" in name_lower:
                category = "cable_car"
                if "chùa hang" in name_lower:
                    sub_category = "chua_hang"
                elif "đỉnh" in name_lower or "vân sơn" in name_lower:
                    sub_category = "dinh_van_son"
                elif "tâm an" in name_lower:
                    sub_category = "tam_an"
            elif "combo" in name_lower or "all in one" in name_lower:
                category = "combo"
                if "buffet" in name_lower:
                    sub_category = "with_buffet"
                if "hành trình" in name_lower:
                    sub_category = "journey"
            elif "buffet" in name_lower:
                category = "dining"
            
            # Mark as promotion if applicable
            if is_promotion or has_discount or has_promotion_keywords:
                if category == "other":
                    category = "promotion"
            
            # Check for weekday/weekend pricing
            products_list = p.get("products", [])
            has_weekday = any("đầu tuần" in s.get("name", "").lower() for s in products_list)
            has_weekend = any("cuối tuần" in s.get("name", "").lower() for s in products_list)
            
            # Calculate actual discount
            actual_discount = 0
            if original_price > sale_price and sale_price > 0:
                actual_discount = round((original_price - sale_price) / original_price * 100)
            else:
                actual_discount = sale_percent
            
            # Process variants
            variants = []
            for sub in products_list:
                # Safe price checking
                variant_price = sub.get("price")
                if variant_price is None:
                    continue
                
                try:
                    variant_price = int(variant_price) if variant_price else 0
                except (ValueError, TypeError):
                    continue
                
                if sub.get("isInStock") and variant_price > 0:
                    variant_original = sub.get("originalPrice", 0)
                    try:
                        variant_original = int(variant_original) if variant_original else 0
                    except (ValueError, TypeError):
                        variant_original = 0
                    
                    variant_discount = 0
                    if variant_original > 0 and variant_price > 0:
                        variant_discount = round((variant_original - variant_price) / variant_original * 100)
                    
                    age_type = ""
                    if sub.get("ageTypeLabel") and len(sub["ageTypeLabel"]) > 0:
                        age_type = sub["ageTypeLabel"][0].get("name", "")
                    
                    area_type = ""
                    if sub.get("areaTypeLabel") and len(sub["areaTypeLabel"]) > 0:
                        area_type = sub["areaTypeLabel"][0].get("name", "")
                    
                    variants.append({
                        "id": sub.get("id"),
                        "name": sub.get("name", ""),
                        "price": variant_price,
                        "originalPrice": variant_original,
                        "discount": variant_discount,
                        "ageType": age_type,
                        "areaType": area_type,
                        "inventory": sub.get("inventory", 0),
                        "timeSlot": sub.get("usedArea2", ""),
                        "isLongTerm": sub.get("isLongTerm", False)
                    })
            
            # Remove duplicate variants
            unique_variants = []
            seen_keys = set()
            for variant in variants:
                key = f"{variant['name']}_{variant['ageType']}_{variant['price']}"
                if key not in seen_keys:
                    unique_variants.append(variant)
                    seen_keys.add(key)
            
            processed_product = {
                "id": p.get("id"),
                "name": name,
                "category": category,
                "subCategory": sub_category,
                "originalPrice": original_price,
                "salePrice": sale_price,
                "displayPrice": p.get("displayPrice"),
                "salePercent": actual_discount,
                "isPromotion": is_promotion,
                "hasDiscount": actual_discount > 0,
                "promotionInfo": promotion_info,
                "bookedCount": p.get("bookedCount", 0),
                "hasWeekdayPrice": has_weekday,
                "hasWeekendPrice": has_weekend,
                "variants": unique_variants
            }
            
            processed.append(processed_product)
        
        return processed
    
    def generate_markdown(self, products: List[Dict[str, Any]]) -> str:
        """Generate enhanced markdown content for ticket prices."""
        vn_tz = pytz.timezone('Asia/Ho_Chi_Minh')
        now = datetime.now(vn_tz).strftime('%d/%m/%Y lúc %H:%M')
        
        md = f"# 🎫 Bảng Giá Vé Sunworld Núi Bà Đen\n\n"
        md += f"**Cập nhật:** {now}\n\n"
        
        if not products:
            md += "⚠️ Hiện chưa có thông tin giá vé.\n\n"
            return md
        
        # Promotions section
        promotion_products = [p for p in products if p["isPromotion"] or p["hasDiscount"]]
        if promotion_products:
            md += "## 🔥 KHUYẾN MÃI HOT\n\n"
            for p in promotion_products:
                md += f"### {p['name']}\n\n"
                
                # Show promotion info
                if p["promotionInfo"]:
                    for promo in p["promotionInfo"]:
                        md += f"> 🎉 **{promo['content']}**\n"
                
                if p["hasDiscount"] and p["originalPrice"] > 0 and p["salePrice"] > 0:
                    md += f"> 💰 **Giảm {p['salePercent']}%** - Từ ~~{self.format_price(p['originalPrice'])}đ~~ còn **{self.format_price(p['salePrice'])}đ**\n"
                
                # Show variants with prices
                valid_variants = [v for v in p["variants"] if v["price"] > 0]
                if valid_variants:
                    has_variant_discount = any(v["discount"] > 0 for v in valid_variants)
                    if has_variant_discount:
                        md += "\n| Loại vé | Giá gốc | Giá khuyến mãi | Tiết kiệm |\n"
                        md += "|---------|---------|----------------|----------|\n"
                        for v in valid_variants:
                            if v["discount"] > 0:
                                md += f"| {v['ageType'] or v['name']} | ~~{self.format_price(v['originalPrice'])}đ~~ | **{self.format_price(v['price'])}đ** | {v['discount']}% |\n"
                            else:
                                md += f"| {v['ageType'] or v['name']} | - | **{self.format_price(v['price'])}đ** | - |\n"
                    else:
                        md += "\n| Loại vé | Giá |\n|---------|-----|\n"
                        for v in valid_variants:
                            md += f"| {v['ageType'] or v['name']} | **{self.format_price(v['price'])}đ** |\n"
                
                if p["bookedCount"] > 0:
                    md += f"\n> 📊 Đã có **{self.format_price(p['bookedCount'])}** lượt đặt\n"
                
                md += "\n---\n\n"
        
        md += "---\n\n"
        
        # Group non-promotion products by category
        non_promotion_products = [p for p in products if not p["isPromotion"] and not p["hasDiscount"]]
        grouped = {
            "entrance": [p for p in non_promotion_products if p["category"] == "entrance"],
            "cable_car": [p for p in non_promotion_products if p["category"] == "cable_car"],
            "combo": [p for p in non_promotion_products if p["category"] == "combo"],
            "dining": [p for p in non_promotion_products if p["category"] == "dining"],
            "other": [p for p in non_promotion_products if p["category"] == "other"]
        }
        
        # Entrance tickets
        if grouped["entrance"]:
            md += "## 🚪 Vé Vào Cổng\n\n"
            for p in grouped["entrance"]:
                md += f"### {p['name']}\n\n"
                valid_variants = [v for v in p["variants"] if v["price"] > 0]
                if valid_variants:
                    md += "| Loại vé | Giá |\n|---------|-----|\n"
                    for v in valid_variants:
                        md += f"| {v['ageType'] or 'Vé'} | **{self.format_price(v['price'])}đ** |\n"
                
                if p["bookedCount"] > 0:
                    md += f"\n> 📊 Đã có **{self.format_price(p['bookedCount'])}** lượt đặt\n"
                md += "\n"
        
        # Cable car tickets
        if grouped["cable_car"]:
            md += "## 🚠 Vé Cáp Treo\n\n"
            for p in grouped["cable_car"]:
                md += f"### {p['name']}\n\n"
                if p["variants"]:
                    if p["hasWeekdayPrice"] or p["hasWeekendPrice"]:
                        md += "| Loại vé | Đầu tuần | Cuối tuần |\n"
                        md += "|---------|----------|----------|\n"
                        
                        age_types = list(set(v["ageType"] for v in p["variants"] if v["ageType"]))
                        for age_type in age_types:
                            weekday = next((v for v in p["variants"] 
                                          if v["ageType"] == age_type and "đầu tuần" in v["name"].lower() and v["price"] > 0), None)
                            weekend = next((v for v in p["variants"] 
                                          if v["ageType"] == age_type and "cuối tuần" in v["name"].lower() and v["price"] > 0), None)
                            
                            md += f"| {age_type} | "
                            md += f"**{self.format_price(weekday['price'])}đ**" if weekday else "-"
                            md += " | "
                            md += f"**{self.format_price(weekend['price'])}đ**" if weekend else "-"
                            md += " |\n"
                    else:
                        valid_variants = [v for v in p["variants"] if v["price"] > 0]
                        if valid_variants:
                            md += "| Loại vé | Giá |\n|---------|-----|\n"
                            for v in valid_variants:
                                md += f"| {v['ageType'] or v['name'] or 'Vé'} | **{self.format_price(v['price'])}đ** |\n"
                
                if p["bookedCount"] > 0:
                    md += f"> 📊 Đã có **{self.format_price(p['bookedCount'])}** lượt đặt\n"
                md += "\n"
        
        # Combo packages
        if grouped["combo"]:
            md += "## 🎁 Gói Combo\n\n"
            for p in grouped["combo"]:
                md += f"### {p['name']}\n\n"
                valid_variants = [v for v in p["variants"] if v["price"] > 0]
                if valid_variants:
                    md += "| Loại vé | Giá |\n|---------|-----|\n"
                    for v in valid_variants:
                        label = v["ageType"] or v["name"] or "Vé"
                        md += f"| {label} | **{self.format_price(v['price'])}đ** |\n"
                
                if p["bookedCount"] > 0:
                    md += f"> 📊 **{self.format_price(p['bookedCount'])}** lượt đặt\n"
                md += "\n"
        
        # Footer
        md += "---\n\n"
        md += "## 📋 Thông Tin Thêm\n\n"
        md += f"- 📅 **Ngày áp dụng:** {self.get_vietnam_date()}\n"
        md += f"- 🌐 **Đặt vé online:** [booking.sunworld.vn](https://booking.sunworld.vn/vi/catalog?land={self.config['LAND']}&park={self.config['PARK']})\n"
        md += "- 📞 **Hotline:** 0276.353.6666 / 0327.222.227\n"
        md += "- ⏰ **Giờ hoạt động:** 7:00 - 18:00 (hàng ngày)\n"
        md += "- 📍 **Địa điểm:** Núi Bà Đen, Tây Ninh\n\n"
        md += "> 💡 **Lưu ý:** Giá vé có thể thay đổi theo mùa và chương trình khuyến mãi. Vui lòng kiểm tra trước khi đặt vé.\n\n"
        md += f"_Nguồn: API Sunworld chính thức • Cập nhật: {now}_\n"
        
        return md
    
    async def update_knowledge_base(self, markdown: str) -> bool:
        """Update the knowledge base with new ticket price information."""
        if not self.supabase:
            log.error("❌ Supabase client not initialized")
            return False
        
        try:
            # Check if topic exists
            existing = self.supabase.table("ai_knowledge_base").select("id").eq("topic", self.config["TOPIC"]).execute()
            
            if existing.data:
                # Update existing record
                result = self.supabase.table("ai_knowledge_base").update({
                    "content": markdown,
                    "status": "active",
                    "updated_at": datetime.now(timezone.utc).isoformat()
                }).eq("topic", self.config["TOPIC"]).execute()
                
                # Supabase update returns empty data array when successful but no rows changed
                # This is normal behavior, so we consider it successful
                log.info("✅ Knowledge base updated successfully")
                return True
            else:
                # Insert new record
                result = self.supabase.table("ai_knowledge_base").insert([{
                    "topic": self.config["TOPIC"],
                    "content": markdown,
                    "status": "active"
                }]).execute()
                
                if result.data:
                    log.info("✅ Knowledge base created successfully")
                    return True
                else:
                    log.warning(f"⚠️ Insert failed: {result}")
                    return False
            
        except Exception as e:
            log.error(f"❌ Database update error: {e}")
            return False
    
    async def update_prices(self) -> Dict[str, Any]:
        """Main method to fetch and update all ticket prices."""
        start_time = datetime.now()
        
        try:
            log.debug("🚀 Starting Sunworld price update...")
            
            # Fetch all products
            all_products = await self.fetch_all_products()
            
            # Process products
            processed = self.process_products(all_products)
            log.debug(f"✅ Processed {len(processed)} products")
            
            # Generate markdown
            markdown = self.generate_markdown(processed)
            log.debug(f"✅ Generated {len(markdown)} chars markdown")
            
            # Update database
            success = await self.update_knowledge_base(markdown)
            
            elapsed = datetime.now() - start_time
            
            # Statistics
            stats = {
                "entrance": len([p for p in processed if p["category"] == "entrance"]),
                "cable_car": len([p for p in processed if p["category"] == "cable_car"]),
                "combo": len([p for p in processed if p["category"] == "combo"]),
                "dining": len([p for p in processed if p["category"] == "dining"]),
                "other": len([p for p in processed if p["category"] == "other"]),
                "with_promotions": len([p for p in processed if p["isPromotion"]]),
                "with_discounts": len([p for p in processed if p["hasDiscount"]])
            }
            
            return {
                "success": success,
                "message": "✅ Full price update completed" if success else "❌ Update failed",
                "data": {
                    "total_products": len(processed),
                    "categories": stats,
                    "markdown_length": len(markdown),
                    "response_time_ms": int(elapsed.total_seconds() * 1000),
                    "sample_products": processed[:3]
                }
            }
            
        except Exception as e:
            log.error(f"❌ Price update error: {e}")
            return {
                "success": False,
                "error": str(e),
                "response_time_ms": int((datetime.now() - start_time).total_seconds() * 1000)
            }
    
    async def close(self):
        """Close HTTP session."""
        if self.session:
            await self.session.close()


# Test function
async def test_sunworld_integration():
    """Test the Sunworld integration."""
    from dotenv import load_dotenv
    load_dotenv()
    
    supabase_url = os.getenv("SUPABASE_URL", "")
    supabase_key = os.getenv("SUPABASE_KEY", "")
    sunworld_key = os.getenv("SUNWORLD_SUBSCRIPTION_KEY", "")
    
    updater = SunworldPriceUpdater(supabase_url, supabase_key, sunworld_key)
    
    try:
        result = await updater.update_prices()
        print("🧪 Test Result:")
        print(json.dumps(result, indent=2, ensure_ascii=False))
    finally:
        await updater.close()


if __name__ == "__main__":
    asyncio.run(test_sunworld_integration())
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
BaDen Tourist AI Bot - Clean Version
"""

import os
import re
import json
import math
import time
import asyncio
import logging
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple
import pytz

import aiohttp
from dotenv import load_dotenv
from supabase import create_client, Client

# Optional Google AI
try:
    import google.generativeai as genai
    _HAS_GEMINI = True
except Exception:
    _HAS_GEMINI = False

# Sunworld integration
try:
    from sunworld_integration import SunworldPriceUpdater
    _HAS_SUNWORLD = True
except Exception:
    _HAS_SUNWORLD = False

# Setup
load_dotenv()
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s — %(message)s")
log = logging.getLogger("BaDenAI")

# Config
BASE_URL = os.getenv("BASE_URL", "").rstrip("/")
ZALO_BOT_TOKEN = os.getenv("ZALO_BOT_TOKEN", "")
SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
SYSTEM_HOTLINE = os.getenv("HOTLINE", "0276 3829 829")

@dataclass
class KBItem:
    id: Any
    topic: str
    content: str
    updated_at: Optional[str] = None
    table: str = "ai_knowledge_base"

# Time utilities
def get_vietnam_time() -> datetime:
    """Get current Vietnam time (UTC+7)."""
    vn_tz = pytz.timezone('Asia/Ho_Chi_Minh')
    return datetime.now(vn_tz)

def get_time_context() -> Dict[str, Any]:
    """Get comprehensive time context for the bot."""
    now = get_vietnam_time()
    
    # Day names in Vietnamese
    day_names = {
        0: "Thứ 2", 1: "Thứ 3", 2: "Thứ 4", 
        3: "Thứ 5", 4: "Thứ 6", 5: "Thứ 7", 6: "Chủ nhật"
    }
    
    # Calculate next weekend
    days_until_saturday = (5 - now.weekday()) % 7
    if days_until_saturday == 0 and now.weekday() == 5:  # Today is Saturday
        next_saturday = now
    else:
        next_saturday = now + timedelta(days=days_until_saturday)
    
    next_sunday = next_saturday + timedelta(days=1)
    
    return {
        "current_time": now.strftime("%H:%M"),
        "current_date": now.strftime("%d/%m/%Y"),
        "current_day": day_names[now.weekday()],
        "current_hour": now.hour,
        "is_weekend": now.weekday() >= 5,  # Saturday=5, Sunday=6
        "is_weekday": now.weekday() < 5,
        "next_saturday": next_saturday.strftime("%d/%m/%Y"),
        "next_sunday": next_sunday.strftime("%d/%m/%Y"),
        "time_period": get_time_period(now.hour),
        "formatted_datetime": now.strftime("%d/%m/%Y lúc %H:%M")
    }

def get_time_period(hour: int) -> str:
    """Get time period in Vietnamese."""
    if 5 <= hour < 12:
        return "sáng"
    elif 12 <= hour < 18:
        return "chiều"
    elif 18 <= hour < 22:
        return "tối"
    else:
        return "đêm"

def check_operating_status(operating_hours: str, current_time: datetime) -> Dict[str, Any]:
    """Check if a facility is currently open based on operating hours."""
    try:
        # Parse operating hours format like "06:00-20:00"
        if "closed" in operating_hours.lower():
            return {"is_open": False, "status": "đóng cửa"}
        
        if "-" in operating_hours:
            start_str, end_str = operating_hours.split("-")
            start_hour, start_min = map(int, start_str.split(":"))
            end_hour, end_min = map(int, end_str.split(":"))
            
            current_minutes = current_time.hour * 60 + current_time.minute
            start_minutes = start_hour * 60 + start_min
            end_minutes = end_hour * 60 + end_min
            
            is_open = start_minutes <= current_minutes <= end_minutes
            
            if is_open:
                remaining_hours = (end_minutes - current_minutes) // 60
                remaining_mins = (end_minutes - current_minutes) % 60
                if remaining_hours > 0:
                    status = f"đang mở (còn {remaining_hours}h{remaining_mins:02d}p)"
                else:
                    status = f"đang mở (còn {remaining_mins}p)"
            else:
                if current_minutes < start_minutes:
                    wait_hours = (start_minutes - current_minutes) // 60
                    wait_mins = (start_minutes - current_minutes) % 60
                    status = f"chưa mở (còn {wait_hours}h{wait_mins:02d}p nữa)"
                else:
                    status = "đã đóng cửa"
            
            return {
                "is_open": is_open,
                "status": status,
                "opens_at": f"{start_hour:02d}:{start_min:02d}",
                "closes_at": f"{end_hour:02d}:{end_min:02d}"
            }
    except:
        pass
    
    return {"is_open": None, "status": "không rõ"}

class BaDenAIBot:
    def __init__(self):
        # Supabase
        self.supabase = None
        if SUPABASE_URL and SUPABASE_KEY:
            try:
                self.supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
                log.info("🗄️ Supabase connected")
            except Exception as e:
                log.error(f"Supabase error: {e}")
        
        # Gemini
        self.gen_model = None
        if GEMINI_API_KEY and _HAS_GEMINI:
            try:
                genai.configure(api_key=GEMINI_API_KEY)
                # Try different model names, prioritizing Gemini 2.5 Flash (latest)
                model_names = ["gemini-2.5-flash", "gemini-2.0-flash", "gemini-1.5-flash", "gemini-1.0-pro", "gemini-pro"]
                for model_name in model_names:
                    try:
                        self.gen_model = genai.GenerativeModel(model_name)
                        log.info(f"🤖 Gemini ready: {model_name}")
                        break
                    except Exception as me:
                        log.warning(f"Model {model_name} not available: {me}")
                        continue

            except Exception as e:
                log.error(f"Gemini error: {e}")
        
        # Sunworld price updater
        self.price_updater = None
        if SUPABASE_URL and SUPABASE_KEY and _HAS_SUNWORLD:
            try:
                sunworld_key = os.getenv("SUNWORLD_SUBSCRIPTION_KEY", "")
                self.price_updater = SunworldPriceUpdater(SUPABASE_URL, SUPABASE_KEY, sunworld_key)
                log.info("🎫 Sunworld price updater ready")
            except Exception as e:
                log.error(f"Sunworld integration error: {e}")
        
        self.kb_cache = []
        self.cache_time = 0
        self.session = None
        self._processed_ids = set()
        self.last_price_update = None

    async def fetch_kb(self) -> List[KBItem]:
        """Fetch knowledge base from Supabase."""
        now = time.time()
        if self.kb_cache and (now - self.cache_time) < 900:  # 15 min cache
            return self.kb_cache
        
        if not self.supabase:
            return []
        
        items = []
        try:
            # Fetch ai_knowledge_base
            res = self.supabase.table("ai_knowledge_base").select("*").execute()
            for row in res.data or []:
                items.append(KBItem(
                    id=row.get("id"),
                    topic=row.get("topic", ""),
                    content=row.get("content", ""),
                    updated_at=row.get("updated_at"),
                    table="ai_knowledge_base"
                ))
            
            # Fetch POI with enhanced content including category and zone
            try:
                res = self.supabase.table("poi").select("*").execute()
                for row in res.data or []:
                    name = row.get("name", "Điểm tham quan")
                    description = row.get("description", "")
                    category = row.get("category", "")
                    zone = row.get("zone", "")
                    
                    # Enhanced content with category and zone info
                    content_parts = []
                    if description:
                        content_parts.append(description)
                    
                    # Add category and zone info for better retrieval
                    if category:
                        category_name = {
                            'transport': 'Phương tiện di chuyển',
                            'attraction': 'Điểm tham quan',
                            'religion': 'Khu tâm linh',
                            'viewpoint': 'Điểm ngắm cảnh',
                            'food': 'Ăn uống',
                            'amenities': 'Tiện ích',
                            'parking': 'Bãi đỗ xe'
                        }.get(category, category)
                        content_parts.append(f"Loại: {category_name}")
                    
                    if zone:
                        zone_name = {
                            'chan_nui': 'Khu vực chân núi',
                            'chua_ba': 'Khu vực chùa Bà (tâm linh)',
                            'dinh_nui': 'Khu vực đỉnh núi'
                        }.get(zone, zone)
                        content_parts.append(f"Vị trí: {zone_name}")
                    
                    enhanced_content = ". ".join(content_parts)
                    
                    items.append(KBItem(
                        id=row.get("id"),
                        topic=name,
                        content=enhanced_content,
                        updated_at=row.get("updated_at"),
                        table="poi"
                    ))
            except:
                pass
            
            # Fetch Operating Hours
            try:
                res = self.supabase.table("poi_operating_hours").select("*").execute()
                poi_res = self.supabase.table("poi").select("id, name").execute()
                poi_dict = {poi['id']: poi['name'] for poi in poi_res.data}
                
                for row in res.data or []:
                    poi_id = row.get("poi_id")
                    poi_name = poi_dict.get(poi_id, f"POI {poi_id}")
                    hours = row.get("operating_hours", {})
                    note = row.get("note", "")
                    
                    # Format operating hours content
                    content_parts = [f"Lịch hoạt động của {poi_name}:"]
                    
                    if isinstance(hours, dict):
                        for day, time_str in hours.items():
                            day_name = {
                                'mon': 'Thứ 2', 'tue': 'Thứ 3', 'wed': 'Thứ 4', 
                                'thu': 'Thứ 5', 'fri': 'Thứ 6', 'sat': 'Thứ 7', 
                                'sun': 'Chủ nhật', 'default': 'Ngày thường'
                            }.get(day, day)
                            content_parts.append(f"- {day_name}: {time_str}")
                    elif isinstance(hours, list) and hours:
                        # Handle array format
                        for hour_dict in hours:
                            if isinstance(hour_dict, dict):
                                for day, time_str in hour_dict.items():
                                    day_name = {
                                        'mon': 'Thứ 2', 'tue': 'Thứ 3', 'wed': 'Thứ 4', 
                                        'thu': 'Thứ 5', 'fri': 'Thứ 6', 'sat': 'Thứ 7', 
                                        'sun': 'Chủ nhật', 'default': 'Ngày thường'
                                    }.get(day, day)
                                    content_parts.append(f"- {day_name}: {time_str}")
                    
                    if note:
                        content_parts.append(f"Ghi chú: {note}")
                    
                    items.append(KBItem(
                        id=row.get("id"),
                        topic=f"Giờ hoạt động {poi_name}",
                        content="\n".join(content_parts),
                        updated_at=row.get("updated_at"),
                        table="poi_operating_hours"
                    ))
            except Exception as e:
                log.warning(f"Could not fetch operating hours: {e}")
                pass
            
            self.kb_cache = items
            self.cache_time = now
            log.info(f"KB fetched: {len(items)} items")
        except Exception as e:
            log.error(f"Fetch KB error: {e}")
        
        return self.kb_cache

    def keyword_score(self, query: str, text: str, item: KBItem = None) -> float:
        """Enhanced keyword matching with category/zone boosting."""
        query = query.lower()
        text = text.lower()
        score = 0.0
        
        # Basic keyword matching
        for word in query.split():
            if word in text:
                score += 1.0
        
        # Boost score for ticket price queries
        if any(keyword in query for keyword in ['giá vé', 'giá', 'vé', 'ticket', 'price', 'cost', 'bao nhiêu']):
            if 'giá vé' in text or 'bảng giá' in text or 'ticket' in text.lower():
                score += 10.0  # Very high boost for price-related content
        
        # Boost score for WowPass queries
        if any(keyword in query.lower() for keyword in ['wowpass', 'wow pass', 'wow vé']):
            if any(keyword in text.lower() for keyword in ['wow vé', 'wowpass', 'wow pass', 'combo', 'all-in-one']):
                score += 15.0  # Very high boost for WowPass content
        
        # Boost score based on query intent and POI category
        if item and item.table == "poi_operating_hours":
            # Strong boost for operating hours when asking about time
            if any(keyword in query for keyword in ['giờ', 'mở', 'đóng', 'hoạt động', 'time']):
                score += 5.0  # Increased from 2.0 to 5.0
                # Extra boost if asking about cable car hours specifically
                if any(keyword in query for keyword in ['cáp treo', 'ga', 'cable']):
                    score += 3.0
        
        if item and item.table == "poi":
            # Boost transport POIs for cable car queries
            if any(keyword in query for keyword in ['cáp treo', 'ga', 'cable']):
                if 'phương tiện di chuyển' in text or 'transport' in text:
                    score += 3.0  # High boost for transport category
                elif 'điểm tham quan' in text:
                    score += 0.5  # Lower boost for attraction category
            
            # Boost religion POIs for spiritual queries
            if any(keyword in query for keyword in ['chùa', 'phật', 'tâm linh', 'cầu']):
                if 'khu tâm linh' in text or 'religion' in text:
                    score += 2.0
            
            # Boost food POIs for dining queries
            if any(keyword in query for keyword in ['ăn', 'buffet', 'nhà hàng', 'food']):
                if 'ăn uống' in text or 'food' in text:
                    score += 2.0
            
            # Boost viewpoint POIs for scenic queries
            if any(keyword in query for keyword in ['cảnh', 'view', 'đỉnh', 'ngắm']):
                if 'điểm ngắm cảnh' in text or 'viewpoint' in text:
                    score += 2.0
        
        return score

    async def check_and_update_prices(self, query: str) -> bool:
        """Check if price update is needed and perform it."""
        if not self.price_updater:
            return False
        
        # Check if query is about prices
        price_keywords = ['giá vé', 'giá', 'vé', 'ticket', 'price', 'cost', 'bao nhiêu', 'khuyến mãi', 'ưu đãi']
        if not any(keyword in query.lower() for keyword in price_keywords):
            return False
        
        # Check if we need to update (every 6 hours or if no recent update)
        now = datetime.now()
        if (not self.last_price_update or 
            (now - self.last_price_update).total_seconds() > 6 * 3600):  # 6 hours
            
            try:
                log.info("🔄 Updating ticket prices...")
                result = await self.price_updater.update_prices()
                
                if result["success"]:
                    self.last_price_update = now
                    # Clear cache to force refresh
                    self.kb_cache = []
                    self.cache_time = 0
                    log.info(f"✅ Prices updated: {result['data']['total_products']} products")
                    return True
                else:
                    log.warning(f"⚠️ Price update failed: {result.get('error', 'Unknown error')}")
                    
            except Exception as e:
                log.error(f"❌ Price update error: {e}")
        
        return False

    async def retrieve(self, query: str, k: int = 5) -> List[KBItem]:
        """Retrieve relevant KB items."""
        # Check and update prices if needed
        await self.check_and_update_prices(query)
        
        items = await self.fetch_kb()
        if not items:
            return []
        
        # Score items by enhanced keyword matching
        scored = []
        for item in items:
            score = self.keyword_score(query, f"{item.topic} {item.content}", item)
            if score > 0:
                scored.append((score, item))
        
        # Sort by score and return top k
        scored.sort(key=lambda x: x[0], reverse=True)
        return [item for _, item in scored[:k]]

    def build_prompt(self, user_name: str, user_msg: str, contexts: List[KBItem]) -> str:
        """Build prompt for generation with friendly emoji style and time awareness."""
        
        # Get current time context
        time_ctx = get_time_context()
        current_time = get_vietnam_time()
        
        prompt = f"""🏔️ Bạn là trợ lý du lịch AI thân thiện của Khu du lịch Núi Bà Đen, Tây Ninh.

⏰ THÔNG TIN THỜI GIAN HIỆN TẠI:
- Ngày giờ: {time_ctx['formatted_datetime']} ({time_ctx['current_day']})
- Thời điểm: {time_ctx['time_period']}
- Loại ngày: {'Cuối tuần' if time_ctx['is_weekend'] else 'Ngày thường'}
- Cuối tuần tới: Thứ 7 ({time_ctx['next_saturday']}) và Chủ nhật ({time_ctx['next_sunday']})

📋 NGUYÊN TẮC:
- ✅ Chỉ sử dụng thông tin từ dữ liệu bên dưới
- ❌ Không bịa đặt thông tin
- 😊 Trả lời thân thiện, nhiệt tình với emoji phù hợp
- ⏰ SỬ DỤNG THÔNG TIN THỜI GIAN để tư vấn chính xác (bây giờ, hôm nay, chiều nay, cuối tuần)
- 🎯 Giúp du khách có trải nghiệm tuyệt vời
- 📞 Nếu thiếu thông tin, gợi ý gọi hotline {SYSTEM_HOTLINE}

🎨 PHONG CÁCH TRẢ LỜI:
- Sử dụng emoji phù hợp: 🎫 (vé), 🕐 (giờ), 🌤️ (thời tiết), 🏛️ (chùa), 🚠 (cáp treo), 🍽️ (ăn uống), 📍 (địa điểm), 💰 (giá), ⛰️ (núi), 🎒 (du lịch)
- Gọi tên khách hàng thân thiện
- Kết thúc bằng lời chúc tốt đẹp
- Tạo cảm giác như đang nói chuyện với bạn bè
- Khi khách hỏi "bây giờ", "hôm nay", "chiều nay" → dùng thông tin thời gian thực để trả lời

📚 DỮ LIỆU:
"""
        
        for i, ctx in enumerate(contexts, 1):
            # Add relevant emoji based on content
            emoji = "📌"
            if "giá" in ctx.topic.lower() or "vé" in ctx.topic.lower():
                emoji = "🎫"
            elif "giờ" in ctx.topic.lower() or "hoạt động" in ctx.topic.lower():
                emoji = "🕐"
            elif "thời tiết" in ctx.topic.lower():
                emoji = "🌤️"
            elif "ga" in ctx.topic.lower() or "cáp treo" in ctx.topic.lower():
                emoji = "🚠"
            elif "chùa" in ctx.topic.lower() or "phật" in ctx.topic.lower():
                emoji = "🏛️"
            elif "nhà hàng" in ctx.topic.lower() or "buffet" in ctx.topic.lower():
                emoji = "🍽️"
            elif "điểm tham quan" in ctx.topic.lower():
                emoji = "📍"
                
            # Use full content - no limits for complete information retrieval
            prompt += f"\n{emoji} {i}. {ctx.topic}\n   {ctx.content}\n"
        
        prompt += f"""
👤 KHÁCH HÀNG: {user_name or 'Bạn'}
💬 CÂU HỎI: {user_msg}

🤖 TRẢ LỜI (thân thiện với emoji, TỐI ĐA 1200 ký tự, súc tích và đi thẳng vào vấn đề):"""
        
        return prompt

    async def generate(self, user_name: str, user_msg: str, contexts: List[KBItem]) -> str:
        """Generate response."""
        if self.gen_model and contexts:
            try:
                prompt = self.build_prompt(user_name, user_msg, contexts)
                response = self.gen_model.generate_content(prompt)
                return response.text.strip()
            except Exception as e:
                log.error(f"Generation error: {e}")
        
        # Fallback
        if not contexts:
            return f"Xin chào {user_name or 'bạn'}! 😊 Mình chưa tìm thấy thông tin phù hợp trong hệ thống. Bạn có thể gọi hotline 📞 {SYSTEM_HOTLINE} để được hỗ trợ nhanh nhất nhé! 🙏"
        
        # Simple fallback
        best = contexts[0]
        return f"📋 Theo thông tin từ hệ thống: {best.content[:300]}... \n\n📞 Để biết thêm chi tiết, bạn có thể gọi hotline {SYSTEM_HOTLINE} nhé! 😊"

    # Transport methods
    async def _http_get(self, path: str, params: Optional[dict] = None) -> Dict[str, Any]:
        """HTTP GET request to bot API with improved error handling."""
        url = f"{BASE_URL}/{path.lstrip('/')}"
        headers = {}
        if ZALO_BOT_TOKEN:
            headers["Authorization"] = f"Bearer {ZALO_BOT_TOKEN}"
        
        if not self.session:
            # Create session with better timeout configuration
            timeout = aiohttp.ClientTimeout(total=10, connect=5)  # Reduced timeout
            connector = aiohttp.TCPConnector(limit=10, limit_per_host=5)
            self.session = aiohttp.ClientSession(timeout=timeout, connector=connector)
        
        try:
            async with self.session.get(url, params=params or {}, headers=headers) as r:
                txt = await r.text()
                try:
                    return json.loads(txt)
                except Exception:
                    return {"ok": False, "raw": txt, "status": r.status}
        except asyncio.TimeoutError:
            log.warning(f"⏰ Timeout for GET {path}")
            return {"ok": False, "error": "timeout", "status": 408}
        except aiohttp.ClientError as e:
            log.warning(f"🌐 Network error for GET {path}: {e}")
            return {"ok": False, "error": str(e), "status": 500}
        except Exception as e:
            log.error(f"❌ Unexpected error for GET {path}: {e}")
            return {"ok": False, "error": str(e), "status": 500}

    async def _http_post(self, path: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """HTTP POST request to bot API with improved error handling."""
        url = f"{BASE_URL}/{path.lstrip('/')}"
        headers = {"Content-Type": "application/json"}
        if ZALO_BOT_TOKEN:
            headers["Authorization"] = f"Bearer {ZALO_BOT_TOKEN}"
            
        if not self.session:
            # Create session with better timeout configuration
            timeout = aiohttp.ClientTimeout(total=10, connect=5)  # Reduced timeout
            connector = aiohttp.TCPConnector(limit=10, limit_per_host=5)
            self.session = aiohttp.ClientSession(timeout=timeout, connector=connector)
        
        try:
            async with self.session.post(url, data=json.dumps(data), headers=headers) as r:
                txt = await r.text()
                try:
                    return json.loads(txt)
                except Exception:
                    return {"ok": False, "raw": txt, "status": r.status}
        except asyncio.TimeoutError:
            log.warning(f"⏰ Timeout for POST {path}")
            return {"ok": False, "error": "timeout", "status": 408}
        except aiohttp.ClientError as e:
            log.warning(f"🌐 Network error for POST {path}: {e}")
            return {"ok": False, "error": str(e), "status": 500}
        except Exception as e:
            log.error(f"❌ Unexpected error for POST {path}: {e}")
            return {"ok": False, "error": str(e), "status": 500}

    async def get_updates(self) -> List[Dict[str, Any]]:
        """Get updates from Zalo Bot API with better error handling."""
        try:
            resp = await self._http_get("getUpdates")
            
            # Handle timeout and network errors
            if resp.get("status") == 408:
                log.warning("⏰ getUpdates timeout - server may be slow")
                return []
            elif resp.get("status") == 500:
                log.warning("🌐 getUpdates network error - retrying later")
                return []
            
            # Debug log only for successful responses with data
            if resp and resp.get("ok") and resp.get("result"):
                log.info(f"📡 getUpdates response: {resp}")
            
            if resp.get("ok"):
                result = resp.get("result", {})
                # Zalo format: {"ok": True, "result": {"message": {...}, "event_name": "..."}}
                if "message" in result:
                    return [result["message"]]  # Return the message object
                else:
                    return []
            else:
                # Only log raw response if it's not empty and not a timeout
                if resp.get("raw") and resp.get("status") != 408:
                    log.warning(f"Raw response: {resp.get('raw')}")
                return []
        except Exception as e:
            log.error(f"getUpdates error: {e}")
            return []

    async def send_chat_action(self, chat_id: str, action: str = "typing") -> bool:
        """Send chat action (typing indicator) via Zalo Bot API."""
        try:
            data = {"chat_id": chat_id, "action": action}
            resp = await self._http_post("sendChatAction", data)
            return resp.get("ok", False)
        except Exception as e:
            log.error(f"sendChatAction error: {e}")
            return False

    async def send_message(self, chat_id: str, text: str) -> bool:
        """Send message via Zalo Bot API."""
        try:
            # Check length and truncate if necessary
            if len(text) > 1900:
                text = text[:1900] + "...\n\n📞 Để biết thêm chi tiết, bạn có thể gọi hotline 0276 3829 829 nhé!"
            
            data = {"chat_id": chat_id, "text": text}
            resp = await self._http_post("sendMessage", data)
            if resp.get("ok"):
                return True
            else:
                log.warning(f"sendMessage failed: {resp}")
                return False
        except Exception as e:
            log.error(f"sendMessage error: {e}")
            return False

    async def process_message(self, msg):
        """Process incoming message from Zalo with typing indicator."""
        try:
            # Handle different message formats
            if isinstance(msg, str):
                log.warning(f"Received string message: {msg}")
                return
            
            if not isinstance(msg, dict):
                log.warning(f"Unexpected message type: {type(msg)}")
                return
            
            # Extract message info (Zalo format)
            # Handle multiple possible formats
            chat_id = "unknown"
            user_id = "unknown"
            user_name = ""
            text = ""
            msg_id = ""
            
            # Try different message formats
            if "chat" in msg and "id" in msg["chat"]:
                # Standard format: {"chat": {"id": "..."}, "from": {"id": "...", "display_name": "..."}, "text": "..."}
                chat_id = msg["chat"]["id"]
                user_id = msg.get("from", {}).get("id", "unknown")
                user_name = msg.get("from", {}).get("display_name", "")
                text = msg.get("text", "").strip()
                msg_id = msg.get("message_id", f"{user_id}_{int(time.time())}")
            elif "message_id" in msg and "text" in msg:
                # Alternative format: {"message_id": "...", "text": "...", "from": {...}}
                msg_id = msg["message_id"]
                text = msg.get("text", "").strip()
                if "from" in msg:
                    user_id = msg["from"].get("id", "unknown")
                    user_name = msg["from"].get("display_name", "")
                    # Use user_id as chat_id for private messages
                    chat_id = user_id
                else:
                    # Extract user info from message_id if possible
                    chat_id = msg_id.split(":")[0] if ":" in msg_id else msg_id
                    user_id = chat_id
            else:
                # Try to extract any available info
                text = msg.get("text", "").strip()
                msg_id = msg.get("message_id", f"unknown_{int(time.time())}")
                chat_id = msg.get("chat_id", msg.get("user_id", "unknown"))
                user_id = msg.get("user_id", msg.get("from", {}).get("id", "unknown"))
                user_name = msg.get("display_name", msg.get("from", {}).get("display_name", ""))
            
            # Debug log
            log.info(f"📥 Raw message: {msg}")
            
            # Dedup
            if msg_id in self._processed_ids:
                return
            self._processed_ids.add(msg_id)
            
            if not text:
                log.warning(f"Empty text from message: {msg}")
                return
            
            log.info(f"📨 Message from {user_name} ({user_id}) in chat {chat_id}: {text}")
            
            # Send typing indicator immediately
            await self.send_chat_action(chat_id, "typing")
            
            # Retrieve relevant context
            contexts = await self.retrieve(text, k=8)
            
            # Send typing indicator again if processing takes time
            await self.send_chat_action(chat_id, "typing")
            
            # Generate response
            answer = await self.generate(user_name, text, contexts)
            
            # Send response
            success = await self.send_message(chat_id, answer)
            if success:
                log.info(f"✅ Replied to {user_name}: {answer[:100]}...")
            else:
                log.error(f"❌ Failed to send reply to {user_name}")
                
        except Exception as e:
            log.error(f"Message processing error: {e}")
            import traceback
            log.error(traceback.format_exc())

    async def run(self):
        """Main bot loop."""
        log.info("🚀 BaDen Tourist AI Bot starting...")
        log.info(f"🔗 Polling: {BASE_URL}")
        
        # Initialize HTTP session
        import aiohttp
        self.session = aiohttp.ClientSession()
        
        try:
            # Pre-fetch KB
            await self.fetch_kb()
            log.info(f"📚 Knowledge Base loaded: {len(self.kb_cache)} items")
            
            log.info("🔄 Starting polling loop...")
            consecutive_errors = 0
            max_consecutive_errors = 5
            
            while True:
                try:
                    updates = await self.get_updates()
                    
                    if updates:
                        consecutive_errors = 0  # Reset error counter on success
                        for update in updates:
                            await self.process_message(update)
                    
                    # Adaptive polling interval based on activity
                    if updates:
                        await asyncio.sleep(1)  # Faster when there are messages
                    else:
                        await asyncio.sleep(3)  # Slower when idle to reduce server load
                    
                except KeyboardInterrupt:
                    log.info("🛑 Stopping bot...")
                    break
                except Exception as e:
                    consecutive_errors += 1
                    log.error(f"Polling error ({consecutive_errors}/{max_consecutive_errors}): {e}")
                    
                    if consecutive_errors >= max_consecutive_errors:
                        log.error("🚨 Too many consecutive errors, recreating session...")
                        if self.session:
                            await self.session.close()
                            self.session = None
                        consecutive_errors = 0
                        await asyncio.sleep(10)  # Longer wait after session reset
                    else:
                        # Exponential backoff
                        wait_time = min(2 ** consecutive_errors, 30)
                        await asyncio.sleep(wait_time)
                    
        finally:
            if self.session:
                await self.session.close()
            if self.price_updater:
                await self.price_updater.close()

# Test function
async def test_bot():
    """Test the bot functionality."""
    print("🧪 Testing BaDen AI Bot")
    print("=" * 40)
    
    bot = BaDenAIBot()
    
    # Test KB fetch
    kb = await bot.fetch_kb()
    print(f"📚 KB items: {len(kb)}")
    
    # Test queries
    test_queries = [
        "giá vé cáp treo",
        "giờ hoạt động", 
        "thời tiết",
        "điểm tham quan"
    ]
    
    for query in test_queries:
        print(f"\n🔍 Query: {query}")
        contexts = await bot.retrieve(query)
        print(f"   Found: {len(contexts)} contexts")
        
        if contexts:
            response = await bot.generate("Test User", query, contexts)
            print(f"   Response: {response[:100]}...")

# Main entry point
async def main():
    """Entry point for production bot."""
    if not BASE_URL:
        log.error("❌ BASE_URL not configured. Set it in .env file.")
        return
    
    if not SUPABASE_URL or not SUPABASE_KEY:
        log.warning("⚠️ Supabase not configured. Bot will have limited functionality.")
    
    bot = BaDenAIBot()
    await bot.run()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        log.info("👋 Bot stopped by user")
    except Exception as e:
        log.error(f"Fatal error: {e}")
        raise
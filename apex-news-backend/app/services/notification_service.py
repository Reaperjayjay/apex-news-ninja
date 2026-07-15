"""
Notification service for sending WhatsApp digests via WAWP API.
Includes retry logic and message formatting.
"""
import logging
import asyncio
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
from bson import ObjectId
import httpx
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.config import settings
from app.services.personalization_service import PersonalizationService

logger = logging.getLogger(__name__)


class NotificationService:
    """
    Service for sending WhatsApp notifications via WAWP API.
    """

    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.wawp_url = settings.wawp_api_url
        self.api_key = settings.wawp_api_key
        self.sender_id = settings.wawp_sender_id
        self.max_retries = settings.notification_max_retries
        self.retry_delay = settings.notification_retry_delay_seconds

    async def send_daily_digest(self, user_id: str) -> bool:
        """
        Send daily news digest to user via WhatsApp.

        Args:
            user_id: User ID

        Returns:
            True if sent successfully, False otherwise
        """
        try:
            # Get user details
            try:
                user_oid = ObjectId(user_id)
            except Exception:
                logger.error(f"Invalid user ID format: {user_id}")
                return False
            
            user = await self.db.users.find_one({"_id": user_oid})

            if not user:
                logger.error(f"User not found: {user_id}")
                return False

            if not user.get("whatsapp_number"):
                logger.warning(f"User {user_id} has no WhatsApp number")
                return False

            # Get user preferences for max articles
            prefs = await self.db.user_preferences.find_one({"user_id": user_id})
            max_articles = prefs.get("max_articles",
                                     settings.max_digest_articles) if prefs else settings.max_digest_articles

            # Get personalized articles
            articles = await PersonalizationService.get_recommended_articles(
                self.db, user_id, limit=max_articles
            )

            if not articles:
                logger.info(f"No articles to send in digest for user {user_id}")
                return False

            # Format digest message
            message = self._format_digest_message(user, articles)

            # Send via WAWP
            success = await self._send_whatsapp_message(
                user["whatsapp_number"],
                message
            )

            if success:
                # Log digest sent
                await self.db.digest_logs.insert_one({
                    "user_id": user_id,
                    "sent_at": datetime.utcnow(),
                    "article_count": len(articles),
                    "status": "sent"
                })
                logger.info(f"Digest sent to user {user_id}")

            return success

        except Exception as e:
            logger.error(f"Failed to send digest to user {user_id}: {e}")
            return False

    def _format_digest_message(
            self,
            user: Dict[str, Any],
            articles: List[Dict[str, Any]]
    ) -> str:
        """
        Format digest message for WhatsApp.

        Args:
            user: User document
            articles: List of article documents

        Returns:
            Formatted message string
        """
        greeting = f"🥷 *Apex News Ninja Digest*\n"
        greeting += f"Hey {user.get('full_name', user.get('username', 'there'))}!\n\n"
        greeting += f"Here are your top {len(articles)} personalized news stories:\n\n"

        message_parts = [greeting]

        for i, article in enumerate(articles, 1):
            article_text = f"*{i}. {article['title']}*\n"

            if article.get('description'):
                # Truncate description to 150 chars
                desc = article['description'][:150]
                if len(article['description']) > 150:
                    desc += "..."
                article_text += f"{desc}\n"

            article_text += f"📰 {article['source']} | 🏷️ {article.get('category', 'general').title()}\n"
            article_text += f"🔗 {article['url']}\n\n"

            message_parts.append(article_text)

        footer = f"---\n"
        footer += f"📊 View Count: {sum(a.get('view_count', 0) for a in articles)}\n"
        footer += f"⏰ Generated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}\n"
        footer += f"\n_Stay informed with Apex News Ninja!_ 🚀"

        message_parts.append(footer)

        return "".join(message_parts)

    async def _send_whatsapp_message(
            self,
            phone_number: str,
            message: str
    ) -> bool:
        """
        Send WhatsApp message via WAWP API with retry logic.

        Args:
            phone_number: Recipient WhatsApp number
            message: Message text

        Returns:
            True if sent successfully, False otherwise
        """
        if not self.wawp_url or not self.api_key:
            logger.warning("WAWP API not configured, skipping WhatsApp send")
            return False

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "sender": self.sender_id,
            "recipient": phone_number,
            "message": message,
            "type": "text"
        }

        retry_count = 0

        async with httpx.AsyncClient(timeout=30) as client:
            while retry_count < self.max_retries:
                try:
                    logger.debug(f"Sending WhatsApp to {phone_number} (attempt {retry_count + 1})")

                    response = await client.post(
                        self.wawp_url,
                        headers=headers,
                        json=payload
                    )

                    response.raise_for_status()

                    logger.info(f"WhatsApp sent successfully to {phone_number}")
                    return True

                except httpx.HTTPStatusError as e:
                    logger.error(f"WAWP API error: {e.response.status_code} - {e.response.text}")
                    retry_count += 1

                    if retry_count < self.max_retries:
                        await asyncio.sleep(self.retry_delay * retry_count)  # Exponential backoff

                except Exception as e:
                    logger.error(f"WhatsApp send failed: {e}")
                    retry_count += 1

                    if retry_count < self.max_retries:
                        await asyncio.sleep(self.retry_delay * retry_count)

        logger.error(f"Failed to send WhatsApp after {self.max_retries} attempts")
        return False

    async def send_instant_notification(
            self,
            user_id: str,
            title: str,
            message: str
    ) -> bool:
        """
        Send instant notification to user (breaking news, alerts).

        Args:
            user_id: User ID
            title: Notification title
            message: Notification message

        Returns:
            True if sent successfully
        """
        try:
            user_oid = ObjectId(user_id)
        except Exception:
            logger.error(f"Invalid user ID format: {user_id}")
            return False
        
        user = await self.db.users.find_one({"_id": user_oid})

        if not user or not user.get("whatsapp_number"):
            return False

        formatted_message = f"🚨 *{title}*\n\n{message}"

        return await self._send_whatsapp_message(
            user["whatsapp_number"],
            formatted_message
        )

    async def send_welcome_message(self, user_id: str) -> bool:
        """
        Send welcome message to new user.

        Args:
            user_id: User ID

        Returns:
            True if sent successfully
        """
        try:
            user_oid = ObjectId(user_id)
        except Exception:
            logger.error(f"Invalid user ID format: {user_id}")
            return False

        user = await self.db.users.find_one({"_id": user_oid})

        if not user or not user.get("whatsapp_number"):
            return False

        message = f"👋 *Welcome to Apex News Ninja!*\n\n"
        message += f"Hi {user.get('full_name', user.get('username', 'there'))}! Thanks for joining us.\n\n"
        message += f"You'll receive your daily news digest at {settings.digest_send_time} UTC.\n"
        message += f"Customize your niches in your profile settings to get the news that matters to you.\n\n"
        message += f"🚀 _Stay sharp, stay informed!_"

        return await self._send_whatsapp_message(
            user["whatsapp_number"],
            message
        )
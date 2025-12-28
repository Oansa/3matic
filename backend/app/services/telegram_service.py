import asyncio
from datetime import datetime, timedelta
from typing import Dict, Any, List
import httpx
from app.services.gemini_service import generate_response
from app.services.vector_store import get_collection
from app.database import get_db
from bson import ObjectId

class TelegramService:
    def __init__(self):
        self.scheduled_tasks = {}
    
    async def send_message(self, telegram_token: str, chat_id: str, message: str) -> bool:
        """Send a message via Telegram"""
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    f"https://api.telegram.org/bot{telegram_token}/sendMessage",
                    json={"chat_id": chat_id, "text": message}
                )
                return response.status_code == 200
            except Exception as e:
                print(f"Error sending Telegram message: {e}")
                return False
    
    async def generate_content(self, community: Dict[str, Any]) -> str:
        """Generate content based on community configuration"""
        # Get relevant documents from vector store
        collection = get_collection(str(community["_id"]))
        if collection:
            # Query for relevant content based on purpose and rules
            query = f"Generate engaging content for a community about: {community.get('purpose', '')}"
            results = collection.query(query_texts=[query], n_results=5)
            
            context = "\n".join(results['documents'][0]) if results['documents'] else ""
        else:
            context = ""
        
        # Generate response using Gemini
        prompt = f"""
        Generate an engaging message for a Telegram community with the following characteristics:
        - Purpose: {community.get('purpose', 'general discussion')}
        - Engagement style: {community.get('engagementStyle', 'friendly')}
        - Moderation level: {community.get('moderationLevel', 'medium')}
        
        Context from uploaded documents:
        {context}
        
        Create a natural, engaging message that would fit this community's style.
        """
        
        content = await generate_response(prompt)
        return content
    
    async def post_immediately(self, community_id: str) -> bool:
        """Post content immediately to the community"""
        db = get_db()
        if not db:
            return False
        
        community = await db.communities.find_one({"_id": ObjectId(community_id)})
        if not community:
            return False
        
        content = await self.generate_content(community)
        success = await self.send_message(
            community["telegram_token"],
            community["telegram_chat_id"],
            content
        )
        
        if success:
            # Log the post
            await db.communities.update_one(
                {"_id": ObjectId(community_id)},
                {"$push": {"scheduledPosts": {
                    "content": content,
                    "timestamp": datetime.utcnow(),
                    "type": "immediate"
                }}}
            )
        
        return success
    
    async def schedule_posts(self, community_id: str):
        """Schedule posts based on frequency setting"""
        db = get_db()
        if not db:
            return
        
        community = await db.communities.find_one({"_id": ObjectId(community_id)})
        if not community:
            return
        
        frequency = community.get("postingFrequency", "moderate")
        
        # Calculate interval based on frequency
        if frequency == "low":
            interval_hours = 24  # once per day
        elif frequency == "moderate":
            interval_hours = 12  # twice per day
        elif frequency == "high":
            interval_hours = 6   # four times per day
        else:
            interval_hours = 12
        
        # Cancel existing task if any
        if community_id in self.scheduled_tasks:
            self.scheduled_tasks[community_id].cancel()
        
        # Schedule new task
        async def scheduled_post():
            while True:
                await asyncio.sleep(interval_hours * 3600)  # Convert hours to seconds
                await self.post_immediately(community_id)
        
        task = asyncio.create_task(scheduled_post())
        self.scheduled_tasks[community_id] = task
    
    async def start_scheduling(self, community_id: str):
        """Start scheduling for a community"""
        await self.schedule_posts(community_id)
    
    async def stop_scheduling(self, community_id: str):
        """Stop scheduling for a community"""
        if community_id in self.scheduled_tasks:
            self.scheduled_tasks[community_id].cancel()
            del self.scheduled_tasks[community_id]

# Global instance
telegram_service = TelegramService()
from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from typing import Dict, Any
from bson import ObjectId
from datetime import datetime

from app.database import get_db
from app.services.vector_store import search, add_memory
from app.services.gemini_service import generate_response
from app.services.platform_handlers import (
    send_telegram_message
)

router = APIRouter()

def is_mention(message: str, bot_name: str = None) -> bool:
    """Check if message mentions the bot"""
    if not bot_name:
        return False
    return bot_name.lower() in message.lower() or "@" in message

async def process_message(community_id: str, message: str, user_info: Dict[str, Any] = None):
    """Process incoming message and generate response if needed"""
    db = get_db()
    try:
        community = await db.communities.find_one({"_id": ObjectId(community_id)})
    except Exception:
        return None
    
    if not community or community.get("status") != "active":
        return None
    
    # Check if bot is mentioned
    if not is_mention(message):
        return None
    
    # Search relevant context from vector store
    search_results = await search(community_id, message, n_results=3)
    context = search_results.get("documents", [])
    
    # Generate response
    response = await generate_response(
        community_config={
            "platform": community["platform"],
            "purpose": community.get("purpose", ""),
            "moderationLevel": community.get("moderationLevel", "medium"),
            "engagementStyle": community.get("engagementStyle", "friendly"),
            "postingFrequency": community.get("postingFrequency", "moderate")
        },
        user_message=message,
        context=context[0] if context else []
    )
    
    # Store interaction in memory
    memory_id = f"interaction_{datetime.utcnow().timestamp()}"
    await add_memory(
        community_id=community_id,
        memory_id=memory_id,
        text=f"User: {message}\nAI: {response}",
        metadata={"type": "interaction"}
    )
    
    return response

@router.post("/telegram/{community_id}")
async def telegram_webhook(community_id: str, request: Request):
    """Handle Telegram webhook"""
    try:
        data = await request.json()
        
        # Telegram webhook format
        if "message" in data:
            message_obj = data["message"]
            chat_id = message_obj["chat"]["id"]
            message_text = message_obj.get("text", "")
            user = message_obj.get("from", {})
            
            if message_text:
                response = await process_message(community_id, message_text, user)
                
                if response:
                    db = get_db()
                    community = await db.communities.find_one({"_id": ObjectId(community_id)})
                    if community:
                        await send_telegram_message(community["botToken"], str(chat_id), response)
        
        return JSONResponse(content={"ok": True})
    except Exception as e:
        print(f"Telegram webhook error: {e}")
        return JSONResponse(content={"ok": False}, status_code=500)


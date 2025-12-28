import google.generativeai as genai
import os
from dotenv import load_dotenv
from typing import List, Dict, Any

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "KEY HERE")

# Try to use the latest model, fallback to gemini-pro if needed
model = None
if GEMINI_API_KEY and GEMINI_API_KEY != "KEY HERE":
    try:
        genai.configure(api_key=GEMINI_API_KEY)
        # Try gemini-1.5-flash first (faster, cheaper), fallback to gemini-1.5-pro, then gemini-pro
        try:
            model = genai.GenerativeModel('gemini-1.5-flash')
            print("Using Gemini 1.5 Flash model")
        except:
            try:
                model = genai.GenerativeModel('gemini-1.5-pro')
                print("Using Gemini 1.5 Pro model")
            except:
                model = genai.GenerativeModel('gemini-pro')
                print("Using Gemini Pro model (legacy)")
    except Exception as e:
        print(f"Failed to configure Gemini API: {e}")
        model = None
else:
    print("Gemini API key not configured. Using fallback messages.")

async def generate_setup_intro() -> str:
    """Generate AI assistant introduction message"""
    if not model:
        print("⚠️  Gemini model not initialized - using fallback message")
        return "Welcome! I'm your AI Community Manager assistant. I'll help you configure your community management system."
    
    prompt = """You are a friendly AI assistant helping users set up their community management system. 
    Write a brief, welcoming introduction (2-3 sentences) that explains you'll ask questions to understand their community needs."""
    
    try:
        response = model.generate_content(prompt)
        print("✅ Gemini API call successful")
        return response.text
    except Exception as e:
        print(f"❌ Error generating intro with Gemini API: {e}")
        print(f"   Error type: {type(e).__name__}")
        return "Welcome! I'm your AI Community Manager assistant. I'll help you configure your community management system."

async def generate_response(
    community_config: Dict[str, Any],
    user_message: str,
    context: List[str] = None
) -> str:
    """Generate AI response based on community configuration and context"""
    if not model:
        return "I'm here to help! (Gemini API not configured)"
    
    context_text = "\n".join(context) if context else "No additional context."
    
    prompt = f"""You are an AI community manager for a {community_config.get('platform', 'community')} community.

Community Configuration:
- Purpose: {community_config.get('purpose', 'Not specified')}
- Moderation Level: {community_config.get('moderationLevel', 'medium')}
- Engagement Style: {community_config.get('engagementStyle', 'friendly')}
- Posting Frequency: {community_config.get('postingFrequency', 'moderate')}

Relevant Context:
{context_text}

User Message: {user_message}

Respond in a {community_config.get('engagementStyle', 'friendly')} style, keeping moderation level {community_config.get('moderationLevel', 'medium')} in mind.
Keep your response concise and helpful."""
    
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        print(f"Error generating response: {e}")
        return "I apologize, but I'm having trouble processing that right now. Please try again."

async def generate_scheduled_post(community_config: Dict[str, Any], topic: str = None) -> str:
    """Generate scheduled post content"""
    if not model:
        return "Community update: Stay engaged and keep the conversation going!"
    
    prompt = f"""Generate a {community_config.get('engagementStyle', 'friendly')} community post for a {community_config.get('platform', 'community')} community.
    
Community Purpose: {community_config.get('purpose', 'General community')}
Topic: {topic or 'General community engagement'}

Keep it engaging, relevant to the community purpose, and match the {community_config.get('engagementStyle', 'friendly')} style.
Maximum 200 words."""
    
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        print(f"Error generating post: {e}")
        return "Hello everyone! Hope you're having a great day. Let's keep the conversation going! 🚀"


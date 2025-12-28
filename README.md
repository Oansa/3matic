# PowerHause - AI-Powered Community Management Platform

A comprehensive prototype for managing communities across Telegram, Discord, and WhatsApp using AI-powered automation.

## Features

- 🔐 OAuth Authentication (Google & GitHub)
- 💬 Multi-platform Support (Telegram, Discord, WhatsApp)
- 🤖 AI-Powered Community Manager (Gemini API)
- 📄 Document Processing (PDF, Word)
- 🧠 Vector Store for Community Memory (Chroma)
- 📊 Community Dashboard
- ⚙️ Configurable Rules & Moderation

## Project Structure

```
powerhause/
├── frontend/          # Vite + React frontend
├── backend/           # FastAPI backend
└── README.md
```

## Prerequisites

- Python 3.9+
- Node.js 18+
- MongoDB (local or cloud)
- Google Gemini API Key

## Setup Instructions

### Backend Setup

1. Navigate to backend directory:
```bash
cd backend
```

2. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create `.env` file from `.env.example`:
```bash
cp .env.example .env
```

5. Configure `.env` file:
```env
MONGO_URL=mongodb://localhost:27017
DATABASE_NAME=powerhause
JWT_SECRET=your-secret-key-change-in-production
GEMINI_API_KEY=KEY HERE  # Replace with your actual key
BASE_URL=http://localhost:8000
FRONTEND_URL=http://localhost:3000

# OAuth (optional for development)
GOOGLE_CLIENT_ID=
GOOGLE_CLIENT_SECRET=
GITHUB_CLIENT_ID=
GITHUB_CLIENT_SECRET=
```

6. Start MongoDB (if running locally):
```bash
mongod
```

7. Run the backend server:
```bash
python main.py
# or
uvicorn main:app --reload
```

Backend will run on `http://localhost:8000`

### Frontend Setup

1. Navigate to frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Start development server:
```bash
npm run dev
```

Frontend will run on `http://localhost:3000`

## Usage

### 1. Login
- Use OAuth (Google/GitHub) to authenticate
- For development, you can modify the auth flow to use mock authentication

### 2. Connect Community
- Select platform (Telegram/Discord/WhatsApp)
- Enter bot token/credentials
- System will create a community entry

### 3. AI Setup
- AI assistant will ask structured questions:
  - Community purpose
  - Moderation level
  - Engagement style
  - Posting frequency

### 4. Upload Documents (Optional)
- Upload PDF or Word documents
- Documents are processed and stored in vector store
- Used for context in AI responses

### 5. Deploy
- System configures webhooks
- Activates community manager
- Starts monitoring and auto-responding

## API Endpoints

### Authentication
- `GET /api/auth/oauth/{provider}` - Initiate OAuth login
- `GET /api/auth/oauth/{provider}/callback` - OAuth callback
- `GET /api/auth/me` - Get current user

### Communities
- `GET /api/communities` - List all communities
- `GET /api/communities/{id}` - Get community details
- `POST /api/communities/connect` - Connect new community
- `POST /api/communities/{id}/setup/start` - Start AI setup
- `POST /api/communities/{id}/setup/answer` - Answer setup question
- `POST /api/communities/{id}/documents` - Upload documents
- `POST /api/communities/{id}/deploy` - Deploy community manager

### Webhooks
- `POST /api/webhooks/telegram/{community_id}` - Telegram webhook
- `POST /api/webhooks/discord/{community_id}` - Discord webhook
- `POST /api/webhooks/whatsapp/{community_id}` - WhatsApp webhook

## Cloud Deployment

### Backend (FastAPI)
- Deploy to services like:
  - Railway
  - Render
  - Heroku
  - AWS/GCP/Azure

- Set environment variables in your hosting platform
- Update `BASE_URL` to your production URL

### Frontend (Vite)
- Build for production:
```bash
npm run build
```

- Deploy to:
  - Vercel
  - Netlify
  - Cloudflare Pages
  - Any static hosting

- Update API proxy in `vite.config.js` for production

### MongoDB
- Use MongoDB Atlas (cloud) or self-hosted

### Chroma Vector Store
- For production, consider:
  - Chroma Cloud
  - Self-hosted with persistent storage
  - Alternative: Pinecone, Weaviate

## Development Notes

- The prototype uses local Chroma DB (persisted in `./chroma_db`)
- Uploaded documents are stored in `./uploads`
- OAuth requires proper callback URLs configured in provider settings
- Webhook URLs need to be publicly accessible for production

## Environment Variables Reference

### Backend
- `MONGO_URL` - MongoDB connection string
- `DATABASE_NAME` - Database name
- `JWT_SECRET` - Secret for JWT tokens
- `GEMINI_API_KEY` - Google Gemini API key
- `BASE_URL` - Backend base URL (for webhooks)
- `FRONTEND_URL` - Frontend URL (for OAuth redirects)
- `GOOGLE_CLIENT_ID` / `GOOGLE_CLIENT_SECRET` - Google OAuth
- `GITHUB_CLIENT_ID` / `GITHUB_CLIENT_SECRET` - GitHub OAuth

## Troubleshooting

### MongoDB Connection Issues
- Ensure MongoDB is running
- Check connection string format
- Verify network access if using cloud MongoDB

### OAuth Not Working
- Verify callback URLs in OAuth provider settings
- Check `FRONTEND_URL` matches your frontend URL
- Ensure client IDs and secrets are correct

### Webhook Issues
- Webhooks require public URL (use ngrok for local testing)
- Verify bot tokens are correct
- Check platform-specific webhook requirements

### Vector Store Issues
- Ensure write permissions for `./chroma_db` directory
- Check Chroma version compatibility

## License

This is a prototype project for demonstration purposes.


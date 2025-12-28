# Quick Start Guide

## Prerequisites Check

- [ ] Python 3.9+ installed
- [ ] Node.js 18+ installed
- [ ] MongoDB running (local or cloud)
- [ ] Gemini API key ready

## Step-by-Step Setup

### 1. Backend Setup (5 minutes)

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

Create `.env` file:
```env
MONGO_URL=mongodb://localhost:27017
DATABASE_NAME=powerhause
JWT_SECRET=change-this-secret-key
GEMINI_API_KEY=KEY HERE
BASE_URL=http://localhost:8000
FRONTEND_URL=http://localhost:3000
```

Start backend:
```bash
python main.py
```

### 2. Frontend Setup (2 minutes)

```bash
cd frontend
npm install
npm run dev
```

### 3. Access Application

Open browser: `http://localhost:3000`

## Testing Without OAuth

For quick testing, you can modify the auth flow or use mock authentication. The system will work once you:
1. Connect a community (use test bot tokens)
2. Complete the setup flow
3. Deploy the community manager

## Next Steps

1. Configure OAuth providers (Google/GitHub) for production
2. Set up bot tokens for your platforms
3. Test webhook endpoints (use ngrok for local testing)
4. Deploy to cloud when ready

## Troubleshooting

- **MongoDB not connecting**: Check if MongoDB is running and connection string is correct
- **Port already in use**: Change ports in config files
- **CORS errors**: Verify frontend URL in backend CORS settings
- **Vector store errors**: Ensure write permissions for `./chroma_db` directory


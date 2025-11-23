# RAGLint Deployment Guide

## Option 1: Railway (Recommended - 5 min)

### Step 1: Prepare for Railway
Create `railway.json`:
```json
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "DOCKERFILE"
  },
  "deploy": {
    "startCommand": "uvicorn raglint.dashboard.app:app --host 0.0.0.0 --port $PORT",
    "healthcheckPath": "/health"
  }
}
```

### Step 2: Add Postgres Plugin
1. Go to railway.app
2. Click "New Project"
3. Select "Deploy from GitHub repo"
4. Add environment variables:
   - `RAGLINT_DB_URL`: (auto-filled by Railway Postgres plugin)
   - `OPENAI_API_KEY`: Your OpenAI key (optional)

### Step 3: Deploy
```bash
railway up
```

**Done!** Your demo will be at `https://raglint-production.up.railway.app`

---

## Option 2: Vercel (Frontend only)

Vercel can't run the full stack (no Postgres), but good for static demo:

1. Create `vercel.json`:
```json
{
  "builds": [
    {
      "src": "raglint/dashboard/app.py",
      "use": "@vercel/python"
    }
  ],
  "routes": [
    {
      "src": "/(.*)",
      "dest": "raglint/dashboard/app.py"
    }
  ]
}
```

2. Deploy:
```bash
vercel --prod
```

---

## Option 3: Docker Compose (VPS/EC2)

### Step 1: Clone repo on server
```bash
git clone https://github.com/yourusername/raglint
cd raglint
```

### Step 2: Set environment variables
```bash
export OPENAI_API_KEY="sk-..."
```

### Step 3: Deploy
```bash
docker-compose up -d
```

### Step 4: Configure domain (optional)
Point your DNS to the server IP and use nginx as reverse proxy.

**Cost**: ~$5/month (DigitalOcean Droplet)

---

## Cost Comparison

| Platform | Cost/month | Postgres | Custom Domain | Best For |
|----------|------------|----------|---------------|----------|
| Railway | $5-20 | ✅ | ✅ | Quick demo |
| Vercel | Free-$20 | ❌ | ✅ | Static demo |
| VPS (DO) | $5 | ✅ | ✅ | Production |

**Recommendation**: Start with Railway for demo, then move to VPS for production.

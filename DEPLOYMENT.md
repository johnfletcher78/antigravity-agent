# Deployment Guide

You can access your **Antigravity Marketing Agent** from your phone or any other computer by deploying it to the cloud.

We recommend using **Vercel** for the frontend and **Render** for the backend (both have free tiers).

## Step 1: Push Code to GitHub
1. Create a repository on GitHub (e.g., `antigravity-agent`).
2. Push your code to this repository.

## Step 2: Deploy Backend (Render.com)
1. Sign up/Log in to [Render](https://render.com).
2. Click **New +** -> **Web Service**.
3. Connect your GitHub repository.
4. Settings:
   - **Root Directory**: `backend`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
5. **Environment Variables** (Add these in the "Environment" tab):
   - `GOOGLE_API_KEY`: (Your Google/Gemini Key)
   - `ELEVENLABS_API_KEY`: (Your ElevenLabs Key)
   - `ELEVENLABS_VOICE_ID`: `rfkTsdZrVWEVhDycUYn9`
6. Click **Deploy**.
7. Once deployed, copy your **backend URL** (e.g., `https://antigravity-backend.onrender.com`).

## Step 3: Deploy Frontend (Vercel)
1. Sign up/Log in to [Vercel](https://vercel.com).
2. Click **Add New** -> **Project**.
3. connect your GitHub repository.
4. Settings:
   - **Root Directory**: `frontend` (Click "Edit" next to Root Directory).
   - **Framework Preset**: Next.js (Should auto-detect).
5. **Environment Variables**:
   - `NEXT_PUBLIC_API_URL`: Paste your **Backend URL** from Step 2 (e.g., `https://antigravity-backend.onrender.com`).
     *(Note: Do not add a trailing slash `/`)*
   - `NEXT_PUBLIC_APP_PASSWORD`: Set your desired access password (default: `marketing123`).
6. Click **Deploy**.

## Step 4: Access on Mobile
1. Once Vercel finishes, you will get a domain like `https://antigravity-agent.vercel.app`.
2. Open this URL on your phone.
3. Login with your password.
4. **Use Voice**: Since it's HTTPS, the microphone will work perfectly!

## Troubleshooting
- **CORS Errors**: Ensure your Backend URL in Vercel is correct (no trailing slash).
- **Voice Lag**: On mobile networks, latency might be slightly higher than localhost.

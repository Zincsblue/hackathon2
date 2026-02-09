# Deploy Backend to Render (Free Forever)

## Why Render?
- ✅ **Truly free forever** (no credit card required)
- ✅ Perfect for FastAPI backends
- ✅ Auto-deploy from GitHub
- ✅ Built-in HTTPS
- ⚠️ Spins down after 15 min inactivity (first request takes 30-60 sec)

## Step 1: Set Up Neon Database (5 minutes)

1. Go to https://neon.tech
2. Sign up (free, no credit card)
3. Create new project: "todo-app"
4. Copy the connection string:
   ```
   postgresql://user:password@ep-xxx.region.aws.neon.tech/neondb?sslmode=require
   ```
5. Keep this - you'll need it for Render

## Step 2: Generate SECRET_KEY

Run this command in your terminal:
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

Copy the output - you'll need it for Render.

## Step 3: Deploy Backend to Render

### 3.1 Create Render Account
1. Go to https://render.com
2. Click "Get Started for Free"
3. Sign up with GitHub (recommended)

### 3.2 Create New Web Service
1. Click "New +" → "Web Service"
2. Connect your GitHub repository: `Zincsblue/hackathon2`
3. Click "Connect" next to your repository

### 3.3 Configure the Service
Fill in these settings:

**Basic Settings:**
- **Name**: `todo-backend` (or any name you like)
- **Region**: Choose closest to you (e.g., Oregon)
- **Branch**: `003-frontend-integration`
- **Root Directory**: `backend`
- **Runtime**: `Python 3`
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `uvicorn src.main:app --host 0.0.0.0 --port $PORT`

**Plan:**
- Select **"Free"** plan

### 3.4 Add Environment Variables

Click "Advanced" and add these environment variables:

| Key | Value |
|-----|-------|
| `DATABASE_URL` | Your Neon connection string |
| `SECRET_KEY` | Your generated secret key |
| `ALGORITHM` | `HS256` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `30` |
| `REFRESH_TOKEN_EXPIRE_DAYS` | `7` |
| `CORS_ORIGINS` | `https://your-frontend.vercel.app` (update after frontend deploys) |

**Important:** For `CORS_ORIGINS`, temporarily use `*` (allow all), then update it after you get your Vercel frontend URL.

### 3.5 Deploy
1. Click "Create Web Service"
2. Wait 5-10 minutes for the build to complete
3. You'll see logs in real-time
4. When done, you'll get a URL like: `https://todo-backend-xxxx.onrender.com`

### 3.6 Copy Your Backend URL
Copy the Render URL - you'll need it for the frontend deployment.

## Step 4: Run Database Migrations

You need to run Alembic migrations on your Neon database.

### Option A: Run Locally (Easiest)
```bash
cd backend
set DATABASE_URL=<your-neon-connection-string>
alembic upgrade head
```

### Option B: Use Render Shell
1. Go to your Render dashboard
2. Click on your service
3. Click "Shell" tab
4. Run: `alembic upgrade head`

## Step 5: Test Your Backend

Test if your backend is working:

1. Visit: `https://your-backend.onrender.com/docs`
2. You should see the FastAPI Swagger documentation
3. Try the `/health` endpoint (if you have one)

**Note:** First request might take 30-60 seconds if the service was sleeping.

## Step 6: Update Frontend Environment Variable

1. Go to your Vercel dashboard
2. Find your frontend project
3. Go to Settings → Environment Variables
4. Update or add:
   ```
   NEXT_PUBLIC_API_BASE_URL=https://your-backend.onrender.com/api
   ```
5. Redeploy your frontend

## Step 7: Update Backend CORS

1. Go back to Render dashboard
2. Click on your backend service
3. Go to Environment
4. Update `CORS_ORIGINS` with your actual Vercel URL:
   ```
   CORS_ORIGINS=https://your-frontend.vercel.app
   ```
5. Save (Render will auto-redeploy)

## Troubleshooting

### Backend won't start
- Check Render logs for errors
- Verify all environment variables are set
- Make sure `DATABASE_URL` is correct

### CORS errors in frontend
- Verify `CORS_ORIGINS` matches your Vercel URL exactly
- No trailing slash in the URL
- Wait for Render to redeploy after changing env vars

### Database connection errors
- Verify Neon connection string is correct
- Make sure migrations ran successfully
- Check if Neon database is active

### 503 Service Unavailable
- This is normal on first request (service is waking up)
- Wait 30-60 seconds and try again
- Subsequent requests will be fast

## Free Tier Limitations

**Render Free Tier:**
- ✅ 750 hours/month (enough for 24/7 if only 1 service)
- ✅ Automatic HTTPS
- ✅ Auto-deploy from GitHub
- ⚠️ Spins down after 15 minutes of inactivity
- ⚠️ 512 MB RAM
- ⚠️ Shared CPU

**Neon Free Tier:**
- ✅ 1 project
- ✅ 10 branches
- ✅ 3 GB storage
- ✅ Automatic backups

**Vercel Free Tier:**
- ✅ Unlimited deployments
- ✅ 100 GB bandwidth/month
- ✅ Automatic HTTPS

## Total Cost: $0/month 🎉

## Keep Service Awake (Optional)

To prevent the 15-minute spin-down, you can:

1. Use a free uptime monitoring service like:
   - UptimeRobot (https://uptimerobot.com)
   - Cron-job.org (https://cron-job.org)

2. Set it to ping your backend every 10 minutes:
   - URL: `https://your-backend.onrender.com/docs`
   - Interval: 10 minutes

This keeps your service warm and responsive.

## Next Steps

1. ✅ Backend deployed to Render
2. ✅ Database set up on Neon
3. ✅ Migrations run
4. ⬜ Frontend deployed to Vercel
5. ⬜ Environment variables configured
6. ⬜ Test the full application

## Support

If you encounter issues:
- Check Render logs in the dashboard
- Verify all environment variables
- Test backend API docs at `/docs`
- Check Neon database connection

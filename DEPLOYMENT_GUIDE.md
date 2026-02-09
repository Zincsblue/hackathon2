# Deployment Guide - Todo Full-Stack Application

## Prerequisites
- GitHub account (✓ Already have repository at https://github.com/Zincsblue/hackathon2.git)
- Vercel account (sign up at https://vercel.com)
- Neon account for PostgreSQL database (sign up at https://neon.tech)

## Step 1: Set Up Neon Database (Free Tier)

1. Go to https://neon.tech and sign up/login
2. Create a new project:
   - Project name: `todo-app`
   - Region: Choose closest to your users
3. Copy the connection string (it looks like):
   ```
   postgresql://user:password@ep-xxx.region.aws.neon.tech/neondb?sslmode=require
   ```
4. Keep this connection string - you'll need it for backend deployment

## Step 2: Deploy Backend to Railway (Free Tier - Better for FastAPI)

**Why Railway instead of Vercel for backend?**
- Vercel has limited Python/FastAPI support
- Railway offers better support for Python backends with free tier
- Railway provides persistent connections needed for database

### Railway Deployment Steps:

1. Go to https://railway.app and sign up with GitHub
2. Click "New Project" → "Deploy from GitHub repo"
3. Select your repository: `Zincsblue/hackathon2`
4. Select branch: `003-frontend-integration`
5. Railway will detect it's a Python project
6. Configure the service:
   - **Root Directory**: `backend`
   - **Start Command**: `uvicorn src.main:app --host 0.0.0.0 --port $PORT`

7. Add Environment Variables in Railway:
   ```
   DATABASE_URL=<your-neon-connection-string>
   SECRET_KEY=<generate-a-random-secret-key>
   ALGORITHM=HS256
   ACCESS_TOKEN_EXPIRE_MINUTES=30
   REFRESH_TOKEN_EXPIRE_DAYS=7
   CORS_ORIGINS=https://your-frontend-url.vercel.app
   ```

8. To generate a SECRET_KEY, run this in your terminal:
   ```bash
   python -c "import secrets; print(secrets.token_urlsafe(32))"
   ```

9. Click "Deploy" - Railway will build and deploy your backend
10. Copy the Railway URL (e.g., `https://your-app.railway.app`)

## Step 3: Deploy Frontend to Vercel (Free Tier)

1. Go to https://vercel.com and sign up with GitHub
2. Click "Add New" → "Project"
3. Import your GitHub repository: `Zincsblue/hackathon2`
4. Configure the project:
   - **Framework Preset**: Next.js
   - **Root Directory**: `frontend`
   - **Build Command**: `npm run build`
   - **Output Directory**: `.next`

5. Add Environment Variables:
   ```
   NEXT_PUBLIC_API_BASE_URL=https://your-backend-url.railway.app/api
   ```
   Replace `your-backend-url.railway.app` with your actual Railway backend URL

6. Click "Deploy"
7. Wait for deployment to complete (2-3 minutes)
8. Copy your Vercel frontend URL (e.g., `https://your-app.vercel.app`)

## Step 4: Update Backend CORS Settings

1. Go back to Railway dashboard
2. Update the `CORS_ORIGINS` environment variable with your Vercel frontend URL:
   ```
   CORS_ORIGINS=https://your-app.vercel.app
   ```
3. Redeploy the backend (Railway will auto-redeploy on env change)

## Step 5: Run Database Migrations

You need to run Alembic migrations on your Neon database:

### Option A: Run locally (Recommended)
```bash
cd backend
# Set environment variable
set DATABASE_URL=<your-neon-connection-string>
# Run migrations
alembic upgrade head
```

### Option B: Run via Railway CLI
```bash
# Install Railway CLI
npm i -g @railway/cli
# Login
railway login
# Link to your project
railway link
# Run migrations
railway run alembic upgrade head
```

## Step 6: Test Your Deployed Application

1. Visit your Vercel frontend URL: `https://your-app.vercel.app`
2. Click "Sign Up" and create an account
3. Log in and create some tasks
4. Test all features:
   - Create task
   - Edit task
   - Delete task
   - Mark as complete
   - Dark/Light mode toggle
   - Logout

## Troubleshooting

### Backend Issues:
- **500 errors**: Check Railway logs for database connection issues
- **CORS errors**: Verify CORS_ORIGINS matches your frontend URL exactly
- **Database errors**: Ensure migrations ran successfully

### Frontend Issues:
- **API connection failed**: Verify NEXT_PUBLIC_API_BASE_URL is correct
- **Build failed**: Check Vercel build logs for errors
- **Authentication not working**: Ensure backend is running and accessible

## Free Tier Limits

### Vercel (Frontend):
- ✓ Unlimited deployments
- ✓ 100 GB bandwidth/month
- ✓ Automatic HTTPS
- ✓ Custom domains

### Railway (Backend):
- ✓ $5 free credit/month
- ✓ 500 hours execution time
- ✓ Automatic HTTPS
- ✓ Custom domains

### Neon (Database):
- ✓ 1 project
- ✓ 10 branches
- ✓ 3 GB storage
- ✓ Automatic backups

## Alternative: Deploy Backend to Render

If you prefer Render over Railway:

1. Go to https://render.com
2. Create "New Web Service"
3. Connect GitHub repository
4. Configure:
   - **Root Directory**: `backend`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn src.main:app --host 0.0.0.0 --port $PORT`
5. Add same environment variables as Railway
6. Deploy

## Cost Estimate

**Total Monthly Cost: $0** (using free tiers)
- Vercel: Free
- Railway: Free ($5 credit covers typical usage)
- Neon: Free
- GitHub: Free

## Next Steps

1. Set up custom domain (optional)
2. Configure monitoring and alerts
3. Set up CI/CD for automatic deployments
4. Add analytics (Vercel Analytics is free)
5. Enable error tracking (Sentry free tier)

## Support

If you encounter issues:
1. Check Railway logs: `railway logs`
2. Check Vercel logs in dashboard
3. Check Neon database connection
4. Verify all environment variables are set correctly

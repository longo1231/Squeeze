# 🚀 SqueezeMetrics Dashboard - Render Deployment Guide

## Files Created for Deployment:

### 1. `app.py` 
- Production-ready version of the dashboard
- Fetches data directly from SqueezeMetrics API (no local files)
- Simplified with core functionality: Overview, Portfolio, Analysis
- Configured for Render hosting

### 2. `render.yaml`
- Render service configuration
- Specifies Python environment and build commands

### 3. `requirements.txt` (Updated)
- Simplified dependencies for faster deployment
- Added `gunicorn` for production server

## 🚀 Deployment Steps:

### Step 1: Push to GitHub
```bash
git add .
git commit -m "Add Render deployment configuration"
git push origin main
```

### Step 2: Deploy on Render
1. Go to [render.com](https://render.com) and sign up
2. Click "New +" → "Web Service"
3. Connect your GitHub account
4. Select your `Squeeze` repository
5. Configure:
   - **Name**: `squeezemetrics-dashboard`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python app.py`
   - **Instance Type**: `Free`

### Step 3: Environment Variables (Optional)
- Render will auto-detect Python version
- No additional environment variables needed

## 📊 Production Features:

✅ **Live Data**: Fetches real-time data from SqueezeMetrics API  
✅ **Portfolio Builder**: 20 longs + 40 shorts with $10M volume filter  
✅ **Responsive Design**: Works on mobile and desktop  
✅ **Auto-scaling**: Render handles traffic automatically  
✅ **HTTPS**: Automatic SSL certificate  

## 🔗 Access Your Dashboard:
After deployment, your dashboard will be available at:
`https://squeezemetrics-dashboard.onrender.com`

## 🛠 Local Testing:
Test the production version locally:
```bash
python app.py
```
Visit: `http://localhost:10000`

## 📝 Notes:
- Uses SqueezeMetrics API directly (no Excel files needed)
- Simplified interface for faster loading
- Free tier includes 750 hours/month
- Auto-sleeps after inactivity (30 seconds to wake up)

## 🚨 Troubleshooting:
- If deployment fails, check the build logs in Render dashboard
- API timeouts: Dashboard shows warning if SqueezeMetrics API is unavailable
- Cold starts: First load may take 30 seconds (Render wakes up the service)
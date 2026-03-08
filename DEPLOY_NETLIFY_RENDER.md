# Deploy Original Dashboard to Netlify + Render

## ✅ Your Original Design - 10 Minutes to Live

Your dashboard is ready with the original look and feel. Here's how to deploy:

---

## Step 1: Deploy Backend to Render (3 minutes)

### 1.1 Create Render Account
- Go to https://render.com
- Sign up with GitHub (same account you used for the repo)

### 1.2 Create New Service
1. Click **"New +"** → **"Web Service"**
2. Select your **`Ecommerce-CX-Intelligence-Hub`** repository
3. Fill in:
   - **Name:** `navedas-cx-backend`
   - **Root Directory:** `backend`
   - **Runtime:** `Python 3`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `python server.py`

### 1.3 Deploy
1. Click **"Create Web Service"**
2. Wait for green checkmark (2-3 minutes)
3. Copy your URL (looks like: `https://navedas-cx-backend-xxxxx.onrender.com`)

**Save this URL** ⬅️ You'll need it next

---

## Step 2: Deploy Frontend to Netlify (3 minutes)

### 2.1 Connect Netlify
1. Go to https://app.netlify.com
2. Click **"Add new site"** → **"Import an existing project"**
3. Connect GitHub
4. Select **`Ecommerce-CX-Intelligence-Hub`** repo

### 2.2 Configure Netlify
1. Click **"Deploy site"**
2. Wait for green **"Published"** status (1-2 minutes)

---

## Step 3: Update API Endpoint (2 minutes)

### 3.1 Edit HTML
1. In your GitHub repo, go to **`frontend/index.html`**
2. Find line ~895 with: `return 'https://your-backend.railway.app';`
3. Replace with your Render URL from Step 1.3

### 3.2 Commit & Push
```bash
git add frontend/index.html
git commit -m "Update API endpoint to Render backend"
git push
```

Netlify will auto-redeploy within 1 minute.

---

## ✅ Done!

Your dashboard is now live with:
- ✓ Original design & styling
- ✓ All 1,000 tickets from Excel
- ✓ Live data updates
- ✓ Working filters, charts, exports
- ✓ Responsive design

### Your URLs:
- **Frontend:** `https://your-site-name.netlify.app`
- **Backend:** `https://navedas-cx-backend-xxxxx.onrender.com`

Share the **Frontend URL** with your team! 🎉

---

## Troubleshooting

### "Failed to load data" Error
1. Open DevTools (F12)
2. Check Console
3. Verify API URL is showing your Render URL
4. Make sure Render service is running (green status)

### Render Service Crashes
1. Go to Render dashboard
2. Click your service → Logs
3. Check for errors
4. Common fix: Wait 2 minutes for deployment to fully complete

### Data Not Updating
1. Verify Excel file is in `backend/` folder on GitHub
2. Re-deploy on Render if needed


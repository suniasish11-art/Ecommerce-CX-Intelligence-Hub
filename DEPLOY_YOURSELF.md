# Self-Deploy to Netlify + Railway - Step by Step

## Prerequisites
- GitHub account (free)
- Netlify account (free)
- Railway account (free)
- Git installed on your computer

---

## Part 1: Prepare GitHub Repository (5 minutes)

### 1.1 Create GitHub Repo

1. Go to **https://github.com/new**
2. Name: `navedas-cx-dashboard`
3. Description: "Ecommerce CX Intelligence Dashboard"
4. **Create repository**

### 1.2 Clone & Setup Locally

```bash
# Clone the repo
git clone https://github.com/YOUR_USERNAME/navedas-cx-dashboard.git
cd navedas-cx-dashboard

# Create folder structure
mkdir frontend
mkdir backend
```

### 1.3 Add Files

**Copy to `frontend/` folder:**
- `ecommerce_cx_hub_v10 (3).html` → Rename to `index.html`

**Copy to `backend/` folder:**
- `server.py`
- `navedas_cx_1000 (1).xlsx`
- `requirements.txt`

### 1.4 Push to GitHub

```bash
git add .
git commit -m "Initial commit: Navedas CX Dashboard"
git branch -M main
git push -u origin main
```

---

## Part 2: Deploy Backend to Railway (5 minutes)

### 2.1 Connect Railway to GitHub

1. Go to **https://railway.app**
2. Click **"New Project"**
3. Select **"Deploy from GitHub"**
4. Connect your GitHub account
5. Select **`navedas-cx-dashboard`** repository
6. Select **`backend`** folder as root directory

### 2.2 Configure Environment

1. In Railway, go to **Settings**
2. Add **Variables:**
   ```
   PYTHONUNBUFFERED=1
   PORT=8080
   ```

3. Click **"Deploy"**

### 2.3 Get Backend URL

1. Wait for deployment (green checkmark)
2. Click on your project
3. Copy the **Public URL** (looks like: `https://navedas-cx-backend-prod.railway.app`)
4. **Save this URL** - you'll need it in the next step

---

## Part 3: Update Frontend with Backend URL (2 minutes)

### 3.1 Edit HTML File

1. Open `frontend/index.html`
2. Find line ~895 with:
   ```javascript
   return 'https://your-backend.railway.app';
   ```

3. Replace with your Railway URL:
   ```javascript
   return 'https://navedas-cx-backend-prod.railway.app';
   ```

### 3.2 Push Update to GitHub

```bash
git add frontend/index.html
git commit -m "Update API endpoint to Railway backend"
git push
```

---

## Part 4: Deploy Frontend to Netlify (3 minutes)

### 4.1 Connect Netlify to GitHub

1. Go to **https://app.netlify.com**
2. Click **"Add new site"** → **"Import an existing project"**
3. Connect **GitHub**
4. Select **`navedas-cx-dashboard`** repository
5. Click **"Deploy site"**

### 4.2 Configure Build Settings

If Netlify asks:
- **Build command:** (leave blank)
- **Publish directory:** `frontend`
- Click **"Deploy"**

### 4.3 Get Your Public URL

Netlify will show:
```
https://your-site-name.netlify.app
```

**This is your live dashboard!** 🎉

---

## Part 5: Test Everything

### 5.1 Open Dashboard

Open browser: **https://your-site-name.netlify.app**

### 5.2 Wait for Data

Should see:
```
Loading data from API...
```

Then → **1,000 tickets appear** ✓

### 5.3 Test Features

- [ ] Table shows tickets
- [ ] Can scroll/paginate
- [ ] Filters work (click Loyalty, Revenue, Churn)
- [ ] Search works
- [ ] Can export to CSV
- [ ] Can export to PDF
- [ ] Charts display (click "Show CX Trend")

---

## Troubleshooting

### Problem: "Failed to load data"

**Solution:** Verify backend URL
```javascript
// Open browser DevTools (F12) → Console
// You should see:
// "API Base URL: https://your-railway-url.railway.app"
```

If it shows `http://localhost:8080`, you didn't update the URL correctly.

### Problem: CORS Error

**Solution:** Backend already has CORS enabled. If you still get error:
1. Check Railway deployment is successful (green checkmark)
2. Test API directly: `https://your-railway-url.railway.app/api/data`
3. Should return JSON with 1000 tickets

### Problem: Excel file not found

**Solution:** Make sure Excel file is in `backend/` folder on GitHub and Railway deployed from `backend/` folder

---

## Command Reference

### Push updates to GitHub
```bash
git add .
git commit -m "Your message"
git push
```

### Check Railway deployment status
```
https://railway.app → Select project → View logs
```

### Check Netlify deployment status
```
https://app.netlify.com → Select site → Deploys
```

---

## Final URLs

After deployment, you'll have:

| Component | URL |
|-----------|-----|
| Dashboard | `https://your-site-name.netlify.app` |
| Backend API | `https://your-railway-url.railway.app/api/data` |
| GitHub Repo | `https://github.com/YOUR_USERNAME/navedas-cx-dashboard` |

---

## Share with Team

Send this link to your team:
```
https://your-site-name.netlify.app
```

They'll see:
- ✓ All 1,000 ticket records
- ✓ Live agent performance
- ✓ Real-time KPIs
- ✓ Interactive filters
- ✓ PDF exports

---

## Need Help?

**Check logs:**
- Railway: Project → Deployments → View logs
- Netlify: Site → Deploys → View deploy log

**Common issues:**
- Backend URL not updated → Re-check step Part 3.1
- Port conflicts → Railway auto-manages ports
- Excel file missing → Check it's in `backend/` folder

---

## Time Estimate
- GitHub setup: 5 min
- Railway backend: 5 min
- Update frontend: 2 min
- Netlify frontend: 3 min
- **Total: 15 minutes**

**Let's go!** 🚀

# Deployment Checklist - Print This

## ✓ Pre-Deployment (Do First)

- [ ] Run `setup_for_deployment.bat` in this folder
- [ ] Verify `frontend/` and `backend/` folders created
- [ ] Verify files copied correctly:
  - [ ] `frontend/index.html` exists
  - [ ] `backend/server.py` exists
  - [ ] `backend/navedas_cx_1000 (1).xlsx` exists
  - [ ] `backend/requirements.txt` exists

---

## ✓ GitHub Setup (5 minutes)

### Create Repository
- [ ] Go to https://github.com/new
- [ ] Name: `navedas-cx-dashboard`
- [ ] Description: "Ecommerce CX Intelligence Dashboard"
- [ ] Create repository
- [ ] Copy HTTPS URL (looks like: `https://github.com/YOUR_USERNAME/navedas-cx-dashboard.git`)

### Push Code
```bash
git init
git add .
git commit -m "Initial commit: Navedas CX Dashboard"
git remote add origin YOUR_GITHUB_URL
git branch -M main
git push -u origin main
```

- [ ] Code pushed to GitHub successfully

---

## ✓ Railway Deployment (5 minutes)

### Create Railway Project
- [ ] Go to https://railway.app
- [ ] Click "New Project"
- [ ] Select "Deploy from GitHub"
- [ ] Connect GitHub account
- [ ] Select `navedas-cx-dashboard` repository
- [ ] Select `backend` folder as root directory

### Configure & Deploy
- [ ] Click "Deploy"
- [ ] Wait for green checkmark (deployment complete)
- [ ] Copy Public URL: `https://....railway.app`

**Save this URL:** `_____________________________`

---

## ✓ Update Frontend (2 minutes)

### Edit HTML File
- [ ] Open `frontend/index.html` in text editor
- [ ] Find line ~895: `return 'https://your-backend.railway.app';`
- [ ] Replace with your Railway URL from above
- [ ] Save file

### Push Update
```bash
git add frontend/index.html
git commit -m "Update API endpoint to Railway"
git push
```

- [ ] Update pushed to GitHub

---

## ✓ Netlify Deployment (3 minutes)

### Connect to GitHub
- [ ] Go to https://app.netlify.com
- [ ] Click "Add new site" → "Import an existing project"
- [ ] Select "GitHub"
- [ ] Select `navedas-cx-dashboard` repository
- [ ] Build command: (leave blank)
- [ ] Publish directory: `frontend`
- [ ] Click "Deploy site"

### Wait for Deployment
- [ ] Wait for green "Published" status
- [ ] Copy your Netlify URL: `https://....netlify.app`

**Save this URL:** `_____________________________`

---

## ✓ Testing (5 minutes)

### Open Dashboard
- [ ] Open browser
- [ ] Go to your Netlify URL
- [ ] Wait for "Loading data from API..."

### Verify Data Loads
- [ ] See table with tickets
- [ ] Table shows 1,000 records
- [ ] Check console (F12) for errors

### Test Features
- [ ] Click filter buttons (Loyalty, Revenue, Churn)
- [ ] Type in search box
- [ ] Click "Show CX Trend" button
- [ ] Try "Export CSV" button
- [ ] Try "Export PDF" button
- [ ] Click team cards (Agent Performance)

### Document Results
- [ ] All features working ✓
- [ ] No errors in console ✓
- [ ] Data displaying correctly ✓

---

## ✓ Share with Team

- [ ] Copy your Netlify URL
- [ ] Share URL with team members
- [ ] They can view live dashboard immediately

**Dashboard URL to share:** `_____________________________`

---

## 🆘 Troubleshooting

### "Failed to load data" Error

Check:
1. Open browser DevTools (F12)
2. Go to Console tab
3. Should see: `API Base URL: https://...railway.app`
4. If it shows `localhost`, you didn't update the API URL correctly in step 3

**Fix:** Re-edit `frontend/index.html` with correct Railway URL

### CORS or Network Error

Check:
1. Test Railway API directly: `https://your-railway-url/api/data`
2. Should return JSON with tickets
3. If not, Railway deployment failed

**Fix:** Check Railway logs for errors

### Blank/White Page

Check:
1. Netlify deployed successfully (green checkmark)
2. Console (F12) shows no errors
3. Clear browser cache: Ctrl+Shift+Delete

**Fix:** Redeploy on Netlify

### Excel File Not Found

Check:
1. File is in `backend/` folder on GitHub
2. Railway is reading from `backend/` folder
3. Check Railway logs

**Fix:** Push Excel file to GitHub, redeploy Railway

---

## 📊 Final Status

| Component | Status | URL |
|-----------|--------|-----|
| Frontend | [ ] Deployed | https://... |
| Backend | [ ] Deployed | https://... |
| GitHub | [ ] Ready | https://... |
| Data | [ ] Loading | ✓ Verified |

---

## 🎉 Success Criteria

Your deployment is successful when:

✓ Dashboard loads without errors
✓ Table displays 1,000 tickets
✓ Filters work correctly
✓ Exports generate files
✓ Team can view dashboard
✓ No console errors (F12)

---

## 📞 Need Help?

**Check logs:**
- Railway: Project → Deployments → View log
- Netlify: Site → Deploys → View deploy log

**Common fixes:**
- API URL wrong? → Re-edit step 3
- Excel missing? → Push to GitHub
- Data not loading? → Check Railway URL in HTML

---

**Time to complete: 20 minutes**

**Questions?** See DEPLOY_YOURSELF.md for detailed instructions!

# Deploy to Netlify - 5 Minute Setup

## ⚡ Quick Deploy (Frontend Only to Netlify)

### Option A: Direct HTML Upload to Netlify (Easiest)

1. **Go to:** https://app.netlify.com
2. **Drag & drop:** `ecommerce_cx_hub_v10 (3).html`
3. **Rename to:** `index.html` (for Netlify to serve it)
4. **Deploy!** ✓
5. **Your site:** `https://your-random-name.netlify.app`

**BUT** - You still need a backend. See Step 2 below.

---

## 🚀 Full Deploy (Recommended - Frontend + Backend)

### Step 1: Deploy Backend to Railway (2 minutes)

1. **Go to:** https://railway.app
2. **Sign up** with GitHub
3. **Create Project** → **Provision PostgreSQL** (for simplicity)
4. **Upload files:**
   - `server.py`
   - `navedas_cx_1000 (1).xlsx`
   - `requirements.txt`
5. **Set variables:**
   - `PORT=8080`
6. **Deploy** → Get URL like `https://abc123.railway.app`

### Step 2: Deploy Frontend to Netlify (2 minutes)

1. **Edit HTML file:**
   - Find this line (around line 887):
   ```javascript
   return 'http://localhost:8080'; // fallback
   ```

   - Change to:
   ```javascript
   return 'https://YOUR-RAILWAY-URL.railway.app'; // your backend URL
   ```

2. **Go to:** https://app.netlify.com
3. **Upload updated HTML as index.html**
4. **Done!** ✓

---

## 📋 Checklist

- [ ] Created Railway account
- [ ] Uploaded backend files to Railway
- [ ] Got Railway backend URL
- [ ] Updated API_BASE_URL in HTML
- [ ] Uploaded HTML to Netlify
- [ ] Dashboard loads successfully
- [ ] Can see 1,000 tickets
- [ ] Can export PDF
- [ ] Can filter and search

---

## Testing

1. **Open dashboard:** https://your-site.netlify.app
2. **Wait for data to load** (should see 1,000 tickets)
3. **Test features:**
   - [ ] Table shows data
   - [ ] Filters work
   - [ ] Search works
   - [ ] PDF export works
   - [ ] Charts display

---

## Troubleshooting

### "Failed to load data" error
**Solution:** Check backend URL in HTML is correct
```javascript
// Should be your Railway URL:
return 'https://abc123-project.railway.app';
```

### CORS error
**Solution:** Backend already has CORS enabled, but verify server.py has:
```python
self.send_header("Access-Control-Allow-Origin", "*")
```

### Excel file not found
**Solution:** Make sure `navedas_cx_1000 (1).xlsx` is in same folder as server.py on Railway

---

## Environment-Specific Config

The HTML automatically detects:
- **Local (localhost)** → Uses `http://localhost:8080`
- **Netlify** → Uses your backend URL

Just update this one line in the HTML:
```javascript
// CHANGE THIS when deploying:
return 'https://YOUR-BACKEND-URL.railway.app';
```

---

## Alternative Backend Hosts

| Platform | Cost | Setup |
|----------|------|-------|
| **Railway** | Free tier | ⭐⭐ Easy |
| **Render.com** | Free tier | ⭐⭐ Easy |
| **Heroku** | $7/month | ⭐⭐⭐ Medium |
| **PythonAnywhere** | $5/month | ⭐⭐ Easy |

---

## URLs After Deployment

```
Dashboard Frontend: https://your-site.netlify.app
Backend API:      https://your-backend.railway.app/api/data
```

---

## Files to Upload

**To Netlify (Frontend):**
- `ecommerce_cx_hub_v10 (3).html` (rename to `index.html`)

**To Railway (Backend):**
- `server.py`
- `navedas_cx_1000 (1).xlsx`
- `requirements.txt`

---

**That's it! Your dashboard is live!** 🎉

Share the Netlify URL with your team. They'll see real data from your Excel file, live on the internet.

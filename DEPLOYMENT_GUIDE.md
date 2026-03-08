# Navedas CX Dashboard - Netlify Deployment Guide

## Quick Start (Frontend to Netlify + Backend to Railway)

### Step 1: Deploy Frontend to Netlify

1. **Prepare files:**
   ```
   Copy only these files to netlify-deploy/:
   - ecommerce_cx_hub_v10 (3).html → index.html
   ```

2. **Connect to Git:**
   - Push `netlify-deploy/` folder to GitHub
   - Go to [Netlify](https://app.netlify.com)
   - Click "New site from Git"
   - Select your repository
   - Set publish directory: `netlify-deploy`
   - Deploy!

3. **Result:** Your dashboard will be live at `https://your-site.netlify.app`

---

### Step 2: Deploy Backend to Railway (or Render)

#### Using Railway:

1. **Sign up:** https://railway.app (free tier available)

2. **Create new project:**
   - Click "New Project" → "Deploy from GitHub"
   - OR upload files directly

3. **Upload files:**
   - Create `/backend` folder with:
     - `server.py`
     - `navedas_cx_1000 (1).xlsx`
     - `requirements.txt`

4. **Create `requirements.txt`:**
   ```
   pandas>=1.0
   openpyxl>=3.0
   ```

5. **Railway will:**
   - Auto-detect Python
   - Install dependencies
   - Start `server.py`
   - Give you a public URL: `https://your-backend.railway.app`

#### Using Render.com:

1. **Sign up:** https://render.com

2. **New Web Service:**
   - Select "Python"
   - Build command: `pip install -r requirements.txt`
   - Start command: `python server.py`
   - Environment: `PORT=8080`

---

### Step 3: Update API Endpoint in Dashboard

**In your HTML file, update the API URL:**

Find this line in the load event:
```javascript
fetch('/api/data')
```

Change to:
```javascript
fetch('https://your-backend.railway.app/api/data')
```

Or make it configurable:
```javascript
var API_BASE = window.location.hostname === 'localhost'
  ? 'http://localhost:8080'
  : 'https://your-backend.railway.app';
fetch(API_BASE + '/api/data')
```

---

## Deployment Checklist

- [ ] Frontend HTML copied to Git repo
- [ ] Backend files (server.py, Excel) pushed to GitHub
- [ ] requirements.txt created
- [ ] Netlify site connected and deployed
- [ ] Railway/Render backend deployed
- [ ] Backend URL obtained
- [ ] API endpoint updated in HTML
- [ ] Dashboard loaded successfully
- [ ] Test: Can you see 1,000 tickets?
- [ ] Test: Can you export PDF?
- [ ] Test: Can you filter data?

---

## Environment Variables

For secure deployment, store sensitive data in environment variables:

### Railway:
Go to Project Settings → Variables
```
EXCEL_FILE_PATH=/workspace/navedas_cx_1000\ (1).xlsx
PORT=8080
```

### Render:
Go to Environment
```
EXCEL_FILE_PATH=./navedas_cx_1000\ (1).xlsx
PORT=8080
```

---

## File Structure for Deployment

```
GitHub Repository/
├── netlify-deploy/
│   ├── index.html (your dashboard)
│   └── netlify.toml
│
├── backend/
│   ├── server.py
│   ├── navedas_cx_1000 (1).xlsx
│   └── requirements.txt
│
└── README.md
```

---

## URLs After Deployment

- **Frontend:** https://your-site.netlify.app
- **Backend API:** https://your-backend.railway.app/api/data
- **Dashboard:** https://your-site.netlify.app (fully functional)

---

## Troubleshooting

### Dashboard shows "Failed to load data"
- Check backend URL is correct
- Verify backend is running: https://your-backend.railway.app/api/data
- Check browser console for errors

### CORS errors
- Backend needs CORS headers (server.py already has them)
- Make sure `Access-Control-Allow-Origin: *` is set

### Excel file not found
- Verify file path in server.py
- Use environment variable: `os.getenv('EXCEL_FILE_PATH')`

### Port conflicts
- Set PORT environment variable to different value (8080, 8081, etc.)

---

## Cost

- **Netlify:** FREE (generous limits)
- **Railway:** FREE tier available ($5/month after free credits)
- **Render:** FREE tier with limitations
- **Heroku:** Paid (was free, now $7/month minimum)

---

## Next Steps

1. Choose deployment platform (Railway or Render recommended)
2. Push code to GitHub
3. Connect and deploy
4. Get URLs
5. Update API endpoint
6. Test fully
7. Share dashboard link!

---

**Questions?** Check the platform documentation or reach out!

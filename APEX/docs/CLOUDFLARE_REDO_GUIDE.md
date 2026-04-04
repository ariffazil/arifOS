# Cloudflare Pages Redo - Clean Slate

**Goal:** Delete broken "apex" project, create new one pointing to THEORY folder

**Time:** 5 minutes  
**Difficulty:** Easy (click-by-click instructions)  

---

## ⚠️ BEFORE YOU START

**Don't worry:**
- Your code is safe (it's in GitHub)
- Your domain is safe (apex.arif-fazil.com)
- This just resets the deployment settings

---

## 🔴 STEP 1: Delete the Broken Project

### 1.1 Go to Cloudflare
- Open: https://dash.cloudflare.com
- Log in with your account

### 1.2 Find the Project
- Click **"Workers & Pages"** in the left sidebar
- Find the project named **"apex"** (or "apex-arif-fazil" or similar)
- Click on it

### 1.3 Delete It
- Click **"Settings"** tab at the top
- Scroll to bottom
- Find **"Delete Project"** (red button)
- Click it
- Type "apex" to confirm
- Click **"Delete"**

**Status:** ✅ Old broken project deleted

---

## 🟢 STEP 2: Create New Project (Correctly)

### 2.1 Start New Project
- Click **"Create a project"** button (usually top right)
- Choose **"Pages"**
- Choose **"Connect to Git"**

### 2.2 Connect GitHub
- Click **"Connect GitHub account"** (if not already connected)
- Authorize Cloudflare to access your repos
- Find and select: **ariffazil/arif-fazil-sites**
- Click **"Begin setup"**

### 2.3 Configure Build Settings (IMPORTANT!)

**Project name:** `apex`

**Production branch:** `main`

**Root directory (THIS IS THE FIX!):**
```
THEORY
```
(NOT "soul" — type "THEORY" exactly)

**Build command:**
```
npm run build
```

**Build output directory:**
```
dist
```

### 2.4 Environment Variables
Skip this (none needed)

### 2.5 Save and Deploy
- Click **"Save and Deploy"**

**Status:** ✅ New project created with correct settings

---

## 🟡 STEP 3: Fix Domain (apex.arif-fazil.com)

After deployment finishes:

### 3.1 Go to Project Settings
- Click on your new "apex" project
- Click **"Custom domains"** tab

### 3.2 Add Domain
- Click **"Set up a custom domain"**
- Enter: `apex.arif-fazil.com`
- Click **"Continue"**

### 3.3 Verify
- Cloudflare will check DNS
- If it says "Active" → ✅ Done
- If it says "Error" → Continue to 3.4

### 3.4 Fix DNS (If Needed)
If domain doesn't work:
- Go to Cloudflare dashboard home
- Click your domain: **arif-fazil.com**
- Click **"DNS"** in sidebar
- Add record:
  - Type: **CNAME**
  - Name: **apex**
  - Target: **apex.pages.dev**
  - TTL: Auto
- Save

**Status:** ✅ Domain connected

---

## ✅ VERIFY EVERYTHING WORKS

1. Go to: https://apex.arif-fazil.com
2. Should show your APEX site
3. Check version shows: v55.5-EIGEN
4. Check navigation works

---

## 🎯 WHAT WE FIXED

| Before | After |
|--------|-------|
| Root dir: `soul` (broken) | Root dir: `THEORY` (correct) |
| Build fails | Build succeeds |
| Manual fixes needed | Auto-deploy works |
| Error messages | Clean deploys |

---

## 🆘 TROUBLESHOOTING

### "Project name already exists"
- The old project didn't delete properly
- Go back to Workers & Pages
- Find old "apex" project
- Delete it properly
- Try again

### "Build failed: Cannot find package.json"
- Root directory is wrong
- Go to Settings → Build configuration
- Change "Root directory" to: `THEORY`
- Retry deploy

### Domain shows "Error"
- Wait 5 minutes (DNS takes time)
- Check DNS record exists (Step 3.4)
- Refresh browser

---

## 📞 IF YOU GET STUCK

Take a screenshot of:
1. The error message
2. What step you're on

Send to anyone who knows Cloudflare, or show me.

---

**This is the cleanest fix. Do this once, works forever.**

*"Ditempa Bukan Diberi" — Forged, Not Given*

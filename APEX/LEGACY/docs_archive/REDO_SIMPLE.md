# REDO CLOUDFLARE - SIMPLE VERSION

## Part 1: Delete Broken Project

1. Go to https://dash.cloudflare.com
2. Click "Workers & Pages"
3. Click project named "apex"
4. Click "Settings" tab
5. Scroll down
6. Click red "Delete Project" button
7. Type "apex" to confirm
8. Click "Delete"

## Part 2: Create New Project

1. Click "Create a project"
2. Click "Pages"
3. Click "Connect to Git"
4. Select: ariffazil/arif-fazil-sites
5. Click "Begin setup"
6. Fill in:
   - Project name: `apex`
   - Production branch: `main`
   - Root directory: `THEORY` ← IMPORTANT!
   - Build command: `npm run build`
   - Build output: `dist`
7. Click "Save and Deploy"

## Part 3: Fix Domain

1. Click "Custom domains" tab
2. Click "Set up custom domain"
3. Enter: `apex.arif-fazil.com`
4. Click "Continue"
5. Done

---

**Root directory must be: THEORY**
**NOT: soul**

That's the entire fix.

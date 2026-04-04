# 🔧 Google Workspace (gog) Setup Instructions

## ✅ COMPLETED: What I Did

1. ✅ Saved your `client_secret.json` to the container
2. ✅ Loaded credentials into gog
3. ✅ Set up persistent storage for tokens
4. ✅ Prepared all Google APIs (Gmail, Calendar, Drive, Docs, Sheets, Contacts)

## ⚠️ REQUIRED: OAuth Browser Authentication

**Google OAuth requires a browser** - it cannot be completed headlessly.

### Option A: SSH with Port Forwarding (Recommended)

From your **Windows PC**, run:

```bash
# SSH into VPS with port forwarding
ssh -L 8085:localhost:8085 ariffazil@100.111.84.52

# Then inside the SSH session:
docker exec -it openclaw_gateway bash

# Inside the container:
export PATH="/home/node/.local/bin:/home/node/.npm-global/bin:$PATH"
gog auth add ariffazil@gmail.com --services gmail,calendar,drive,contacts,docs,sheets

# It will give you a URL - copy/paste into your Windows browser
# After auth, it will callback to localhost:8085 which forwards to the container
```

### Option B: Use OpenClaw's Built-in Browser

If the `browser` skill is available in OpenClaw:

```
# In OpenClaw chat/telegram
/browser gog auth add ariffazil@gmail.com --services gmail,calendar,drive
```

### Option C: Desktop Setup (Copy Token)

1. Install gog on your Windows PC:
   ```powershell
   # On Windows (if using WSL or have go installed)
   go install github.com/steipete/gogcli@latest
   ```

2. Authenticate on Windows:
   ```bash
   gog auth credentials client_secret.json
   gog auth add ariffazil@gmail.com --services gmail,calendar,drive,contacts,docs,sheets
   ```

3. Copy the token file to VPS:
   ```bash
   scp ~/.config/gogcli/tokens.json ariffazil@100.111.84.52:/tmp/
   ssh ariffazil@100.111.84.52
   sudo cp /tmp/tokens.json /opt/arifos/data/openclaw/gog/
   ```

### Option D: Service Account (Server-to-Server)

For **headless/server use**, create a Google Service Account instead:

1. Go to: https://console.cloud.google.com/iam-admin/serviceaccounts
2. Create Service Account → Download JSON key
3. Share your Google Calendar/Gmail with the service account email
4. Use service account auth (different from OAuth)

---

## 📋 CURRENT STATUS

```bash
# Credentials loaded:
~/.openclaw/gog/credentials.json ✓

# Ready to authenticate:
~/.openclaw/gog/tokens.json ⏳ (needs OAuth flow)
```

---

## 🚀 AFTER AUTHENTICATION

Once OAuth is complete, gog will work in OpenClaw:

```bash
# Gmail
gog gmail search 'newer_than:7d' --max 10
gog gmail send --to someone@example.com --subject "Hello" --body "Message"

# Calendar
gog calendar events primary --from 2026-03-01 --to 2026-03-31
gog calendar create primary --summary "Meeting" --from 2026-03-10T10:00:00Z --to 2026-03-10T11:00:00Z

# Drive
gog drive search "project" --max 10
gog drive upload file.pdf --folder "Documents"
```

---

## 💡 RECOMMENDATION

**Use Option A (SSH port forwarding)** - it's the fastest and keeps everything on the VPS.

1. Open PowerShell on your Windows PC
2. Run the SSH command with port forwarding
3. Follow the OAuth flow in your browser
4. Done - gog will be fully configured

---

**Need help with any of these steps?**

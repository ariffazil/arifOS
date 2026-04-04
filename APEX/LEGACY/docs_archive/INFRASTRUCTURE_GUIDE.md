# arifOS Infrastructure Guide (EL15)

**Version:** v50.0.0
**Target Audience:** Beginners ("Explain Like I'm 5 / 15")

This guide explains how **Docker** and **Railway** work, using simple analogies, so you can confidently deploy your arifOS MCP server.

---

## 1. What is Docker? (The "Shipping Container")

Imagine you baked a **cake** (your code).
- It tastes great in your kitchen (your computer).
- But when you mail it to a friend, it arrives smashed because their plate is different, or the temperature changed.

**Docker** is like a magic, indestructible **shipping container** for your cake.
1. You put your cake + your specific plate + the exact air temperature inside the container.
2. You seal it.
3. Now, you can ship this container *anywhere* (your friend's house, a big server, the cloud).
4. When they open it, it runs *exactly* as it did in your kitchen.

### Key Terms
- **Dockerfile** (`Recipe`): A text file that tells Docker how to pack the container. "Start with Python, add these files, install these libraries."
- **Image** (`The Packed Container`): The frozen, read-only snapshot of your app.
- **Container** (`The Opened Box`): A running instance of your Image. You can run 1 or 100 copies of it.
- **Docker Desktop**: The program on your Windows PC that builds and runs these containers.

### How to Use It
In your terminal:
```bash
# 1. Build the container (Pack the box)
docker build -t arifos-server .

# 2. Run the container (Open/Run the box)
# -p 8000:8000 means "connect port 8000 on my PC to port 8000 inside the box"
docker run -p 8000:8000 arifos-server
```

---

## 2. What is Railway? (The "Cloud Butler")

You have your **Docker container** (your magic box). Now you want it to run **24/7 on the internet**, not just on your laptop.

**Railway** is a service (like a hotel for apps) that:
1. Translates your code into a running website/service.
2. Gives it a permanent address (URL).
3. Keeps it running even if you turn off your computer.

### How it Works with arifOS
1. You push your code to **GitHub**.
2. **Railway** sees the change.
3. Railway reads your **Dockerfile** (or `railway.json`).
4. Railway builds the container *for you* in the cloud.
5. Railway launches it and gives you a link (e.g., `https://arifos-production.up.railway.app`).

---

## 3. Deployment Steps

### Method A: The Lazy Way (Recommended)
1. Commit your changes to GitHub.
   ```bash
   git add .
   git commit -m "Update server"
   git push
   ```
2. Railway (if connected) will automatically redeploy.

### Method B: Manual Docker Test (Verify before deploy)
1. Open **Docker Desktop**.
2. Run in terminal:
   ```bash
   docker build -t test-arifos .
   docker run -p 8000:8000 test-arifos
   ```
3. Check `http://localhost:8000/health`. If it says "OK", your code works!

---

## 4. MCP & Model Agnosticism

**"Model Agnostic"** just means your code doesn't care which AI brain it talks to.
- Old way: Code says "Call OpenAI GPT-4".
- New way: Code says "Call `ENV.MODEL_NAME`" (which could be GPT-4, Claude, or local Llama).

We achieve this using **Environment Variables** (`.env`).
- On your laptop, `.env` might say `MODEL=llama3`.
- On Railway, the Environment Variable says `MODEL=gpt-4-turbo`.
- **The code stays the same.**

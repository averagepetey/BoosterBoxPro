# Mobile Testing Setup Guide

## 📱 How to Test on Your Phone

### Step 1: Find Your Computer's IP Address

**On Mac:**
```bash
ifconfig | grep "inet " | grep -v 127.0.0.1
```
Look for an IP like `192.168.x.x` or `10.0.x.x`

**Or use:**
```bash
ipconfig getifaddr en0
```

**On Windows:**
```bash
ipconfig
```
Look for "IPv4 Address" under your active network adapter

**On Linux:**
```bash
hostname -I
```

### Step 2: Start Frontend with Network Access

The Next.js dev server needs to be accessible on your local network.

**Option A: Start with explicit host (Recommended)**
```bash
cd frontend
npm run dev -- -H 0.0.0.0
```

**Option B: Modify package.json script**
Add `-H 0.0.0.0` to the dev script in `frontend/package.json`:
```json
"dev": "next dev -H 0.0.0.0"
```

Then run:
```bash
cd frontend
npm run dev
```

### Step 3: Configure Backend CORS (If Needed)

The backend should already allow connections from your network, but verify in `main.py`:
```python
allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"]
```

You may need to add your phone's IP or use a wildcard for development:
```python
allow_origins=["*"]  # Only for development!
```

### Step 4: Update Frontend API URL

The frontend needs to know where to find the backend when accessed from your phone.

**Option A: Use your computer's IP for API calls**

Create/update `frontend/.env.local`:
```bash
NEXT_PUBLIC_API_URL=http://YOUR_COMPUTER_IP:8000
```

Replace `YOUR_COMPUTER_IP` with the IP from Step 1 (e.g., `192.168.1.100`)

**Option B: Use environment variable in code**

The frontend already uses `process.env.NEXT_PUBLIC_API_URL` with a fallback to `localhost:8000`. You'll need to set this.

### Step 5: Access from Your Phone

1. **Make sure your phone is on the same Wi-Fi network** as your computer

2. **Open browser on your phone** and go to:
   ```
   http://YOUR_COMPUTER_IP:3000
   ```
   Replace `YOUR_COMPUTER_IP` with your actual IP (e.g., `192.168.1.100:3000`)

3. **You should see the app!**

### Step 6: Test Everything

- [ ] Dashboard loads
- [ ] Leaderboard displays
- [ ] Can click boxes to see detail page
- [ ] Mobile layout looks good
- [ ] Navigation works
- [ ] Charts display correctly

## 🔧 Troubleshooting

### "This site can't be reached"
- **Check:** Phone and computer are on same Wi-Fi network
- **Check:** Firewall isn't blocking port 3000
- **Check:** IP address is correct

### "Failed to fetch" or API errors
- **Check:** Backend is running
- **Check:** `NEXT_PUBLIC_API_URL` in `.env.local` points to your computer's IP
- **Check:** Backend CORS allows your phone's IP

### Can't find IP address
- **Mac:** System Preferences → Network → Wi-Fi → Advanced → TCP/IP
- **Windows:** Settings → Network & Internet → Wi-Fi → Properties

### Firewall blocking
**Mac:**
```bash
# Allow incoming connections on port 3000
sudo /usr/libexec/ApplicationFirewall/socketfilterfw --add /usr/local/bin/node
```

**Or:** System Preferences → Security & Privacy → Firewall → Firewall Options → Add Node.js

**Windows:**
- Windows Defender Firewall → Allow an app → Add Node.js

## 🚀 Quick Start Commands

```bash
# 1. Find your IP
ipconfig getifaddr en0  # Mac
# or
hostname -I  # Linux

# 2. Start frontend with network access
cd frontend
npm run dev -- -H 0.0.0.0

# 3. Make sure backend is running
# (In another terminal)
python main.py

# 4. Create .env.local with your IP
echo "NEXT_PUBLIC_API_URL=http://YOUR_IP:8000" > frontend/.env.local

# 5. Access from phone
# http://YOUR_IP:3000
```

## 📝 Example

If your computer's IP is `192.168.1.100`:

1. Start frontend: `npm run dev -- -H 0.0.0.0`
2. Create `frontend/.env.local`: `NEXT_PUBLIC_API_URL=http://192.168.1.100:8000`
3. Access from phone: `http://192.168.1.100:3000`

## ⚠️ Security Note

This setup is for **development only**. Don't use `allow_origins=["*"]` or expose ports in production!



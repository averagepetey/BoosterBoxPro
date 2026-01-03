# 📱 Quick Start: Test on Your Phone

## Step 1: Find Your Computer's IP Address

**On Mac:**
```bash
ipconfig getifaddr en0
```

**Or check System Preferences:**
- System Preferences → Network → Wi-Fi → Advanced → TCP/IP
- Look for "IPv4 Address" (something like `192.168.1.100`)

**On Windows:**
```bash
ipconfig
```
Look for "IPv4 Address" under your Wi-Fi adapter

## Step 2: Start the Frontend (Already Configured!)

The frontend is already set to accept network connections. Just start it:

```bash
cd frontend
npm run dev
```

You should see:
```
- Local:        http://localhost:3000
- Network:      http://192.168.x.x:3000
```

**Note the Network URL** - that's what you'll use on your phone!

## Step 3: Update API URL for Mobile

Create `frontend/.env.local` file:

```bash
cd frontend
echo "NEXT_PUBLIC_API_URL=http://YOUR_IP:8000" > .env.local
```

Replace `YOUR_IP` with your computer's IP from Step 1.

**Example:**
```bash
echo "NEXT_PUBLIC_API_URL=http://192.168.1.100:8000" > .env.local
```

**Important:** Restart the frontend dev server after creating `.env.local`:
```bash
# Stop the server (Ctrl+C), then:
npm run dev
```

## Step 4: Make Sure Backend is Running

In a separate terminal:
```bash
python main.py
```

The backend is already configured to accept connections from your network.

## Step 5: Access from Your Phone

1. **Make sure your phone is on the same Wi-Fi network** as your computer

2. **Open a browser on your phone** (Safari, Chrome, etc.)

3. **Go to the Network URL** shown when you started the frontend:
   ```
   http://192.168.x.x:3000
   ```
   (Use the IP address from Step 1)

4. **You should see the app!** 🎉

## Step 6: Test Everything

- [ ] Dashboard loads
- [ ] Leaderboard shows boxes
- [ ] Can click a box to see detail page
- [ ] Mobile layout looks good
- [ ] Navigation hamburger menu works
- [ ] Charts display correctly
- [ ] Touch interactions work smoothly

## 🔧 Troubleshooting

### "This site can't be reached"
- ✅ Check: Phone and computer are on **same Wi-Fi network**
- ✅ Check: Firewall isn't blocking port 3000
- ✅ Check: IP address is correct (no typos)

### "Failed to fetch" or API errors
- ✅ Check: Backend is running (`python main.py`)
- ✅ Check: `.env.local` has correct IP address
- ✅ Check: Restarted frontend after creating `.env.local`

### Can't find IP address
**Mac:**
- System Preferences → Network → Wi-Fi → Advanced → TCP/IP
- Look for "IPv4 Address"

**Windows:**
- Settings → Network & Internet → Wi-Fi → Properties
- Look for "IPv4 address"

### Firewall Blocking?

**Mac:**
1. System Preferences → Security & Privacy → Firewall
2. Click "Firewall Options"
3. Make sure Node.js is allowed, or temporarily disable firewall for testing

**Windows:**
1. Windows Defender Firewall → Allow an app
2. Add Node.js or allow port 3000

## 📝 Example Walkthrough

If your computer's IP is `192.168.1.100`:

1. **Start frontend:**
   ```bash
   cd frontend
   npm run dev
   ```
   See: `Network: http://192.168.1.100:3000`

2. **Create .env.local:**
   ```bash
   echo "NEXT_PUBLIC_API_URL=http://192.168.1.100:8000" > frontend/.env.local
   ```

3. **Restart frontend** (stop with Ctrl+C, then `npm run dev` again)

4. **On your phone:** Open `http://192.168.1.100:3000`

5. **Test the app!**

## ✅ Success!

You'll know it's working when:
- ✅ App loads on your phone
- ✅ Dashboard shows boxes
- ✅ Can navigate and interact
- ✅ Mobile layout looks good
- ✅ No console errors

## 🎯 Pro Tips

- **Keep both terminals open:** One for frontend, one for backend
- **Use the Network URL:** Next.js shows it when you start the dev server
- **Same Wi-Fi:** Phone and computer must be on the same network
- **Restart after .env.local:** Frontend needs to restart to pick up new env vars



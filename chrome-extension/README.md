# BoosterBoxPro Chrome Extension

**Location:** In your project root, the extension lives in the **`chrome-extension`** folder:

```
BoosterBoxPro/
├── chrome-extension/     ← HERE
│   ├── manifest.json
│   ├── background.js
│   ├── content/
│   ├── popup/
│   └── icons/
├── frontend/
├── app/
└── ...
```

## How to load it in Chrome

1. **Open Chrome** and go to:  
   `chrome://extensions/`

2. **Turn on Developer mode** (toggle in the top-right).

3. Click **“Load unpacked”**.

4. **Select the `chrome-extension` folder**  
   - In the file picker, go to your BoosterBoxPro project.
   - Open the **`chrome-extension`** folder (the one that contains `manifest.json`).
   - Click **“Select”** (or “Open” on Mac).

5. The extension should appear in the list and show a BoosterBoxPro icon in the Chrome toolbar.

## Quick path

- **Mac:**  
  `Desktop → Vibe Code Bin → BoosterBoxPro → chrome-extension`

- **Or in Terminal:**  
  `cd "/Users/johnpetersenhomefolder/Desktop/Vibe Code Bin/BoosterBoxPro/chrome-extension"`  
  Then in the “Load unpacked” dialog you can paste that path or navigate there.

## Using it

- Click the extension icon → **“Open Extension”** to show the panel on the current tab.
- On a **TCGplayer** booster box product page, the sidebar shows the same metrics as the dashboard box detail.
- **“Open Full Dashboard”** opens the main app (e.g. `http://localhost:3000/dashboard`).

## Requirements

- **Backend must be running** for the extension to load data. Start it with `python main.py` in the project root (see project **START_SERVERS.md**). Default API URL: `http://localhost:8000`.

## Connection error?

1. **Start the backend:** In the project folder run `python main.py` (or your usual command). You should see “Uvicorn running on http://0.0.0.0:8000”.
2. **Check the URL:** Right‑click the BoosterBoxPro icon → **Options**. Set “Backend API URL” to your server (e.g. `http://localhost:8000` or your deployed URL). Click **Save**.
3. **Reload the TCGplayer tab** and click **Retry** in the extension panel.
4. If you use a different host (e.g. `http://127.0.0.1:8000`), set that in Options and save.

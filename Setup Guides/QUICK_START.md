# Quick Start - Virtual Environment Setup

## ✅ Python 3.11 is Installed!

Now follow these commands **one at a time** in your terminal:

---

## Step-by-Step Commands

### 1. Navigate to Project Directory
```bash
cd "/Users/johnpetersenhomefolder/Desktop/Vibe Code Bin/BoosterBoxPro"
```

### 2. Create Virtual Environment
```bash
python3.11 -m venv venv
```

### 3. Activate Virtual Environment
```bash
source venv/bin/activate
```

You should see `(venv)` appear in your terminal prompt.

### 4. Upgrade pip
```bash
pip install --upgrade pip
```

### 5. Install All Dependencies
```bash
pip install -r requirements.txt
```

**This will take 2-3 minutes** - you'll see packages downloading and installing.

### 6. Verify Installation
```bash
python -c "import fastapi; print('✅ FastAPI installed')"
python -c "import sqlalchemy; print('✅ SQLAlchemy installed')"
python -c "import alembic; print('✅ Alembic installed')"
```

---

## ✅ Success Checklist

After running all commands, you should have:

- [ ] `venv/` directory created in your project
- [ ] `(venv)` showing in your terminal prompt when activated
- [ ] All packages installed (no errors)
- [ ] FastAPI, SQLAlchemy, and Alembic import successfully

---

## 🔧 If You Encounter Errors

### Error: "command not found: python3.11"
**Solution:** Try `python3` instead, or check where Python 3.11 is installed:
```bash
which python3.11
# If not found, try:
brew list python@3.11
```

### Error: "Permission denied"
**Solution:** Don't use `sudo`. Virtual environments should be created without sudo.

### Error: "Failed building wheel for asyncpg"
**Solution:** Install build tools:
```bash
xcode-select --install
# Then try again
pip install -r requirements.txt
```

---

## 🎯 What's Next?

Once everything is installed and verified:

**Next Step:** Phase 1, Step 2 - Database Setup
- Install PostgreSQL 15+
- Create database
- Configure connection

---

**Run the commands above and let me know when you're done!** 🚀


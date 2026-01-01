# Virtual Environment Setup Guide - Step by Step

## Current Status

Your system has Python 3.9.6 installed, but this project requires **Python 3.11+**.

## Option 1: Check if you have Python 3.11+ available

First, let's check if you have a newer Python version:

```bash
# Check for Python 3.11
python3.11 --version

# Check for Python 3.12
python3.12 --version

# Check for Python 3.13
python3.13 --version
```

If any of these work, use that version instead of `python3`.

---

## Option 2: Install Python 3.11+ (if needed)

### On macOS (using Homebrew):

```bash
# Install Homebrew (if not already installed)
# Visit: https://brew.sh

# Install Python 3.11
brew install python@3.11

# Or install latest Python
brew install python@3.12

# After installation, you can use:
python3.11 -m venv venv
# OR
python3.12 -m venv venv
```

### Alternative: Use pyenv (Python Version Manager)

```bash
# Install pyenv
brew install pyenv

# Install Python 3.11
pyenv install 3.11.9

# Set it for this project
pyenv local 3.11.9

# Now python3 will use 3.11.9
python3 --version  # Should show 3.11.9
```

---

## Step-by-Step: Creating the Virtual Environment

Once you have Python 3.11+ available, follow these steps:

### Step 1: Navigate to Project Directory

```bash
cd "/Users/johnpetersenhomefolder/Desktop/Vibe Code Bin/BoosterBoxPro"
```

### Step 2: Create Virtual Environment

```bash
# Using Python 3.11 (if you installed it)
python3.11 -m venv venv

# OR if your default python3 is 3.11+
python3 -m venv venv
```

**What this does:** Creates a `venv/` directory with an isolated Python environment.

### Step 3: Activate the Virtual Environment

```bash
# On macOS/Linux
source venv/bin/activate

# On Windows (if you're on Windows)
venv\Scripts\activate
```

**What this does:** Activates the virtual environment. You should see `(venv)` in your terminal prompt.

**Verification:** After activation, check:
```bash
which python  # Should point to venv/bin/python
python --version  # Should show Python 3.11+
```

### Step 4: Upgrade pip

```bash
pip install --upgrade pip
```

**What this does:** Upgrades pip to the latest version for better package installation.

### Step 5: Install Project Dependencies

```bash
pip install -r requirements.txt
```

**What this does:** Installs all the packages listed in `requirements.txt`.

**This will take a few minutes.** You'll see packages downloading and installing.

### Step 6: Verify Installation

Check that key packages are installed:

```bash
# Check FastAPI
python -c "import fastapi; print(f'FastAPI {fastapi.__version__}')"

# Check SQLAlchemy
python -c "import sqlalchemy; print(f'SQLAlchemy {sqlalchemy.__version__}')"

# Check Alembic
python -c "import alembic; print(f'Alembic {alembic.__version__}')"
```

All three should print version numbers without errors.

---

## Troubleshooting

### Issue: "command not found: python3.11"

**Solution:** You need to install Python 3.11+. See Option 2 above.

### Issue: "ERROR: Failed building wheel for asyncpg"

**Solution:** You may need to install build tools:
```bash
# On macOS
xcode-select --install

# Then try again
pip install -r requirements.txt
```

### Issue: "Permission denied"

**Solution:** Make sure you're not using `sudo`. Virtual environments should be created without sudo.

### Issue: "ModuleNotFoundError" after installation

**Solution:** Make sure the virtual environment is activated (you should see `(venv)` in your prompt).

---

## Deactivating the Virtual Environment

When you're done working:

```bash
deactivate
```

**What this does:** Deactivates the virtual environment and returns to your system Python.

---

## Quick Reference Commands

```bash
# Create venv
python3.11 -m venv venv  # or python3 if 3.11+

# Activate
source venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Verify
python --version
python -c "import fastapi; print('FastAPI installed')"

# Deactivate (when done)
deactivate
```

---

## Next Steps

Once the virtual environment is set up and dependencies are installed:

1. ✅ Virtual environment created
2. ✅ Dependencies installed
3. ➡️ **Next:** Step 2 - Database Setup (PostgreSQL)

---

**Need help?** If you encounter any issues, share the error message and we'll troubleshoot!


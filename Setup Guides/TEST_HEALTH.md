# Test /health Endpoint

## Prerequisites

Make sure the FastAPI server is running:

```bash
source venv/bin/activate
uvicorn app.main:app --reload
```

## Test Methods

### Option 1: Using the Test Script

```bash
source venv/bin/activate
python scripts/test_health_endpoint.py
```

### Option 2: Using curl

```bash
curl http://localhost:8000/health
```

### Option 3: Using Browser

Open in your browser:
- http://localhost:8000/health

### Option 4: Using Python requests

```bash
source venv/bin/activate
python -c "import requests; print(requests.get('http://localhost:8000/health').json())"
```

## Expected Response

```json
{
  "status": "healthy",
  "environment": "development"
}
```

## Troubleshooting

### "Connection refused" or "Could not connect"

- Make sure the server is running
- Check that it's running on port 8000
- Verify with: `curl http://localhost:8000/`

### "Module not found: requests"

Install requests:
```bash
pip install requests
```

---

**Start the server, then test the endpoint!**


# Admin API Key Configuration

## Development Mode (Default)

If no `ADMIN_API_KEY` is set in your `.env` file, the admin endpoints will accept **any** API key (or no key at all). This is for development convenience.

## Production Mode

To require authentication, set `ADMIN_API_KEY` in your `.env` file:

```bash
ADMIN_API_KEY=your-secret-key-here
```

Then use this key in API requests:

```bash
curl -H "X-API-Key: your-secret-key-here" http://localhost:8000/api/v1/admin/boxes
```

## Current Behavior

- **If `ADMIN_API_KEY` is NOT set**: Admin endpoints accept any API key (development mode)
- **If `ADMIN_API_KEY` IS set**: Admin endpoints require the exact key to match

## Registering Boxes

The `scripts/register_boxes.py` script uses `dev-key` by default, which works fine if `ADMIN_API_KEY` is not set.

If you've set `ADMIN_API_KEY`, either:
1. Remove it from `.env` (development), OR
2. Update the script to use your key, OR
3. Pass the key as an argument: `python scripts/register_boxes.py --api-key your-key`


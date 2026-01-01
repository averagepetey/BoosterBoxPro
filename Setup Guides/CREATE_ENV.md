# Creating .env File

## Your Supabase Connection String

Your connection string has been configured in `.env` file.

**IMPORTANT:** You need to replace `[YOUR-PASSWORD]` with your actual Supabase database password.

### Steps:

1. **Find your Supabase password:**
   - Go to your Supabase project dashboard
   - Project Settings → Database
   - Your password is shown there (or reset it if needed)

2. **Update .env file:**
   ```bash
   # Open .env file
   nano .env
   # OR
   code .env  # if using VS Code
   ```

3. **Replace `[YOUR-PASSWORD]` with your actual password:**
   ```
   DATABASE_URL=postgresql+asyncpg://postgres:YOUR_ACTUAL_PASSWORD@db.umjtdtksqxtyqeqddwkv.supabase.co:5432/postgres
   ```

4. **Save the file**

5. **Test the connection:**
   ```bash
   source venv/bin/activate
   python scripts/test_db_connection.py
   ```

---

## Note

The connection string has been updated from `postgresql://` to `postgresql+asyncpg://` to support async operations with SQLAlchemy.

---

## Security

- The `.env` file is already in `.gitignore` - it won't be committed to git
- Never share your `.env` file or commit it to version control
- Your database password is sensitive information


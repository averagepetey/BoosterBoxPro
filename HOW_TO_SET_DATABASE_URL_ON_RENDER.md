# How to set DATABASE_URL on Render (step-by-step)

This is **step 2** when fixing “Database connection error” on sign-in: make sure your Render **API** service has the correct `DATABASE_URL`.

---

## Part A – Where to set it in the Render dashboard

1. **Open Render**  
   Go to [dashboard.render.com](https://dashboard.render.com) and log in.

2. **Open your project**  
   Click the project that has your BoosterBoxPro backend (the one you connected from GitHub).

3. **Open the API Web Service**  
   Click the **Web Service** that runs your FastAPI backend (often named something like `boosterboxpro-api` or `boosterboxpro`).  
   Do **not** use the Cron Job — the Cron Job has its own env; you want the **API** service.

4. **Go to Environment**  
   In the left sidebar, click **Environment** (or the “Environment” tab if your layout shows it at the top).

5. **Add or edit DATABASE_URL**  
   - If **DATABASE_URL** is already in the list: click it and update the value to your Supabase URL (see Part B below), then save.  
   - If it’s not there: click **“Add Environment Variable”** (or **“Add Variable”**).  
     - **Key:** `DATABASE_URL`  
     - **Value:** paste your full Supabase connection string (from Part B).

6. **Save**  
   When you add or change an env var, Render usually redeploys the service. Wait until the deploy finishes (status “Live”) before trying sign-in again.

---

## Part B – Where to get the DATABASE_URL value (from Supabase)

You need the **database connection string** from Supabase, then you turn it into the form Render expects.

1. **Open Supabase**  
   Go to [supabase.com/dashboard](https://supabase.com/dashboard) and open the project you use for BoosterBoxPro.

2. **Open Database settings**  
   Click the **gear icon** (Project Settings) in the left sidebar, then click **Database**.

3. **Get the connection string**  
   Scroll to **“Connection string”**.  
   - Choose the **“URI”** tab (not “Session mode” / “Transaction” unless you use the pooler).  
   - Copy the string. It will look like:
     ```text
     postgresql://postgres:[YOUR-PASSWORD]@db.xxxxxxxxxxxxx.supabase.co:5432/postgres
     ```

4. **Turn it into the value for Render**  
   - Replace `postgresql://` with **`postgresql+asyncpg://`** (required for the Python backend).  
   - Replace `[YOUR-PASSWORD]` with your **real database password** (the one you set when you created the project).  
     If you don’t remember it: same Database page in Supabase has **“Database password”** → **“Reset database password”**.  
   - Add **`?sslmode=require`** at the end if it’s not already there.

   **Example**  
   Supabase shows:
   ```text
   postgresql://postgres:[YOUR-PASSWORD]@db.abcdefghijk.supabase.co:5432/postgres
   ```
   You put in Render:
   ```text
   postgresql+asyncpg://postgres:YourActualPassword123@db.abcdefghijk.supabase.co:5432/postgres?sslmode=require
   ```

5. **Paste that whole line** into the **Value** field for `DATABASE_URL` on Render (no spaces, no line breaks, no quotes around it).

---

## Checklist

- [ ] You’re on the **API** Web Service in Render, not the Cron Job.  
- [ ] **Environment** → `DATABASE_URL` exists and has a value.  
- [ ] The value starts with `postgresql+asyncpg://` and ends with `?sslmode=require` (or contains `?sslmode=require`).  
- [ ] The password in the URL is the real Supabase database password, not `[YOUR-PASSWORD]`.  
- [ ] After saving, you waited for Render to finish redeploying before testing sign-in again.

If you use Supabase’s **connection pooler** (e.g. port **6543** or a URL with `pooler.supabase.com`), use that full URL instead, but still:
- use `postgresql+asyncpg://`, and  
- the backend will use SSL because the host contains `supabase`.

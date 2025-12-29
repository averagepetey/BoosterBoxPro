# Step 3: Run Database Migrations

## Migration Files Created

I've created the initial migration file that will create all the database tables. 

## Next Steps: Run the Migrations

### 1. Review the Migration (Optional)

```bash
# View the migration file
cat migrations/versions/001_initial_schema.py
```

### 2. Run the Migration

```bash
# Activate virtual environment
source venv/bin/activate

# Run migrations
alembic upgrade head
```

This will:
- Create all tables in your PostgreSQL database
- Set up all indexes and constraints
- Create foreign key relationships

### 3. Verify Migration Success

```bash
# Check current migration version
alembic current

# Check migration history
alembic history
```

You should see:
- Current revision: `001`
- All tables created successfully

### 4. Verify Tables Created

You can verify tables were created in your database. In Supabase:
- Go to Table Editor
- You should see all the tables listed

Or use psql:
```bash
# Connect to your database (if you have psql installed)
psql "postgresql://postgres:YOUR_PASSWORD@db.umjtdtksqxtyqeqddwkv.supabase.co:5432/postgres"

# List tables
\dt

# Exit
\q
```

---

## Tables Created

The migration creates these tables:

1. **booster_boxes** - Core entity table (product master data)
2. **tcg_listings_raw** - TCGplayer listings (placeholder for future API)
3. **tcg_box_metrics_daily** - Daily TCGplayer metrics
4. **ebay_sales_raw** - eBay sales (placeholder for future API)
5. **ebay_box_metrics_daily** - Daily eBay metrics
6. **box_metrics_unified** - Unified metrics (PRIMARY table for leaderboard)
7. **tcg_listing_changes** - Audit log for listing changes
8. **users** - User accounts for authentication
9. **user_favorites** - User favorite boxes (many-to-many)

---

## Troubleshooting

### Error: "Target database is not up to date"

This means the database already has some tables. You may need to:
1. Check if tables already exist
2. If they do, you may need to stamp the migration as applied: `alembic stamp head`
3. Or drop existing tables and re-run: `alembic downgrade base && alembic upgrade head`

### Error: "Can't locate revision identified by '001'"

Make sure the migration file is in `migrations/versions/` directory and has the correct format.

### Error: Connection refused

Verify your `.env` file has the correct `DATABASE_URL` and password.

---

**Run `alembic upgrade head` to create all tables!**


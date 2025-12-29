#!/bin/bash
# Script to run Alembic migrations

echo "🚀 Running database migrations..."
echo ""

# Activate virtual environment
source venv/bin/activate

# Run migrations
echo "Running: alembic upgrade head"
alembic upgrade head

echo ""
echo "✅ Migration complete!"
echo ""
echo "To verify tables were created, run:"
echo "  alembic current"
echo "  alembic history"


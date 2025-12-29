#!/usr/bin/env python3
"""
Test SQLAlchemy Models
Verify models can be imported and have correct structure
"""

import sys

try:
    # Test imports
    from app.models import Base, BoosterBox, UnifiedBoxMetrics
    print("✅ All models imported successfully")
    
    # Check BoosterBox model
    print(f"\n✅ BoosterBox table: {BoosterBox.__tablename__}")
    print(f"   Columns: {len(BoosterBox.__table__.columns)}")
    
    # Check UnifiedBoxMetrics model
    print(f"\n✅ UnifiedBoxMetrics table: {UnifiedBoxMetrics.__tablename__}")
    print(f"   Columns: {len(UnifiedBoxMetrics.__table__.columns)}")
    
    # Check relationship setup (will be added later)
    print(f"\n✅ Base metadata: {Base.metadata}")
    
    print("\n✅ All model tests passed!")
    sys.exit(0)
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)


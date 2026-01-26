#!/usr/bin/env python3
"""
Stripe Configuration Verification Script
Checks if Stripe is properly configured without exposing sensitive values
"""

import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

try:
    import stripe
    from app.config import settings
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("   Make sure you're in the virtual environment: source venv/bin/activate")
    sys.exit(1)


def check_env_var(name: str, required: bool = True) -> tuple[bool, str]:
    """Check if environment variable is set"""
    value = os.getenv(name) or getattr(settings, name.lower(), None)
    if not value:
        if required:
            return False, f"❌ {name} is not set"
        else:
            return True, f"⚠️  {name} is not set (optional)"
    
    # Check format
    if name == "STRIPE_SECRET_KEY":
        if not value.startswith("sk_"):
            return False, f"❌ {name} format invalid (should start with 'sk_')"
        return True, f"✅ {name} is set (starts with 'sk_...')"
    
    elif name == "STRIPE_PUBLISHABLE_KEY":
        if not value.startswith("pk_"):
            return False, f"❌ {name} format invalid (should start with 'pk_')"
        return True, f"✅ {name} is set (starts with 'pk_...')"
    
    elif name == "STRIPE_WEBHOOK_SECRET":
        if not value.startswith("whsec_"):
            return False, f"❌ {name} format invalid (should start with 'whsec_')"
        return True, f"✅ {name} is set (starts with 'whsec_...')"
    
    elif name.startswith("STRIPE_PRICE_ID_"):
        if not value.startswith("price_"):
            return False, f"❌ {name} format invalid (should start with 'price_')"
        return True, f"✅ {name} is set (starts with 'price_...')"
    
    return True, f"✅ {name} is set"


def test_stripe_connection() -> tuple[bool, str]:
    """Test Stripe API connection"""
    if not settings.stripe_secret_key:
        return False, "❌ Cannot test connection: STRIPE_SECRET_KEY not set"
    
    try:
        stripe.api_key = settings.stripe_secret_key
        # Try to list customers (limit 1) - this tests the API connection
        customers = stripe.Customer.list(limit=1)
        return True, "✅ Stripe API connection successful"
    except stripe.error.AuthenticationError:
        return False, "❌ Stripe API authentication failed (invalid secret key)"
    except stripe.error.APIConnectionError:
        return False, "❌ Stripe API connection failed (network issue)"
    except Exception as e:
        return False, f"❌ Stripe API error: {str(e)}"


def check_price_ids() -> list[tuple[bool, str]]:
    """Check if price IDs are configured for all tiers"""
    results = []
    tiers = {
        "free": "STRIPE_PRICE_ID_FREE",
        "premium": "STRIPE_PRICE_ID_PREMIUM",
        "pro": "STRIPE_PRICE_ID_PRO",
        "pro+": "STRIPE_PRICE_ID_PRO_PLUS",
    }
    
    for tier, env_var in tiers.items():
        # Check both settings and env
        value = getattr(settings, env_var.lower(), None) or os.getenv(env_var)
        if value:
            if value.startswith("price_"):
                results.append((True, f"✅ {tier.upper()} tier: {env_var} is set"))
            else:
                results.append((False, f"❌ {tier.upper()} tier: {env_var} format invalid"))
        else:
            results.append((False, f"⚠️  {tier.upper()} tier: {env_var} not set (optional)"))
    
    return results


def main():
    """Main verification function"""
    print("=" * 60)
    print("Stripe Configuration Verification")
    print("=" * 60)
    print()
    
    all_checks_passed = True
    
    # Check API Keys
    print("📋 API Keys:")
    print("-" * 60)
    
    secret_check = check_env_var("STRIPE_SECRET_KEY", required=True)
    print(f"  {secret_check[1]}")
    if not secret_check[0]:
        all_checks_passed = False
    
    publishable_check = check_env_var("STRIPE_PUBLISHABLE_KEY", required=False)
    print(f"  {publishable_check[1]}")
    
    webhook_check = check_env_var("STRIPE_WEBHOOK_SECRET", required=True)
    print(f"  {webhook_check[1]}")
    if not webhook_check[0]:
        all_checks_passed = False
    
    print()
    
    # Test Stripe Connection
    print("🔌 Stripe API Connection:")
    print("-" * 60)
    connection_check = test_stripe_connection()
    print(f"  {connection_check[1]}")
    if not connection_check[0]:
        all_checks_passed = False
    
    print()
    
    # Check Price IDs
    print("💰 Subscription Price IDs:")
    print("-" * 60)
    price_checks = check_price_ids()
    for check in price_checks:
        print(f"  {check[1]}")
        if not check[0] and "⚠️" not in check[1]:  # Don't fail on optional warnings
            all_checks_passed = False
    
    print()
    
    # Summary
    print("=" * 60)
    if all_checks_passed:
        print("✅ All critical Stripe configuration checks passed!")
        print()
        print("Next steps:")
        print("  1. Test checkout session creation")
        print("  2. Test webhook handling with Stripe CLI")
        print("  3. Test end-to-end subscription flow")
    else:
        print("❌ Some Stripe configuration checks failed")
        print()
        print("Please fix the issues above before proceeding.")
        print("See STRIPE_SETUP.md for detailed setup instructions.")
        sys.exit(1)
    
    print("=" * 60)


if __name__ == "__main__":
    main()

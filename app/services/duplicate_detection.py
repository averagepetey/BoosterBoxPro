"""
Duplicate Detection Service
Detects duplicate listings and sales to prevent double-counting
"""

from typing import Dict, Any, List, Optional, Set, Tuple
from datetime import date


class DuplicateDetectionService:
    """Service for detecting duplicate listings and sales"""
    
    def __init__(self):
        pass
    
    def detect_listing_duplicates(
        self,
        new_listings: List[Dict[str, Any]],
        existing_listings: List[Dict[str, Any]]
    ) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]], List[Dict[str, Any]]]:
        """
        Detect duplicate listings and categorize them
        
        Args:
            new_listings: New listings from current screenshot
            existing_listings: Existing listings from previous data
        
        Returns:
            Tuple of (new_listings, updated_listings, duplicate_listings)
            - new_listings: Listings that are truly new
            - updated_listings: Listings where price changed (same seller+quantity+platform)
            - duplicate_listings: Exact duplicates (skip these)
        """
        new_listings_filtered = []
        updated_listings = []
        duplicate_listings = []
        
        # Create lookup set for existing listings
        existing_lookup = self._create_listing_lookup(existing_listings)
        
        for listing in new_listings:
            listing_key = self._get_listing_key(listing)
            
            if listing_key in existing_lookup:
                existing_listing = existing_lookup[listing_key]
                
                # Check if price changed
                if self._prices_differ(listing, existing_listing):
                    # Price changed - this is an UPDATE, not a new listing
                    updated_listings.append(listing)
                else:
                    # Exact duplicate - skip
                    duplicate_listings.append(listing)
            else:
                # New listing
                new_listings_filtered.append(listing)
        
        return new_listings_filtered, updated_listings, duplicate_listings
    
    def detect_sale_duplicates(
        self,
        new_sales: List[Dict[str, Any]],
        existing_sales: List[Dict[str, Any]]
    ) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
        """
        Detect duplicate sales
        
        Args:
            new_sales: New sales from current screenshot
            existing_sales: Existing sales from previous data
        
        Returns:
            Tuple of (new_sales, duplicate_sales)
            - new_sales: Sales that are new (not duplicates)
            - duplicate_sales: Exact duplicates (skip these)
        """
        new_sales_filtered = []
        duplicate_sales = []
        
        # Create lookup set for existing sales
        existing_lookup = self._create_sale_lookup(existing_sales)
        
        for sale in new_sales:
            sale_key = self._get_sale_key(sale)
            
            if sale_key in existing_lookup:
                # Exact duplicate - skip
                duplicate_sales.append(sale)
            else:
                # New sale
                new_sales_filtered.append(sale)
        
        return new_sales_filtered, duplicate_sales
    
    def _create_listing_lookup(self, listings: List[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
        """Create lookup dictionary for listings"""
        lookup = {}
        for listing in listings:
            key = self._get_listing_key(listing)
            lookup[key] = listing
        return lookup
    
    def _create_sale_lookup(self, sales: List[Dict[str, Any]]) -> Set[str]:
        """Create lookup set for sales"""
        return {self._get_sale_key(sale) for sale in sales}
    
    def _get_listing_key(self, listing: Dict[str, Any]) -> str:
        """
        Create unique key for listing duplicate detection
        Format: seller|quantity|platform|listing_id (if available)
        """
        seller = str(listing.get("seller", "")).strip()
        quantity = str(listing.get("quantity", "")).strip()
        platform = str(listing.get("platform", "")).strip().lower()
        listing_id = str(listing.get("listing_id", "")).strip()
        
        # If listing_id available, use it for more precise matching
        if listing_id:
            return f"{seller}|{quantity}|{platform}|{listing_id}"
        else:
            # Fallback to seller+quantity+platform
            return f"{seller}|{quantity}|{platform}"
    
    def _get_sale_key(self, sale: Dict[str, Any]) -> str:
        """
        Create unique key for sale duplicate detection
        Format: seller|price|quantity|date|platform|sale_id (if available)
        """
        seller = str(sale.get("seller", "")).strip()
        price = str(sale.get("price", "")).strip()
        quantity = str(sale.get("quantity", "")).strip()
        sale_date = str(sale.get("date", "")).strip()
        platform = str(sale.get("platform", "")).strip().lower()
        sale_id = str(sale.get("sale_id", "")).strip()
        
        # If sale_id available, use it for more precise matching
        if sale_id:
            return f"{seller}|{price}|{quantity}|{sale_date}|{platform}|{sale_id}"
        else:
            # Fallback to seller+price+quantity+date+platform
            return f"{seller}|{price}|{quantity}|{sale_date}|{platform}"
    
    def _prices_differ(self, listing1: Dict[str, Any], listing2: Dict[str, Any], tolerance: float = 0.01) -> bool:
        """Check if two listing prices differ (within tolerance)"""
        price1 = float(listing1.get("price", 0))
        price2 = float(listing2.get("price", 0))
        return abs(price1 - price2) > tolerance


# Global service instance
duplicate_detection_service = DuplicateDetectionService()

Detects duplicate listings and sales to prevent double-counting
"""

from typing import Dict, Any, List, Optional, Set, Tuple
from datetime import date


class DuplicateDetectionService:
    """Service for detecting duplicate listings and sales"""
    
    def __init__(self):
        pass
    
    def detect_listing_duplicates(
        self,
        new_listings: List[Dict[str, Any]],
        existing_listings: List[Dict[str, Any]]
    ) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]], List[Dict[str, Any]]]:
        """
        Detect duplicate listings and categorize them
        
        Args:
            new_listings: New listings from current screenshot
            existing_listings: Existing listings from previous data
        
        Returns:
            Tuple of (new_listings, updated_listings, duplicate_listings)
            - new_listings: Listings that are truly new
            - updated_listings: Listings where price changed (same seller+quantity+platform)
            - duplicate_listings: Exact duplicates (skip these)
        """
        new_listings_filtered = []
        updated_listings = []
        duplicate_listings = []
        
        # Create lookup set for existing listings
        existing_lookup = self._create_listing_lookup(existing_listings)
        
        for listing in new_listings:
            listing_key = self._get_listing_key(listing)
            
            if listing_key in existing_lookup:
                existing_listing = existing_lookup[listing_key]
                
                # Check if price changed
                if self._prices_differ(listing, existing_listing):
                    # Price changed - this is an UPDATE, not a new listing
                    updated_listings.append(listing)
                else:
                    # Exact duplicate - skip
                    duplicate_listings.append(listing)
            else:
                # New listing
                new_listings_filtered.append(listing)
        
        return new_listings_filtered, updated_listings, duplicate_listings
    
    def detect_sale_duplicates(
        self,
        new_sales: List[Dict[str, Any]],
        existing_sales: List[Dict[str, Any]]
    ) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
        """
        Detect duplicate sales
        
        Args:
            new_sales: New sales from current screenshot
            existing_sales: Existing sales from previous data
        
        Returns:
            Tuple of (new_sales, duplicate_sales)
            - new_sales: Sales that are new (not duplicates)
            - duplicate_sales: Exact duplicates (skip these)
        """
        new_sales_filtered = []
        duplicate_sales = []
        
        # Create lookup set for existing sales
        existing_lookup = self._create_sale_lookup(existing_sales)
        
        for sale in new_sales:
            sale_key = self._get_sale_key(sale)
            
            if sale_key in existing_lookup:
                # Exact duplicate - skip
                duplicate_sales.append(sale)
            else:
                # New sale
                new_sales_filtered.append(sale)
        
        return new_sales_filtered, duplicate_sales
    
    def _create_listing_lookup(self, listings: List[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
        """Create lookup dictionary for listings"""
        lookup = {}
        for listing in listings:
            key = self._get_listing_key(listing)
            lookup[key] = listing
        return lookup
    
    def _create_sale_lookup(self, sales: List[Dict[str, Any]]) -> Set[str]:
        """Create lookup set for sales"""
        return {self._get_sale_key(sale) for sale in sales}
    
    def _get_listing_key(self, listing: Dict[str, Any]) -> str:
        """
        Create unique key for listing duplicate detection
        Format: seller|quantity|platform|listing_id (if available)
        """
        seller = str(listing.get("seller", "")).strip()
        quantity = str(listing.get("quantity", "")).strip()
        platform = str(listing.get("platform", "")).strip().lower()
        listing_id = str(listing.get("listing_id", "")).strip()
        
        # If listing_id available, use it for more precise matching
        if listing_id:
            return f"{seller}|{quantity}|{platform}|{listing_id}"
        else:
            # Fallback to seller+quantity+platform
            return f"{seller}|{quantity}|{platform}"
    
    def _get_sale_key(self, sale: Dict[str, Any]) -> str:
        """
        Create unique key for sale duplicate detection
        Format: seller|price|quantity|date|platform|sale_id (if available)
        """
        seller = str(sale.get("seller", "")).strip()
        price = str(sale.get("price", "")).strip()
        quantity = str(sale.get("quantity", "")).strip()
        sale_date = str(sale.get("date", "")).strip()
        platform = str(sale.get("platform", "")).strip().lower()
        sale_id = str(sale.get("sale_id", "")).strip()
        
        # If sale_id available, use it for more precise matching
        if sale_id:
            return f"{seller}|{price}|{quantity}|{sale_date}|{platform}|{sale_id}"
        else:
            # Fallback to seller+price+quantity+date+platform
            return f"{seller}|{price}|{quantity}|{sale_date}|{platform}"
    
    def _prices_differ(self, listing1: Dict[str, Any], listing2: Dict[str, Any], tolerance: float = 0.01) -> bool:
        """Check if two listing prices differ (within tolerance)"""
        price1 = float(listing1.get("price", 0))
        price2 = float(listing2.get("price", 0))
        return abs(price1 - price2) > tolerance


# Global service instance
duplicate_detection_service = DuplicateDetectionService()

Detects duplicate listings and sales to prevent double-counting
"""

from typing import Dict, Any, List, Optional, Set, Tuple
from datetime import date


class DuplicateDetectionService:
    """Service for detecting duplicate listings and sales"""
    
    def __init__(self):
        pass
    
    def detect_listing_duplicates(
        self,
        new_listings: List[Dict[str, Any]],
        existing_listings: List[Dict[str, Any]]
    ) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]], List[Dict[str, Any]]]:
        """
        Detect duplicate listings and categorize them
        
        Args:
            new_listings: New listings from current screenshot
            existing_listings: Existing listings from previous data
        
        Returns:
            Tuple of (new_listings, updated_listings, duplicate_listings)
            - new_listings: Listings that are truly new
            - updated_listings: Listings where price changed (same seller+quantity+platform)
            - duplicate_listings: Exact duplicates (skip these)
        """
        new_listings_filtered = []
        updated_listings = []
        duplicate_listings = []
        
        # Create lookup set for existing listings
        existing_lookup = self._create_listing_lookup(existing_listings)
        
        for listing in new_listings:
            listing_key = self._get_listing_key(listing)
            
            if listing_key in existing_lookup:
                existing_listing = existing_lookup[listing_key]
                
                # Check if price changed
                if self._prices_differ(listing, existing_listing):
                    # Price changed - this is an UPDATE, not a new listing
                    updated_listings.append(listing)
                else:
                    # Exact duplicate - skip
                    duplicate_listings.append(listing)
            else:
                # New listing
                new_listings_filtered.append(listing)
        
        return new_listings_filtered, updated_listings, duplicate_listings
    
    def detect_sale_duplicates(
        self,
        new_sales: List[Dict[str, Any]],
        existing_sales: List[Dict[str, Any]]
    ) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
        """
        Detect duplicate sales
        
        Args:
            new_sales: New sales from current screenshot
            existing_sales: Existing sales from previous data
        
        Returns:
            Tuple of (new_sales, duplicate_sales)
            - new_sales: Sales that are new (not duplicates)
            - duplicate_sales: Exact duplicates (skip these)
        """
        new_sales_filtered = []
        duplicate_sales = []
        
        # Create lookup set for existing sales
        existing_lookup = self._create_sale_lookup(existing_sales)
        
        for sale in new_sales:
            sale_key = self._get_sale_key(sale)
            
            if sale_key in existing_lookup:
                # Exact duplicate - skip
                duplicate_sales.append(sale)
            else:
                # New sale
                new_sales_filtered.append(sale)
        
        return new_sales_filtered, duplicate_sales
    
    def _create_listing_lookup(self, listings: List[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
        """Create lookup dictionary for listings"""
        lookup = {}
        for listing in listings:
            key = self._get_listing_key(listing)
            lookup[key] = listing
        return lookup
    
    def _create_sale_lookup(self, sales: List[Dict[str, Any]]) -> Set[str]:
        """Create lookup set for sales"""
        return {self._get_sale_key(sale) for sale in sales}
    
    def _get_listing_key(self, listing: Dict[str, Any]) -> str:
        """
        Create unique key for listing duplicate detection
        Format: seller|quantity|platform|listing_id (if available)
        """
        seller = str(listing.get("seller", "")).strip()
        quantity = str(listing.get("quantity", "")).strip()
        platform = str(listing.get("platform", "")).strip().lower()
        listing_id = str(listing.get("listing_id", "")).strip()
        
        # If listing_id available, use it for more precise matching
        if listing_id:
            return f"{seller}|{quantity}|{platform}|{listing_id}"
        else:
            # Fallback to seller+quantity+platform
            return f"{seller}|{quantity}|{platform}"
    
    def _get_sale_key(self, sale: Dict[str, Any]) -> str:
        """
        Create unique key for sale duplicate detection
        Format: seller|price|quantity|date|platform|sale_id (if available)
        """
        seller = str(sale.get("seller", "")).strip()
        price = str(sale.get("price", "")).strip()
        quantity = str(sale.get("quantity", "")).strip()
        sale_date = str(sale.get("date", "")).strip()
        platform = str(sale.get("platform", "")).strip().lower()
        sale_id = str(sale.get("sale_id", "")).strip()
        
        # If sale_id available, use it for more precise matching
        if sale_id:
            return f"{seller}|{price}|{quantity}|{sale_date}|{platform}|{sale_id}"
        else:
            # Fallback to seller+price+quantity+date+platform
            return f"{seller}|{price}|{quantity}|{sale_date}|{platform}"
    
    def _prices_differ(self, listing1: Dict[str, Any], listing2: Dict[str, Any], tolerance: float = 0.01) -> bool:
        """Check if two listing prices differ (within tolerance)"""
        price1 = float(listing1.get("price", 0))
        price2 = float(listing2.get("price", 0))
        return abs(price1 - price2) > tolerance


# Global service instance
duplicate_detection_service = DuplicateDetectionService()

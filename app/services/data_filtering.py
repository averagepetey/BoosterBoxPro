"""
Data Filtering Service
Applies filtering rules to listings and sales data extracted from screenshots
"""

from typing import Dict, Any, List, Optional
from decimal import Decimal


class DataFilteringService:
    """Service for filtering listings and sales data"""
    
    def __init__(self):
        self.jp_keywords = ["JP", "Japanese", "japanese", "JPN", "jpn"]
        self.price_filter_threshold = 0.25  # 25% below floor price
    
    def filter_listings(
        self,
        listings: List[Dict[str, Any]],
        box_name: str,
        current_floor_price: Optional[float] = None,
        platform: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Filter listings based on all filtering rules
        
        Args:
            listings: List of listing dictionaries with:
                - price: float (price + shipping)
                - quantity: int
                - seller: str
                - title: str
                - platform: str ("ebay" or "tcgplayer")
            box_name: Name of the booster box (e.g., "OP-01")
            current_floor_price: Current floor price for price filtering
            platform: Platform filter (optional)
        
        Returns:
            Filtered list of listings
        """
        filtered = []
        
        for listing in listings:
            # Skip if listing is missing required fields
            if not listing.get("price") or not listing.get("quantity"):
                continue
            
            # Apply platform filter if specified
            if platform and listing.get("platform") != platform:
                continue
            
            # Apply JP filter
            if self._contains_jp(listing.get("title", "") + " " + listing.get("description", "")):
                continue
            
            # Apply eBay title matching (only for eBay)
            if listing.get("platform", "").lower() == "ebay":
                if not self._matches_box_name(listing.get("title", ""), box_name):
                    continue
            
            # Apply price filter (if floor price available)
            if current_floor_price:
                listing_price = float(listing.get("price", 0))
                threshold = current_floor_price * (1 - self.price_filter_threshold)
                if listing_price < threshold:
                    continue
            
            # Passed all filters
            filtered.append(listing)
        
        return filtered
    
    def filter_sales(
        self,
        sales: List[Dict[str, Any]],
        box_name: str,
        current_floor_price: Optional[float] = None,
        platform: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Filter sales based on all filtering rules
        
        Args:
            sales: List of sale dictionaries with:
                - price: float (price + shipping)
                - quantity: int
                - date: str (ISO date)
                - seller: str
                - title: str
                - platform: str ("ebay" or "tcgplayer")
            box_name: Name of the booster box (e.g., "OP-01")
            current_floor_price: Current floor price for price filtering
            platform: Platform filter (optional)
        
        Returns:
            Filtered list of sales
        """
        filtered = []
        
        for sale in sales:
            # Skip if sale is missing required fields
            if not sale.get("price") or not sale.get("quantity"):
                continue
            
            # Apply platform filter if specified
            if platform and sale.get("platform") != platform:
                continue
            
            # Apply JP filter
            if self._contains_jp(sale.get("title", "") + " " + sale.get("description", "")):
                continue
            
            # Apply eBay title matching (only for eBay)
            if sale.get("platform", "").lower() == "ebay":
                if not self._matches_box_name(sale.get("title", ""), box_name):
                    continue
            
            # Apply price filter (if floor price available)
            if current_floor_price:
                sale_price = float(sale.get("price", 0))
                threshold = current_floor_price * (1 - self.price_filter_threshold)
                if sale_price < threshold:
                    continue
            
            # Passed all filters
            filtered.append(sale)
        
        return filtered
    
    def _contains_jp(self, text: str) -> bool:
        """Check if text contains Japanese keywords"""
        if not text:
            return False
        text_upper = text.upper()
        return any(keyword in text_upper for keyword in self.jp_keywords)
    
    def _matches_box_name(self, title: str, box_name: str) -> bool:
        """
        Check if eBay listing/sale title matches the booster box name
        Uses best judgment to identify legitimate matches
        
        Args:
            title: Listing/sale title from eBay
            box_name: Booster box name (e.g., "OP-01", "One Piece - OP-01 Romance Dawn Booster Box")
        
        Returns:
            True if title appears to match the box, False otherwise
        """
        if not title or not box_name:
            return False
        
        title_upper = title.upper()
        box_upper = box_name.upper()
        
        # Extract set code from box name (e.g., "OP-01", "EB-01")
        import re
        set_code_match = re.search(r'(OP|EB|PRB)-\d+', box_upper)
        if not set_code_match:
            # If no set code, use full box name matching
            # Check if key parts of box name are in title
            key_words = [word for word in box_upper.split() if len(word) > 2]
            return any(word in title_upper for word in key_words)
        
        set_code = set_code_match.group(0)  # e.g., "OP-01"
        
        # Check if set code is in title
        if set_code in title_upper:
            # Additional check: should contain "booster box" or "box" to avoid card listings
            if "BOOSTER BOX" in title_upper or " BOX " in title_upper or title_upper.endswith(" BOX"):
                return True
            # If set code matches but no "box" keyword, be conservative and include
            # (some listings may not have "box" in title)
            return True
        
        return False


# Global service instance
data_filtering_service = DataFilteringService()


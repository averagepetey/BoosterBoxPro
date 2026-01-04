"""
Data Extraction Formatter
Converts AI-extracted data from screenshots into structured format for processing
"""

from typing import Dict, Any, List, Optional
from datetime import date, datetime
from decimal import Decimal


class DataExtractionFormatter:
    """Formats AI-extracted data into system-compatible structure"""
    
    def __init__(self):
        pass
    
    def format_extracted_data(
        self,
        raw_data: Dict[str, Any],
        box_name: str,
        entry_date: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Format AI-extracted data into structured format
        
        Args:
            raw_data: Dictionary with AI-extracted data, expected structure:
                {
                    "floor_price": float or None,
                    "floor_price_shipping": float or None,
                    "listings": [
                        {
                            "price": float,
                            "shipping": float,
                            "quantity": int,
                            "seller": str,
                            "title": str,
                            "platform": str,  # "ebay" or "tcgplayer"
                            "listing_id": str (optional)
                        }
                    ],
                    "sales": [
                        {
                            "price": float,
                            "shipping": float,
                            "quantity": int,
                            "date": str,  # ISO date
                            "seller": str,
                            "title": str,
                            "platform": str,  # "ebay" or "tcgplayer"
                            "sale_id": str (optional)
                        }
                    ]
                }
            box_name: Name of the booster box (e.g., "OP-01")
            entry_date: Date for this entry (ISO format, defaults to today)
        
        Returns:
            Formatted data dictionary ready for processing
        """
        if entry_date is None:
            entry_date = date.today().isoformat()
        
        formatted = {
            "date": entry_date,
            "box_name": box_name,
            "floor_price_usd": None,
            "listings": [],
            "sales": [],
            "price_ladder": [],  # For T₊ calculation
        }
        
        # Format floor price (price + shipping from TCGPlayer)
        floor_price = raw_data.get("floor_price")
        floor_shipping = raw_data.get("floor_price_shipping", 0)
        if floor_price is not None:
            formatted["floor_price_usd"] = float(floor_price) + float(floor_shipping)
        
        # Format listings
        listings = raw_data.get("listings", [])
        for listing in listings:
            formatted_listing = self._format_listing(listing)
            if formatted_listing:
                formatted["listings"].append(formatted_listing)
                # Add to price ladder for T₊ calculation
                formatted["price_ladder"].append({
                    "price": formatted_listing["price"],
                    "quantity": formatted_listing["quantity"]
                })
        
        # Format sales
        sales = raw_data.get("sales", [])
        for sale in sales:
            formatted_sale = self._format_sale(sale, entry_date)
            if formatted_sale:
                formatted["sales"].append(formatted_sale)
        
        return formatted
    
    def _format_listing(self, listing: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Format a single listing"""
        try:
            price = float(listing.get("price", 0))
            shipping = float(listing.get("shipping", 0))
            quantity = int(listing.get("quantity", 1))
            
            if price <= 0 or quantity <= 0:
                return None
            
            return {
                "price": price + shipping,  # Total price (price + shipping)
                "quantity": quantity,
                "seller": str(listing.get("seller", "")).strip(),
                "title": str(listing.get("title", "")).strip(),
                "platform": str(listing.get("platform", "")).strip().lower(),
                "listing_id": str(listing.get("listing_id", "")).strip(),
                "description": str(listing.get("description", "")).strip(),
            }
        except (ValueError, TypeError) as e:
            # Skip invalid listings
            return None
    
    def _format_sale(self, sale: Dict[str, Any], default_date: str) -> Optional[Dict[str, Any]]:
        """Format a single sale"""
        try:
            price = float(sale.get("price", 0))
            shipping = float(sale.get("shipping", 0))
            quantity = int(sale.get("quantity", 1))
            sale_date = sale.get("date", default_date)
            
            if price <= 0 or quantity <= 0:
                return None
            
            # Validate date format
            try:
                date.fromisoformat(sale_date)
            except ValueError:
                sale_date = default_date
            
            return {
                "price": price + shipping,  # Total price (price + shipping)
                "quantity": quantity,
                "date": sale_date,
                "seller": str(sale.get("seller", "")).strip(),
                "title": str(sale.get("title", "")).strip(),
                "platform": str(sale.get("platform", "")).strip().lower(),
                "sale_id": str(sale.get("sale_id", "")).strip(),
                "description": str(sale.get("description", "")).strip(),
            }
        except (ValueError, TypeError) as e:
            # Skip invalid sales
            return None
    
    def aggregate_sales_by_date(self, sales: List[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
        """
        Aggregate sales by date
        
        Args:
            sales: List of formatted sales
        
        Returns:
            Dictionary keyed by date with aggregated totals:
            {
                "2025-01-03": {
                    "volume_usd": float,
                    "quantity": int,
                    "count": int
                }
            }
        """
        aggregated = {}
        
        for sale in sales:
            sale_date = sale.get("date")
            if not sale_date:
                continue
            
            if sale_date not in aggregated:
                aggregated[sale_date] = {
                    "volume_usd": 0.0,
                    "quantity": 0,
                    "count": 0
                }
            
            aggregated[sale_date]["volume_usd"] += sale["price"] * sale["quantity"]
            aggregated[sale_date]["quantity"] += sale["quantity"]
            aggregated[sale_date]["count"] += 1
        
        return aggregated
    
    def build_price_ladder(self, listings: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Build price ladder from listings (for T₊ calculation)
        
        Args:
            listings: List of formatted listings
        
        Returns:
            Price ladder sorted by price (ascending)
        """
        ladder = []
        for listing in listings:
            ladder.append({
                "price": listing["price"],
                "quantity": listing["quantity"]
            })
        
        # Sort by price (ascending)
        ladder.sort(key=lambda x: x["price"])
        return ladder


# Global instance
data_extraction_formatter = DataExtractionFormatter()


"""
Chat-Based Data Entry System
Processes data sent via chat (text or screenshots), checks for duplicates, and updates the database/JSON files
"""

import json
import sys
import base64
from datetime import datetime, date
from typing import Dict, Any, Optional, List, Union
from pathlib import Path
import re

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.config import settings

# Import image processing service
try:
    from app.services.image_processing import image_processing_service
    IMAGE_PROCESSING_AVAILABLE = True
except ImportError:
    IMAGE_PROCESSING_AVAILABLE = False
    image_processing_service = None

# Import historical data manager and metrics calculator
try:
    from scripts.historical_data_manager import historical_data_manager
    from scripts.metrics_calculator import metrics_calculator
    HISTORICAL_DATA_AVAILABLE = True
except ImportError:
    HISTORICAL_DATA_AVAILABLE = False
    historical_data_manager = None
    metrics_calculator = None


class ChatDataEntry:
    """Handles data entry from chat with duplicate detection"""
    
    def __init__(self):
        self.data_file = Path(__file__).parent.parent / "data" / "leaderboard.json"
        self.mock_data_file = Path(__file__).parent.parent / "mock_data" / "leaderboard.json"
        
    def load_existing_data(self) -> Dict[str, Any]:
        """Load existing leaderboard data"""
        # Try data folder first, then mock_data
        if self.data_file.exists():
            with open(self.data_file, 'r') as f:
                return json.load(f)
        elif self.mock_data_file.exists():
            with open(self.mock_data_file, 'r') as f:
                return json.load(f)
        return {"data": []}
    
    def save_data(self, data: Dict[str, Any]) -> bool:
        """Save data to the data folder"""
        # Ensure data directory exists
        self.data_file.parent.mkdir(exist_ok=True)
        
        with open(self.data_file, 'w') as f:
            json.dump(data, f, indent=2)
        return True
    
    def find_box_by_name(self, product_name: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Find a box by product name (fuzzy matching)"""
        product_name_lower = product_name.lower()
        
        for box in data.get("data", []):
            box_name = box.get("product_name", "").lower()
            # Exact match
            if box_name == product_name_lower:
                return box
            # Partial match (contains)
            if product_name_lower in box_name or box_name in product_name_lower:
                return box
            # Match by set code (OP-01, OP-02, etc.)
            set_code_match = re.search(r'(OP|EB|PRB)-\d+', product_name, re.IGNORECASE)
            if set_code_match:
                set_code = set_code_match.group(0).upper()
                box_set_match = re.search(r'(OP|EB|PRB)-\d+', box.get("product_name", ""), re.IGNORECASE)
                if box_set_match and box_set_match.group(0).upper() == set_code:
                    return box
        return None
    
    def parse_data_from_text(self, text: str) -> Dict[str, Any]:
        """
        Parse data from natural language text
        Handles various formats like:
        - "OP-01: Floor $100, Volume $5000, Sales 10"
        - "One Piece OP-01: Floor Price: $100, Daily Volume: $5000"
        """
        data = {}
        
        # Extract product name/set code
        set_code_match = re.search(r'(OP|EB|PRB)-\d+', text, re.IGNORECASE)
        if set_code_match:
            data['set_code'] = set_code_match.group(0).upper()
        
        # Extract product name if mentioned
        product_name_match = re.search(r'(One Piece|Pokemon|Yu-Gi-Oh!?|Magic|MTG).*?(?:-|:|\n)', text, re.IGNORECASE)
        if product_name_match:
            data['product_name'] = product_name_match.group(0).strip(' :-')
        
        # Extract floor price
        floor_price_match = re.search(r'floor[:\s]*\$?([\d,]+\.?\d*)', text, re.IGNORECASE)
        if floor_price_match:
            data['floor_price_usd'] = float(floor_price_match.group(1).replace(',', ''))
        
        # Extract volume
        volume_match = re.search(r'(?:volume|vol)[:\s]*\$?([\d,]+\.?\d*)', text, re.IGNORECASE)
        if volume_match:
            data['daily_volume_usd'] = float(volume_match.group(1).replace(',', ''))
        
        # Extract sales/units sold
        sales_match = re.search(r'(?:sales|sold|units)[:\s]*(\d+)', text, re.IGNORECASE)
        if sales_match:
            data['units_sold_count'] = int(sales_match.group(1))
        
        # Extract listings
        listings_match = re.search(r'(?:listings|listed)[:\s]*(\d+)', text, re.IGNORECASE)
        if listings_match:
            data['active_listings_count'] = int(listings_match.group(1))
        
        # Extract market cap
        market_cap_match = re.search(r'(?:market\s*cap|mcap)[:\s]*\$?([\d,]+\.?\d*)', text, re.IGNORECASE)
        if market_cap_match:
            data['visible_market_cap_usd'] = float(market_cap_match.group(1).replace(',', ''))
        
        # Extract boxes added
        boxes_added_match = re.search(r'(?:boxes\s*added|added\s*today)[:\s]*(\d+)', text, re.IGNORECASE)
        if boxes_added_match:
            data['boxes_added_today'] = int(boxes_added_match.group(1))
        
        # Extract boxes sold per day (7-day average)
        boxes_sold_match = re.search(r'(?:sales|sold|boxes\s*sold)[:\s]*([\d.]+)', text, re.IGNORECASE)
        if boxes_sold_match:
            data['boxes_sold_per_day'] = float(boxes_sold_match.group(1))
        
        # Extract date (default to today)
        date_match = re.search(r'(\d{4}-\d{2}-\d{2})', text)
        if date_match:
            data['metric_date'] = date_match.group(1)
        else:
            data['metric_date'] = date.today().isoformat()
        
        return data
    
    def check_duplicate(self, box_id: str, metric_date: str, new_data: Dict[str, Any], existing_data: Dict[str, Any]) -> Dict[str, Any]:
        """Check if data is a duplicate"""
        # Find existing box data
        box = None
        for b in existing_data.get("data", []):
            if b.get("id") == box_id:
                box = b
                break
        
        if not box:
            return {
                "is_duplicate": False,
                "message": "Box not found in existing data. This is new data.",
                "differences": {}
            }
        
        # Check if metric_date matches
        if box.get("metric_date") != metric_date:
            return {
                "is_duplicate": False,
                "message": f"Different date. Existing: {box.get('metric_date')}, New: {metric_date}",
                "differences": {}
            }
        
        # Compare metrics
        existing_metrics = box.get("metrics", {})
        differences = {}
        is_duplicate = True
        
        comparison_fields = {
            "floor_price_usd": 0.01,
            "daily_volume_usd": 0.01,
            "units_sold_count": 0,
            "active_listings_count": 0,
            "visible_market_cap_usd": 0.01,
        }
        
        for field, tolerance in comparison_fields.items():
            new_value = new_data.get(field)
            existing_value = existing_metrics.get(field)
            
            if new_value is None and existing_value is None:
                continue
            
            if new_value is None or existing_value is None:
                differences[field] = {
                    "existing": existing_value,
                    "new": new_value,
                    "changed": True
                }
                is_duplicate = False
                continue
            
            if isinstance(new_value, (int, float)) and isinstance(existing_value, (int, float)):
                diff = abs(new_value - existing_value)
                if diff > tolerance:
                    differences[field] = {
                        "existing": existing_value,
                        "new": new_value,
                        "difference": diff,
                        "changed": True
                    }
                    is_duplicate = False
        
        if is_duplicate:
            message = "Data already exists and matches existing values. No update needed."
        else:
            changed_fields = list(differences.keys())
            message = f"Data exists but differs in: {', '.join(changed_fields)}"
        
        return {
            "is_duplicate": is_duplicate,
            "existing_data": existing_metrics,
            "differences": differences,
            "message": message
        }
    
    def update_box_data(self, box_id: str, metric_date: str, new_metrics: Dict[str, Any], existing_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update box data in the JSON file"""
        # Find and update the box
        updated = False
        for box in existing_data.get("data", []):
            if box.get("id") == box_id:
                # Update metrics
                if "metrics" not in box:
                    box["metrics"] = {}
                
                # Update each metric field
                for key, value in new_metrics.items():
                    if value is not None:
                        box["metrics"][key] = value
                
                # Update metric_date
                box["metric_date"] = metric_date
                updated = True
                break
        
        if not updated:
            return {
                "success": False,
                "message": f"Box with id {box_id} not found"
            }
        
        # Save updated data
        self.save_data(existing_data)
        
        return {
            "success": True,
            "message": "Data updated successfully",
            "action": "updated"
        }
    
    def process_chat_data(self, text: str, entry_date: Optional[str] = None) -> Dict[str, Any]:
        """
        Main entry point for processing data from chat
        Returns a result dict with success status and message
        
        Args:
            text: Text data to parse
            entry_date: Optional ISO date string (YYYY-MM-DD) for the entry. If None, uses date from text or today.
        """
        try:
            # Load existing data
            existing_data = self.load_existing_data()
            
            # Parse data from text
            parsed_data = self.parse_data_from_text(text)
            
            if not parsed_data.get("set_code") and not parsed_data.get("product_name"):
                return {
                    "success": False,
                    "message": "Could not identify product name or set code from the data. Please include the set code (e.g., OP-01) or product name."
                }
            
            # Find the box
            box = None
            if parsed_data.get("set_code"):
                # Try to find by set code
                for b in existing_data.get("data", []):
                    set_code_match = re.search(r'(OP|EB|PRB)-\d+', b.get("product_name", ""), re.IGNORECASE)
                    if set_code_match and set_code_match.group(0).upper() == parsed_data["set_code"]:
                        box = b
                        break
            
            if not box and parsed_data.get("product_name"):
                box = self.find_box_by_name(parsed_data["product_name"], existing_data)
            
            if not box:
                return {
                    "success": False,
                    "message": f"Could not find box matching '{parsed_data.get('set_code') or parsed_data.get('product_name')}'. Please check the product name or set code."
                }
            
            box_id = box.get("id")
            # Use provided date, date from parsed data, or today
            metric_date = entry_date or parsed_data.get("metric_date") or date.today().isoformat()
            
            # Prepare metrics dict
            new_metrics = {}
            metric_mapping = {
                "floor_price_usd": "floor_price_usd",
                "daily_volume_usd": "daily_volume_usd",
                "units_sold_count": "units_sold_count",
                "active_listings_count": "active_listings_count",
                "visible_market_cap_usd": "visible_market_cap_usd",
                "boxes_added_today": "boxes_added_today",
            }
            
            for key, value in parsed_data.items():
                if key in metric_mapping:
                    new_metrics[metric_mapping[key]] = value
            
            # Check for duplicates
            duplicate_check = self.check_duplicate(box_id, metric_date, new_metrics, existing_data)
            
            if duplicate_check["is_duplicate"]:
                return {
                    "success": False,
                    "message": duplicate_check["message"],
                    "is_duplicate": True,
                    "existing_data": duplicate_check["existing_data"]
                }
            
            # Update the data
            result = self.update_box_data(box_id, metric_date, new_metrics, existing_data)
            
            if result["success"]:
                result["duplicate_check"] = duplicate_check
                result["box_name"] = box.get("product_name")
            
            return result
            
        except Exception as e:
            return {
                "success": False,
                "message": f"Error processing data: {str(e)}",
                "error": str(e)
            }


def process_screenshot_entry(image_bytes: bytes, use_ai: bool = True, data_type: str = "auto", entry_date: Optional[str] = None) -> Dict[str, Any]:
    """
    Process data entry from a screenshot image
    
    Args:
        image_bytes: Raw image bytes from the screenshot
        use_ai: Whether to use AI extraction (default: True)
        data_type: Type of screenshot - "sales", "listings", "combined", or "auto" (default: "auto")
        entry_date: ISO date string (YYYY-MM-DD) for the data. If None, uses today's date.
    
    Returns:
        Result dict with success status and extracted/updated data
    """
    if not IMAGE_PROCESSING_AVAILABLE or not image_processing_service:
        return {
            "success": False,
            "message": "Image processing service not available. Please install required dependencies."
        }
    
    try:
        # Process the screenshot to extract data
        extraction_result = image_processing_service.process_screenshot(image_bytes, use_ai=use_ai)
        
        if not extraction_result.get("success"):
            return {
                "success": False,
                "message": f"Failed to extract data from screenshot: {', '.join(extraction_result.get('errors', ['Unknown error']))}",
                "extraction_result": extraction_result
            }
        
        extracted_data = extraction_result.get("extracted_data", {})
        
        if not extracted_data.get("product_name"):
            return {
                "success": False,
                "message": "Could not identify product name from screenshot. Please ensure the product name or set code (e.g., OP-01) is visible in the image.",
                "extraction_result": extraction_result
            }
        
        # Find the box
        processor = ChatDataEntry()
        existing_data = processor.load_existing_data()
        
        # Find box by product name or set code
        box = None
        product_name = extracted_data.get("product_name", "")
        set_code_match = re.search(r'(OP|EB|PRB)-\d+', product_name, re.IGNORECASE)
        
        if set_code_match:
            set_code = set_code_match.group(0).upper()
            for b in existing_data.get("data", []):
                box_set_match = re.search(r'(OP|EB|PRB)-\d+', b.get("product_name", ""), re.IGNORECASE)
                if box_set_match and box_set_match.group(0).upper() == set_code:
                    box = b
                    break
        
        if not box:
            box = processor.find_box_by_name(product_name, existing_data)
        
        if not box:
            return {
                "success": False,
                "message": f"Could not find box matching '{product_name}'. Please check the product name or set code.",
                "extraction_result": extraction_result
            }
        
        box_id = box.get("id")
        # Use provided date or default to today
        if entry_date:
            # Validate date format
            try:
                datetime.strptime(entry_date, "%Y-%m-%d")
            except ValueError:
                return {
                    "success": False,
                    "message": f"Invalid date format: {entry_date}. Please use YYYY-MM-DD format.",
                    "extraction_result": extraction_result
                }
        else:
            entry_date = date.today().isoformat()
        
        # Auto-detect data type if not specified
        if data_type == "auto":
            # Check what data is present to determine type
            has_sales = extracted_data.get("boxes_sold_today") is not None or extracted_data.get("daily_volume_usd") is not None
            has_listings = extracted_data.get("active_listings_count") is not None or extracted_data.get("floor_price_usd") is not None
            
            if has_sales and has_listings:
                data_type = "combined"
            elif has_sales:
                data_type = "sales"
            elif has_listings:
                data_type = "listings"
            else:
                data_type = "combined"  # Default
        
        # Check if entry already exists for this date and type
        comparison = None
        if HISTORICAL_DATA_AVAILABLE and historical_data_manager:
            existing_entry = historical_data_manager.entry_exists(box_id, entry_date, data_type)
            
            if existing_entry:
                # Get existing entry to compare
                existing_entries = historical_data_manager.get_box_history(box_id)
                day_entries = [e for e in existing_entries if e.get("date") == entry_date and e.get("data_type") == data_type]
                
                if day_entries:
                    # Check if this is truly duplicate or has new information
                    comparison = metrics_calculator.identify_new_data(day_entries, extracted_data)
                    
                    if not comparison.get("needs_update"):
                        return {
                            "success": False,
                            "message": f"Duplicate data for {data_type} on {entry_date}. {comparison.get('update_reason')}",
                            "is_duplicate": True,
                            "comparison": comparison
                        }
        
        # Store historical entry
        entry_data = {
            "date": entry_date,
            "source": "screenshot",
            "data_type": data_type,
            "floor_price_usd": extracted_data.get("floor_price_usd"),
            "active_listings_count": extracted_data.get("active_listings_count"),
            "boxes_sold_today": extracted_data.get("boxes_sold_today"),
            "daily_volume_usd": extracted_data.get("daily_volume_usd"),
            "boxes_added_today": extracted_data.get("boxes_added_today"),
            "visible_market_cap_usd": extracted_data.get("visible_market_cap_usd"),
            "estimated_total_supply": extracted_data.get("estimated_total_supply"),
            "screenshot_metadata": {
                "confidence_scores": extraction_result.get("confidence_scores", {}),
                "extraction_timestamp": datetime.now().isoformat()
            }
        }
        
        if HISTORICAL_DATA_AVAILABLE and historical_data_manager:
            historical_data_manager.add_entry(box_id, entry_data)
        
        # Get all historical entries for this box
        if HISTORICAL_DATA_AVAILABLE and historical_data_manager:
            all_history = historical_data_manager.get_box_history(box_id)
            
            # Merge entries for today if we have multiple
            merged_today = historical_data_manager.merge_entries(box_id, entry_date)
            
            # Calculate metrics from historical data
            if metrics_calculator:
                calculated_metrics = metrics_calculator.calculate_daily_metrics(all_history)
                
                # Update the box with calculated metrics
                processor.update_box_data(box_id, entry_date, calculated_metrics, existing_data)
                
                return {
                    "success": True,
                    "message": f"Data processed and metrics calculated for {box.get('product_name')}",
                    "box_name": box.get("product_name"),
                    "data_type": data_type,
                    "entry_date": entry_date,
                    "extracted_data": extracted_data,
                    "calculated_metrics": calculated_metrics,
                    "comparison": comparison,
                    "extraction_result": extraction_result
                }
        
        # Fallback: process as before if historical data not available
        text_parts = []
        if extracted_data.get("product_name"):
            text_parts.append(extracted_data["product_name"])
        if extracted_data.get("floor_price_usd"):
            text_parts.append(f"Floor ${extracted_data['floor_price_usd']}")
        if extracted_data.get("daily_volume_usd"):
            text_parts.append(f"Volume ${extracted_data['daily_volume_usd']}")
        if extracted_data.get("boxes_sold_today"):
            text_parts.append(f"Sales {extracted_data['boxes_sold_today']}")
        if extracted_data.get("active_listings_count") is not None:
            text_parts.append(f"Listings {extracted_data['active_listings_count']}")
        
        text_data = ", ".join(text_parts)
        result = processor.process_chat_data(text_data)
        result["extraction_result"] = extraction_result
        result["confidence_scores"] = extraction_result.get("confidence_scores", {})
        
        return result
        
    except Exception as e:
        return {
            "success": False,
            "message": f"Error processing screenshot: {str(e)}",
            "error": str(e)
        }


def process_data_entry(text_or_image: Union[str, bytes], is_image: bool = False, use_ai: bool = True) -> Dict[str, Any]:
    """
    Public function to process data entry from chat
    Can handle both text and image inputs
    
    Args:
        text_or_image: Either text string or image bytes
        is_image: True if input is image bytes, False if text
        use_ai: Whether to use AI extraction for images (default: True)
    
    Returns:
        Result dict with success status and message
    """
    if is_image:
        if isinstance(text_or_image, str):
            # If it's a base64 string, decode it
            try:
                image_bytes = base64.b64decode(text_or_image)
            except:
                return {
                    "success": False,
                    "message": "Invalid image format. Expected bytes or base64 string."
                }
        else:
            image_bytes = text_or_image
        return process_screenshot_entry(image_bytes, use_ai=use_ai, entry_date=entry_date)
    else:
        processor = ChatDataEntry()
        return processor.process_chat_data(text_or_image)


if __name__ == "__main__":
    # For testing
    if len(sys.argv) > 1:
        test_text = " ".join(sys.argv[1:])
        result = process_data_entry(test_text, is_image=False)
        print(json.dumps(result, indent=2))
    else:
        print("Usage: python chat_data_entry.py 'OP-01: Floor $100, Volume $5000, Sales 10'")
        print("Or: python chat_data_entry.py <image_file_path> --image")


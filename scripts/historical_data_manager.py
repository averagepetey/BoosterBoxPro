"""
Historical Data Manager
Manages historical data entries for each box, tracking what has been entered and when
"""

import json
from datetime import date, datetime
from typing import Dict, Any, List, Optional
from pathlib import Path


class HistoricalDataManager:
    """Manages historical data entries for tracking and duplicate detection"""
    
    def __init__(self):
        self.historical_file = Path(__file__).parent.parent / "data" / "historical_entries.json"
        self.historical_file.parent.mkdir(exist_ok=True)
    
    def load_historical_data(self) -> Dict[str, List[Dict[str, Any]]]:
        """Load all historical data entries"""
        if not self.historical_file.exists():
            return {}
        
        try:
            with open(self.historical_file, 'r') as f:
                return json.load(f)
        except:
            return {}
    
    def save_historical_data(self, data: Dict[str, List[Dict[str, Any]]]) -> bool:
        """Save historical data"""
        try:
            with open(self.historical_file, 'w') as f:
                json.dump(data, f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving historical data: {e}")
            return False
    
    def get_box_history(self, box_id: str) -> List[Dict[str, Any]]:
        """Get historical entries for a specific box"""
        all_data = self.load_historical_data()
        return all_data.get(box_id, [])
    
    def add_entry(self, box_id: str, entry_data: Dict[str, Any]) -> bool:
        """
        Add a new historical entry
        
        Args:
            box_id: Box identifier
            entry_data: Dictionary with:
                - date: ISO date string
                - source: "screenshot" or "manual"
                - data_type: "sales", "listings", or "combined"
                - floor_price_usd: float or None
                - active_listings_count: int or None
                - boxes_sold_today: int or None
                - daily_volume_usd: float or None
                - boxes_added_today: int or None
                - visible_market_cap_usd: float or None
                - estimated_total_supply: int or None
                - price_ladder: List of {price, quantity} dicts for T₊ calculation (optional)
                - raw_listings: List of individual listings (optional)
                - raw_sales: List of individual sales (optional)
                - screenshot_metadata: Dict with extraction info (optional)
        """
        all_data = self.load_historical_data()
        
        if box_id not in all_data:
            all_data[box_id] = []
        
        # Ensure date is set
        if "date" not in entry_data:
            entry_data["date"] = date.today().isoformat()
        
        # Add timestamp
        entry_data["timestamp"] = datetime.now().isoformat()
        
        # Add entry
        all_data[box_id].append(entry_data)
        
        # Sort by date
        all_data[box_id].sort(key=lambda x: x.get("date", ""))
        
        return self.save_historical_data(all_data)
    
    def entry_exists(self, box_id: str, entry_date: str, data_type: Optional[str] = None) -> bool:
        """Check if an entry exists for a box and date"""
        history = self.get_box_history(box_id)
        
        for entry in history:
            if entry.get("date") == entry_date:
                if data_type is None or entry.get("data_type") == data_type:
                    return True
        
        return False
    
    def get_latest_entry(self, box_id: str, data_type: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Get the most recent entry for a box"""
        history = self.get_box_history(box_id)
        
        if not history:
            return None
        
        # Filter by data_type if specified
        if data_type:
            history = [e for e in history if e.get("data_type") == data_type]
        
        if not history:
            return None
        
        # Sort by date and return latest
        sorted_history = sorted(history, key=lambda x: x.get("date", ""), reverse=True)
        return sorted_history[0]
    
    def merge_entries(self, box_id: str, date_str: str) -> Dict[str, Any]:
        """
        Merge all entries for a box on a specific date into a single combined entry
        
        This is useful when you have separate sales and listings screenshots for the same day
        """
        history = self.get_box_history(box_id)
        day_entries = [e for e in history if e.get("date") == date_str]
        
        if not day_entries:
            return {}
        
        # Start with the most complete entry
        merged = max(day_entries, key=lambda x: sum(1 for v in x.values() if v is not None))
        merged = merged.copy()
        
        # Merge in data from other entries
        for entry in day_entries:
            for key, value in entry.items():
                if value is not None and (merged.get(key) is None or key in ["raw_sales_data", "screenshot_metadata"]):
                    if key == "raw_sales_data":
                        # Merge sales data lists
                        if "raw_sales_data" not in merged:
                            merged["raw_sales_data"] = []
                        merged["raw_sales_data"].extend(value)
                    elif key == "screenshot_metadata":
                        # Merge metadata
                        if "screenshot_metadata" not in merged:
                            merged["screenshot_metadata"] = []
                        if isinstance(value, list):
                            merged["screenshot_metadata"].extend(value)
                        else:
                            merged["screenshot_metadata"].append(value)
                    else:
                        merged[key] = value
        
        # Mark as combined
        merged["data_type"] = "combined"
        merged["merged_from"] = len(day_entries)
        
        return merged


# Global instance
historical_data_manager = HistoricalDataManager()



Manages historical data entries for each box, tracking what has been entered and when
"""

import json
from datetime import date, datetime
from typing import Dict, Any, List, Optional
from pathlib import Path


class HistoricalDataManager:
    """Manages historical data entries for tracking and duplicate detection"""
    
    def __init__(self):
        self.historical_file = Path(__file__).parent.parent / "data" / "historical_entries.json"
        self.historical_file.parent.mkdir(exist_ok=True)
    
    def load_historical_data(self) -> Dict[str, List[Dict[str, Any]]]:
        """Load all historical data entries"""
        if not self.historical_file.exists():
            return {}
        
        try:
            with open(self.historical_file, 'r') as f:
                return json.load(f)
        except:
            return {}
    
    def save_historical_data(self, data: Dict[str, List[Dict[str, Any]]]) -> bool:
        """Save historical data"""
        try:
            with open(self.historical_file, 'w') as f:
                json.dump(data, f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving historical data: {e}")
            return False
    
    def get_box_history(self, box_id: str) -> List[Dict[str, Any]]:
        """Get historical entries for a specific box"""
        all_data = self.load_historical_data()
        return all_data.get(box_id, [])
    
    def add_entry(self, box_id: str, entry_data: Dict[str, Any]) -> bool:
        """
        Add a new historical entry
        
        Args:
            box_id: Box identifier
            entry_data: Dictionary with:
                - date: ISO date string
                - source: "screenshot" or "manual"
                - data_type: "sales", "listings", or "combined"
                - floor_price_usd: float or None
                - active_listings_count: int or None
                - boxes_sold_today: int or None
                - daily_volume_usd: float or None
                - boxes_added_today: int or None
                - visible_market_cap_usd: float or None
                - estimated_total_supply: int or None
                - price_ladder: List of {price, quantity} dicts for T₊ calculation (optional)
                - raw_listings: List of individual listings (optional)
                - raw_sales: List of individual sales (optional)
                - screenshot_metadata: Dict with extraction info (optional)
        """
        all_data = self.load_historical_data()
        
        if box_id not in all_data:
            all_data[box_id] = []
        
        # Ensure date is set
        if "date" not in entry_data:
            entry_data["date"] = date.today().isoformat()
        
        # Add timestamp
        entry_data["timestamp"] = datetime.now().isoformat()
        
        # Add entry
        all_data[box_id].append(entry_data)
        
        # Sort by date
        all_data[box_id].sort(key=lambda x: x.get("date", ""))
        
        return self.save_historical_data(all_data)
    
    def entry_exists(self, box_id: str, entry_date: str, data_type: Optional[str] = None) -> bool:
        """Check if an entry exists for a box and date"""
        history = self.get_box_history(box_id)
        
        for entry in history:
            if entry.get("date") == entry_date:
                if data_type is None or entry.get("data_type") == data_type:
                    return True
        
        return False
    
    def get_latest_entry(self, box_id: str, data_type: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Get the most recent entry for a box"""
        history = self.get_box_history(box_id)
        
        if not history:
            return None
        
        # Filter by data_type if specified
        if data_type:
            history = [e for e in history if e.get("data_type") == data_type]
        
        if not history:
            return None
        
        # Sort by date and return latest
        sorted_history = sorted(history, key=lambda x: x.get("date", ""), reverse=True)
        return sorted_history[0]
    
    def merge_entries(self, box_id: str, date_str: str) -> Dict[str, Any]:
        """
        Merge all entries for a box on a specific date into a single combined entry
        
        This is useful when you have separate sales and listings screenshots for the same day
        """
        history = self.get_box_history(box_id)
        day_entries = [e for e in history if e.get("date") == date_str]
        
        if not day_entries:
            return {}
        
        # Start with the most complete entry
        merged = max(day_entries, key=lambda x: sum(1 for v in x.values() if v is not None))
        merged = merged.copy()
        
        # Merge in data from other entries
        for entry in day_entries:
            for key, value in entry.items():
                if value is not None and (merged.get(key) is None or key in ["raw_sales_data", "screenshot_metadata"]):
                    if key == "raw_sales_data":
                        # Merge sales data lists
                        if "raw_sales_data" not in merged:
                            merged["raw_sales_data"] = []
                        merged["raw_sales_data"].extend(value)
                    elif key == "screenshot_metadata":
                        # Merge metadata
                        if "screenshot_metadata" not in merged:
                            merged["screenshot_metadata"] = []
                        if isinstance(value, list):
                            merged["screenshot_metadata"].extend(value)
                        else:
                            merged["screenshot_metadata"].append(value)
                    else:
                        merged[key] = value
        
        # Mark as combined
        merged["data_type"] = "combined"
        merged["merged_from"] = len(day_entries)
        
        return merged


# Global instance
historical_data_manager = HistoricalDataManager()



Manages historical data entries for each box, tracking what has been entered and when
"""

import json
from datetime import date, datetime
from typing import Dict, Any, List, Optional
from pathlib import Path


class HistoricalDataManager:
    """Manages historical data entries for tracking and duplicate detection"""
    
    def __init__(self):
        self.historical_file = Path(__file__).parent.parent / "data" / "historical_entries.json"
        self.historical_file.parent.mkdir(exist_ok=True)
    
    def load_historical_data(self) -> Dict[str, List[Dict[str, Any]]]:
        """Load all historical data entries"""
        if not self.historical_file.exists():
            return {}
        
        try:
            with open(self.historical_file, 'r') as f:
                return json.load(f)
        except:
            return {}
    
    def save_historical_data(self, data: Dict[str, List[Dict[str, Any]]]) -> bool:
        """Save historical data"""
        try:
            with open(self.historical_file, 'w') as f:
                json.dump(data, f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving historical data: {e}")
            return False
    
    def get_box_history(self, box_id: str) -> List[Dict[str, Any]]:
        """Get historical entries for a specific box"""
        all_data = self.load_historical_data()
        return all_data.get(box_id, [])
    
    def add_entry(self, box_id: str, entry_data: Dict[str, Any]) -> bool:
        """
        Add a new historical entry
        
        Args:
            box_id: Box identifier
            entry_data: Dictionary with:
                - date: ISO date string
                - source: "screenshot" or "manual"
                - data_type: "sales", "listings", or "combined"
                - floor_price_usd: float or None
                - active_listings_count: int or None
                - boxes_sold_today: int or None
                - daily_volume_usd: float or None
                - boxes_added_today: int or None
                - visible_market_cap_usd: float or None
                - estimated_total_supply: int or None
                - price_ladder: List of {price, quantity} dicts for T₊ calculation (optional)
                - raw_listings: List of individual listings (optional)
                - raw_sales: List of individual sales (optional)
                - screenshot_metadata: Dict with extraction info (optional)
        """
        all_data = self.load_historical_data()
        
        if box_id not in all_data:
            all_data[box_id] = []
        
        # Ensure date is set
        if "date" not in entry_data:
            entry_data["date"] = date.today().isoformat()
        
        # Add timestamp
        entry_data["timestamp"] = datetime.now().isoformat()
        
        # Add entry
        all_data[box_id].append(entry_data)
        
        # Sort by date
        all_data[box_id].sort(key=lambda x: x.get("date", ""))
        
        return self.save_historical_data(all_data)
    
    def entry_exists(self, box_id: str, entry_date: str, data_type: Optional[str] = None) -> bool:
        """Check if an entry exists for a box and date"""
        history = self.get_box_history(box_id)
        
        for entry in history:
            if entry.get("date") == entry_date:
                if data_type is None or entry.get("data_type") == data_type:
                    return True
        
        return False
    
    def get_latest_entry(self, box_id: str, data_type: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Get the most recent entry for a box"""
        history = self.get_box_history(box_id)
        
        if not history:
            return None
        
        # Filter by data_type if specified
        if data_type:
            history = [e for e in history if e.get("data_type") == data_type]
        
        if not history:
            return None
        
        # Sort by date and return latest
        sorted_history = sorted(history, key=lambda x: x.get("date", ""), reverse=True)
        return sorted_history[0]
    
    def merge_entries(self, box_id: str, date_str: str) -> Dict[str, Any]:
        """
        Merge all entries for a box on a specific date into a single combined entry
        
        This is useful when you have separate sales and listings screenshots for the same day
        """
        history = self.get_box_history(box_id)
        day_entries = [e for e in history if e.get("date") == date_str]
        
        if not day_entries:
            return {}
        
        # Start with the most complete entry
        merged = max(day_entries, key=lambda x: sum(1 for v in x.values() if v is not None))
        merged = merged.copy()
        
        # Merge in data from other entries
        for entry in day_entries:
            for key, value in entry.items():
                if value is not None and (merged.get(key) is None or key in ["raw_sales_data", "screenshot_metadata"]):
                    if key == "raw_sales_data":
                        # Merge sales data lists
                        if "raw_sales_data" not in merged:
                            merged["raw_sales_data"] = []
                        merged["raw_sales_data"].extend(value)
                    elif key == "screenshot_metadata":
                        # Merge metadata
                        if "screenshot_metadata" not in merged:
                            merged["screenshot_metadata"] = []
                        if isinstance(value, list):
                            merged["screenshot_metadata"].extend(value)
                        else:
                            merged["screenshot_metadata"].append(value)
                    else:
                        merged[key] = value
        
        # Mark as combined
        merged["data_type"] = "combined"
        merged["merged_from"] = len(day_entries)
        
        return merged


# Global instance
historical_data_manager = HistoricalDataManager()



Manages historical data entries for each box, tracking what has been entered and when
"""

import json
from datetime import date, datetime
from typing import Dict, Any, List, Optional
from pathlib import Path


class HistoricalDataManager:
    """Manages historical data entries for tracking and duplicate detection"""
    
    def __init__(self):
        self.historical_file = Path(__file__).parent.parent / "data" / "historical_entries.json"
        self.historical_file.parent.mkdir(exist_ok=True)
    
    def load_historical_data(self) -> Dict[str, List[Dict[str, Any]]]:
        """Load all historical data entries"""
        if not self.historical_file.exists():
            return {}
        
        try:
            with open(self.historical_file, 'r') as f:
                return json.load(f)
        except:
            return {}
    
    def save_historical_data(self, data: Dict[str, List[Dict[str, Any]]]) -> bool:
        """Save historical data"""
        try:
            with open(self.historical_file, 'w') as f:
                json.dump(data, f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving historical data: {e}")
            return False
    
    def get_box_history(self, box_id: str) -> List[Dict[str, Any]]:
        """Get historical entries for a specific box"""
        all_data = self.load_historical_data()
        return all_data.get(box_id, [])
    
    def add_entry(self, box_id: str, entry_data: Dict[str, Any]) -> bool:
        """
        Add a new historical entry
        
        Args:
            box_id: Box identifier
            entry_data: Dictionary with:
                - date: ISO date string
                - source: "screenshot" or "manual"
                - data_type: "sales", "listings", or "combined"
                - floor_price_usd: float or None
                - active_listings_count: int or None
                - boxes_sold_today: int or None
                - daily_volume_usd: float or None
                - boxes_added_today: int or None
                - visible_market_cap_usd: float or None
                - estimated_total_supply: int or None
                - price_ladder: List of {price, quantity} dicts for T₊ calculation (optional)
                - raw_listings: List of individual listings (optional)
                - raw_sales: List of individual sales (optional)
                - screenshot_metadata: Dict with extraction info (optional)
        """
        all_data = self.load_historical_data()
        
        if box_id not in all_data:
            all_data[box_id] = []
        
        # Ensure date is set
        if "date" not in entry_data:
            entry_data["date"] = date.today().isoformat()
        
        # Add timestamp
        entry_data["timestamp"] = datetime.now().isoformat()
        
        # Add entry
        all_data[box_id].append(entry_data)
        
        # Sort by date
        all_data[box_id].sort(key=lambda x: x.get("date", ""))
        
        return self.save_historical_data(all_data)
    
    def entry_exists(self, box_id: str, entry_date: str, data_type: Optional[str] = None) -> bool:
        """Check if an entry exists for a box and date"""
        history = self.get_box_history(box_id)
        
        for entry in history:
            if entry.get("date") == entry_date:
                if data_type is None or entry.get("data_type") == data_type:
                    return True
        
        return False
    
    def get_latest_entry(self, box_id: str, data_type: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Get the most recent entry for a box"""
        history = self.get_box_history(box_id)
        
        if not history:
            return None
        
        # Filter by data_type if specified
        if data_type:
            history = [e for e in history if e.get("data_type") == data_type]
        
        if not history:
            return None
        
        # Sort by date and return latest
        sorted_history = sorted(history, key=lambda x: x.get("date", ""), reverse=True)
        return sorted_history[0]
    
    def merge_entries(self, box_id: str, date_str: str) -> Dict[str, Any]:
        """
        Merge all entries for a box on a specific date into a single combined entry
        
        This is useful when you have separate sales and listings screenshots for the same day
        """
        history = self.get_box_history(box_id)
        day_entries = [e for e in history if e.get("date") == date_str]
        
        if not day_entries:
            return {}
        
        # Start with the most complete entry
        merged = max(day_entries, key=lambda x: sum(1 for v in x.values() if v is not None))
        merged = merged.copy()
        
        # Merge in data from other entries
        for entry in day_entries:
            for key, value in entry.items():
                if value is not None and (merged.get(key) is None or key in ["raw_sales_data", "screenshot_metadata"]):
                    if key == "raw_sales_data":
                        # Merge sales data lists
                        if "raw_sales_data" not in merged:
                            merged["raw_sales_data"] = []
                        merged["raw_sales_data"].extend(value)
                    elif key == "screenshot_metadata":
                        # Merge metadata
                        if "screenshot_metadata" not in merged:
                            merged["screenshot_metadata"] = []
                        if isinstance(value, list):
                            merged["screenshot_metadata"].extend(value)
                        else:
                            merged["screenshot_metadata"].append(value)
                    else:
                        merged[key] = value
        
        # Mark as combined
        merged["data_type"] = "combined"
        merged["merged_from"] = len(day_entries)
        
        return merged


# Global instance
historical_data_manager = HistoricalDataManager()



Manages historical data entries for each box, tracking what has been entered and when
"""

import json
from datetime import date, datetime
from typing import Dict, Any, List, Optional
from pathlib import Path


class HistoricalDataManager:
    """Manages historical data entries for tracking and duplicate detection"""
    
    def __init__(self):
        self.historical_file = Path(__file__).parent.parent / "data" / "historical_entries.json"
        self.historical_file.parent.mkdir(exist_ok=True)
    
    def load_historical_data(self) -> Dict[str, List[Dict[str, Any]]]:
        """Load all historical data entries"""
        if not self.historical_file.exists():
            return {}
        
        try:
            with open(self.historical_file, 'r') as f:
                return json.load(f)
        except:
            return {}
    
    def save_historical_data(self, data: Dict[str, List[Dict[str, Any]]]) -> bool:
        """Save historical data"""
        try:
            with open(self.historical_file, 'w') as f:
                json.dump(data, f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving historical data: {e}")
            return False
    
    def get_box_history(self, box_id: str) -> List[Dict[str, Any]]:
        """Get historical entries for a specific box"""
        all_data = self.load_historical_data()
        return all_data.get(box_id, [])
    
    def add_entry(self, box_id: str, entry_data: Dict[str, Any]) -> bool:
        """
        Add a new historical entry
        
        Args:
            box_id: Box identifier
            entry_data: Dictionary with:
                - date: ISO date string
                - source: "screenshot" or "manual"
                - data_type: "sales", "listings", or "combined"
                - floor_price_usd: float or None
                - active_listings_count: int or None
                - boxes_sold_today: int or None
                - daily_volume_usd: float or None
                - boxes_added_today: int or None
                - visible_market_cap_usd: float or None
                - estimated_total_supply: int or None
                - price_ladder: List of {price, quantity} dicts for T₊ calculation (optional)
                - raw_listings: List of individual listings (optional)
                - raw_sales: List of individual sales (optional)
                - screenshot_metadata: Dict with extraction info (optional)
        """
        all_data = self.load_historical_data()
        
        if box_id not in all_data:
            all_data[box_id] = []
        
        # Ensure date is set
        if "date" not in entry_data:
            entry_data["date"] = date.today().isoformat()
        
        # Add timestamp
        entry_data["timestamp"] = datetime.now().isoformat()
        
        # Add entry
        all_data[box_id].append(entry_data)
        
        # Sort by date
        all_data[box_id].sort(key=lambda x: x.get("date", ""))
        
        return self.save_historical_data(all_data)
    
    def entry_exists(self, box_id: str, entry_date: str, data_type: Optional[str] = None) -> bool:
        """Check if an entry exists for a box and date"""
        history = self.get_box_history(box_id)
        
        for entry in history:
            if entry.get("date") == entry_date:
                if data_type is None or entry.get("data_type") == data_type:
                    return True
        
        return False
    
    def get_latest_entry(self, box_id: str, data_type: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Get the most recent entry for a box"""
        history = self.get_box_history(box_id)
        
        if not history:
            return None
        
        # Filter by data_type if specified
        if data_type:
            history = [e for e in history if e.get("data_type") == data_type]
        
        if not history:
            return None
        
        # Sort by date and return latest
        sorted_history = sorted(history, key=lambda x: x.get("date", ""), reverse=True)
        return sorted_history[0]
    
    def merge_entries(self, box_id: str, date_str: str) -> Dict[str, Any]:
        """
        Merge all entries for a box on a specific date into a single combined entry
        
        This is useful when you have separate sales and listings screenshots for the same day
        """
        history = self.get_box_history(box_id)
        day_entries = [e for e in history if e.get("date") == date_str]
        
        if not day_entries:
            return {}
        
        # Start with the most complete entry
        merged = max(day_entries, key=lambda x: sum(1 for v in x.values() if v is not None))
        merged = merged.copy()
        
        # Merge in data from other entries
        for entry in day_entries:
            for key, value in entry.items():
                if value is not None and (merged.get(key) is None or key in ["raw_sales_data", "screenshot_metadata"]):
                    if key == "raw_sales_data":
                        # Merge sales data lists
                        if "raw_sales_data" not in merged:
                            merged["raw_sales_data"] = []
                        merged["raw_sales_data"].extend(value)
                    elif key == "screenshot_metadata":
                        # Merge metadata
                        if "screenshot_metadata" not in merged:
                            merged["screenshot_metadata"] = []
                        if isinstance(value, list):
                            merged["screenshot_metadata"].extend(value)
                        else:
                            merged["screenshot_metadata"].append(value)
                    else:
                        merged[key] = value
        
        # Mark as combined
        merged["data_type"] = "combined"
        merged["merged_from"] = len(day_entries)
        
        return merged


# Global instance
historical_data_manager = HistoricalDataManager()



Manages historical data entries for each box, tracking what has been entered and when
"""

import json
from datetime import date, datetime
from typing import Dict, Any, List, Optional
from pathlib import Path


class HistoricalDataManager:
    """Manages historical data entries for tracking and duplicate detection"""
    
    def __init__(self):
        self.historical_file = Path(__file__).parent.parent / "data" / "historical_entries.json"
        self.historical_file.parent.mkdir(exist_ok=True)
    
    def load_historical_data(self) -> Dict[str, List[Dict[str, Any]]]:
        """Load all historical data entries"""
        if not self.historical_file.exists():
            return {}
        
        try:
            with open(self.historical_file, 'r') as f:
                return json.load(f)
        except:
            return {}
    
    def save_historical_data(self, data: Dict[str, List[Dict[str, Any]]]) -> bool:
        """Save historical data"""
        try:
            with open(self.historical_file, 'w') as f:
                json.dump(data, f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving historical data: {e}")
            return False
    
    def get_box_history(self, box_id: str) -> List[Dict[str, Any]]:
        """Get historical entries for a specific box"""
        all_data = self.load_historical_data()
        return all_data.get(box_id, [])
    
    def add_entry(self, box_id: str, entry_data: Dict[str, Any]) -> bool:
        """
        Add a new historical entry
        
        Args:
            box_id: Box identifier
            entry_data: Dictionary with:
                - date: ISO date string
                - source: "screenshot" or "manual"
                - data_type: "sales", "listings", or "combined"
                - floor_price_usd: float or None
                - active_listings_count: int or None
                - boxes_sold_today: int or None
                - daily_volume_usd: float or None
                - boxes_added_today: int or None
                - visible_market_cap_usd: float or None
                - estimated_total_supply: int or None
                - price_ladder: List of {price, quantity} dicts for T₊ calculation (optional)
                - raw_listings: List of individual listings (optional)
                - raw_sales: List of individual sales (optional)
                - screenshot_metadata: Dict with extraction info (optional)
        """
        all_data = self.load_historical_data()
        
        if box_id not in all_data:
            all_data[box_id] = []
        
        # Ensure date is set
        if "date" not in entry_data:
            entry_data["date"] = date.today().isoformat()
        
        # Add timestamp
        entry_data["timestamp"] = datetime.now().isoformat()
        
        # Add entry
        all_data[box_id].append(entry_data)
        
        # Sort by date
        all_data[box_id].sort(key=lambda x: x.get("date", ""))
        
        return self.save_historical_data(all_data)
    
    def entry_exists(self, box_id: str, entry_date: str, data_type: Optional[str] = None) -> bool:
        """Check if an entry exists for a box and date"""
        history = self.get_box_history(box_id)
        
        for entry in history:
            if entry.get("date") == entry_date:
                if data_type is None or entry.get("data_type") == data_type:
                    return True
        
        return False
    
    def get_latest_entry(self, box_id: str, data_type: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Get the most recent entry for a box"""
        history = self.get_box_history(box_id)
        
        if not history:
            return None
        
        # Filter by data_type if specified
        if data_type:
            history = [e for e in history if e.get("data_type") == data_type]
        
        if not history:
            return None
        
        # Sort by date and return latest
        sorted_history = sorted(history, key=lambda x: x.get("date", ""), reverse=True)
        return sorted_history[0]
    
    def merge_entries(self, box_id: str, date_str: str) -> Dict[str, Any]:
        """
        Merge all entries for a box on a specific date into a single combined entry
        
        This is useful when you have separate sales and listings screenshots for the same day
        """
        history = self.get_box_history(box_id)
        day_entries = [e for e in history if e.get("date") == date_str]
        
        if not day_entries:
            return {}
        
        # Start with the most complete entry
        merged = max(day_entries, key=lambda x: sum(1 for v in x.values() if v is not None))
        merged = merged.copy()
        
        # Merge in data from other entries
        for entry in day_entries:
            for key, value in entry.items():
                if value is not None and (merged.get(key) is None or key in ["raw_sales_data", "screenshot_metadata"]):
                    if key == "raw_sales_data":
                        # Merge sales data lists
                        if "raw_sales_data" not in merged:
                            merged["raw_sales_data"] = []
                        merged["raw_sales_data"].extend(value)
                    elif key == "screenshot_metadata":
                        # Merge metadata
                        if "screenshot_metadata" not in merged:
                            merged["screenshot_metadata"] = []
                        if isinstance(value, list):
                            merged["screenshot_metadata"].extend(value)
                        else:
                            merged["screenshot_metadata"].append(value)
                    else:
                        merged[key] = value
        
        # Mark as combined
        merged["data_type"] = "combined"
        merged["merged_from"] = len(day_entries)
        
        return merged


# Global instance
historical_data_manager = HistoricalDataManager()



Manages historical data entries for each box, tracking what has been entered and when
"""

import json
from datetime import date, datetime
from typing import Dict, Any, List, Optional
from pathlib import Path


class HistoricalDataManager:
    """Manages historical data entries for tracking and duplicate detection"""
    
    def __init__(self):
        self.historical_file = Path(__file__).parent.parent / "data" / "historical_entries.json"
        self.historical_file.parent.mkdir(exist_ok=True)
    
    def load_historical_data(self) -> Dict[str, List[Dict[str, Any]]]:
        """Load all historical data entries"""
        if not self.historical_file.exists():
            return {}
        
        try:
            with open(self.historical_file, 'r') as f:
                return json.load(f)
        except:
            return {}
    
    def save_historical_data(self, data: Dict[str, List[Dict[str, Any]]]) -> bool:
        """Save historical data"""
        try:
            with open(self.historical_file, 'w') as f:
                json.dump(data, f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving historical data: {e}")
            return False
    
    def get_box_history(self, box_id: str) -> List[Dict[str, Any]]:
        """Get historical entries for a specific box"""
        all_data = self.load_historical_data()
        return all_data.get(box_id, [])
    
    def add_entry(self, box_id: str, entry_data: Dict[str, Any]) -> bool:
        """
        Add a new historical entry
        
        Args:
            box_id: Box identifier
            entry_data: Dictionary with:
                - date: ISO date string
                - source: "screenshot" or "manual"
                - data_type: "sales", "listings", or "combined"
                - floor_price_usd: float or None
                - active_listings_count: int or None
                - boxes_sold_today: int or None
                - daily_volume_usd: float or None
                - boxes_added_today: int or None
                - visible_market_cap_usd: float or None
                - estimated_total_supply: int or None
                - price_ladder: List of {price, quantity} dicts for T₊ calculation (optional)
                - raw_listings: List of individual listings (optional)
                - raw_sales: List of individual sales (optional)
                - screenshot_metadata: Dict with extraction info (optional)
        """
        all_data = self.load_historical_data()
        
        if box_id not in all_data:
            all_data[box_id] = []
        
        # Ensure date is set
        if "date" not in entry_data:
            entry_data["date"] = date.today().isoformat()
        
        # Add timestamp
        entry_data["timestamp"] = datetime.now().isoformat()
        
        # Add entry
        all_data[box_id].append(entry_data)
        
        # Sort by date
        all_data[box_id].sort(key=lambda x: x.get("date", ""))
        
        return self.save_historical_data(all_data)
    
    def entry_exists(self, box_id: str, entry_date: str, data_type: Optional[str] = None) -> bool:
        """Check if an entry exists for a box and date"""
        history = self.get_box_history(box_id)
        
        for entry in history:
            if entry.get("date") == entry_date:
                if data_type is None or entry.get("data_type") == data_type:
                    return True
        
        return False
    
    def get_latest_entry(self, box_id: str, data_type: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Get the most recent entry for a box"""
        history = self.get_box_history(box_id)
        
        if not history:
            return None
        
        # Filter by data_type if specified
        if data_type:
            history = [e for e in history if e.get("data_type") == data_type]
        
        if not history:
            return None
        
        # Sort by date and return latest
        sorted_history = sorted(history, key=lambda x: x.get("date", ""), reverse=True)
        return sorted_history[0]
    
    def merge_entries(self, box_id: str, date_str: str) -> Dict[str, Any]:
        """
        Merge all entries for a box on a specific date into a single combined entry
        
        This is useful when you have separate sales and listings screenshots for the same day
        """
        history = self.get_box_history(box_id)
        day_entries = [e for e in history if e.get("date") == date_str]
        
        if not day_entries:
            return {}
        
        # Start with the most complete entry
        merged = max(day_entries, key=lambda x: sum(1 for v in x.values() if v is not None))
        merged = merged.copy()
        
        # Merge in data from other entries
        for entry in day_entries:
            for key, value in entry.items():
                if value is not None and (merged.get(key) is None or key in ["raw_sales_data", "screenshot_metadata"]):
                    if key == "raw_sales_data":
                        # Merge sales data lists
                        if "raw_sales_data" not in merged:
                            merged["raw_sales_data"] = []
                        merged["raw_sales_data"].extend(value)
                    elif key == "screenshot_metadata":
                        # Merge metadata
                        if "screenshot_metadata" not in merged:
                            merged["screenshot_metadata"] = []
                        if isinstance(value, list):
                            merged["screenshot_metadata"].extend(value)
                        else:
                            merged["screenshot_metadata"].append(value)
                    else:
                        merged[key] = value
        
        # Mark as combined
        merged["data_type"] = "combined"
        merged["merged_from"] = len(day_entries)
        
        return merged


# Global instance
historical_data_manager = HistoricalDataManager()



Manages historical data entries for each box, tracking what has been entered and when
"""

import json
from datetime import date, datetime
from typing import Dict, Any, List, Optional
from pathlib import Path


class HistoricalDataManager:
    """Manages historical data entries for tracking and duplicate detection"""
    
    def __init__(self):
        self.historical_file = Path(__file__).parent.parent / "data" / "historical_entries.json"
        self.historical_file.parent.mkdir(exist_ok=True)
    
    def load_historical_data(self) -> Dict[str, List[Dict[str, Any]]]:
        """Load all historical data entries"""
        if not self.historical_file.exists():
            return {}
        
        try:
            with open(self.historical_file, 'r') as f:
                return json.load(f)
        except:
            return {}
    
    def save_historical_data(self, data: Dict[str, List[Dict[str, Any]]]) -> bool:
        """Save historical data"""
        try:
            with open(self.historical_file, 'w') as f:
                json.dump(data, f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving historical data: {e}")
            return False
    
    def get_box_history(self, box_id: str) -> List[Dict[str, Any]]:
        """Get historical entries for a specific box"""
        all_data = self.load_historical_data()
        return all_data.get(box_id, [])
    
    def add_entry(self, box_id: str, entry_data: Dict[str, Any]) -> bool:
        """
        Add a new historical entry
        
        Args:
            box_id: Box identifier
            entry_data: Dictionary with:
                - date: ISO date string
                - source: "screenshot" or "manual"
                - data_type: "sales", "listings", or "combined"
                - floor_price_usd: float or None
                - active_listings_count: int or None
                - boxes_sold_today: int or None
                - daily_volume_usd: float or None
                - boxes_added_today: int or None
                - visible_market_cap_usd: float or None
                - estimated_total_supply: int or None
                - price_ladder: List of {price, quantity} dicts for T₊ calculation (optional)
                - raw_listings: List of individual listings (optional)
                - raw_sales: List of individual sales (optional)
                - screenshot_metadata: Dict with extraction info (optional)
        """
        all_data = self.load_historical_data()
        
        if box_id not in all_data:
            all_data[box_id] = []
        
        # Ensure date is set
        if "date" not in entry_data:
            entry_data["date"] = date.today().isoformat()
        
        # Add timestamp
        entry_data["timestamp"] = datetime.now().isoformat()
        
        # Add entry
        all_data[box_id].append(entry_data)
        
        # Sort by date
        all_data[box_id].sort(key=lambda x: x.get("date", ""))
        
        return self.save_historical_data(all_data)
    
    def entry_exists(self, box_id: str, entry_date: str, data_type: Optional[str] = None) -> bool:
        """Check if an entry exists for a box and date"""
        history = self.get_box_history(box_id)
        
        for entry in history:
            if entry.get("date") == entry_date:
                if data_type is None or entry.get("data_type") == data_type:
                    return True
        
        return False
    
    def get_latest_entry(self, box_id: str, data_type: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Get the most recent entry for a box"""
        history = self.get_box_history(box_id)
        
        if not history:
            return None
        
        # Filter by data_type if specified
        if data_type:
            history = [e for e in history if e.get("data_type") == data_type]
        
        if not history:
            return None
        
        # Sort by date and return latest
        sorted_history = sorted(history, key=lambda x: x.get("date", ""), reverse=True)
        return sorted_history[0]
    
    def merge_entries(self, box_id: str, date_str: str) -> Dict[str, Any]:
        """
        Merge all entries for a box on a specific date into a single combined entry
        
        This is useful when you have separate sales and listings screenshots for the same day
        """
        history = self.get_box_history(box_id)
        day_entries = [e for e in history if e.get("date") == date_str]
        
        if not day_entries:
            return {}
        
        # Start with the most complete entry
        merged = max(day_entries, key=lambda x: sum(1 for v in x.values() if v is not None))
        merged = merged.copy()
        
        # Merge in data from other entries
        for entry in day_entries:
            for key, value in entry.items():
                if value is not None and (merged.get(key) is None or key in ["raw_sales_data", "screenshot_metadata"]):
                    if key == "raw_sales_data":
                        # Merge sales data lists
                        if "raw_sales_data" not in merged:
                            merged["raw_sales_data"] = []
                        merged["raw_sales_data"].extend(value)
                    elif key == "screenshot_metadata":
                        # Merge metadata
                        if "screenshot_metadata" not in merged:
                            merged["screenshot_metadata"] = []
                        if isinstance(value, list):
                            merged["screenshot_metadata"].extend(value)
                        else:
                            merged["screenshot_metadata"].append(value)
                    else:
                        merged[key] = value
        
        # Mark as combined
        merged["data_type"] = "combined"
        merged["merged_from"] = len(day_entries)
        
        return merged


# Global instance
historical_data_manager = HistoricalDataManager()



Manages historical data entries for each box, tracking what has been entered and when
"""

import json
from datetime import date, datetime
from typing import Dict, Any, List, Optional
from pathlib import Path


class HistoricalDataManager:
    """Manages historical data entries for tracking and duplicate detection"""
    
    def __init__(self):
        self.historical_file = Path(__file__).parent.parent / "data" / "historical_entries.json"
        self.historical_file.parent.mkdir(exist_ok=True)
    
    def load_historical_data(self) -> Dict[str, List[Dict[str, Any]]]:
        """Load all historical data entries"""
        if not self.historical_file.exists():
            return {}
        
        try:
            with open(self.historical_file, 'r') as f:
                return json.load(f)
        except:
            return {}
    
    def save_historical_data(self, data: Dict[str, List[Dict[str, Any]]]) -> bool:
        """Save historical data"""
        try:
            with open(self.historical_file, 'w') as f:
                json.dump(data, f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving historical data: {e}")
            return False
    
    def get_box_history(self, box_id: str) -> List[Dict[str, Any]]:
        """Get historical entries for a specific box"""
        all_data = self.load_historical_data()
        return all_data.get(box_id, [])
    
    def add_entry(self, box_id: str, entry_data: Dict[str, Any]) -> bool:
        """
        Add a new historical entry
        
        Args:
            box_id: Box identifier
            entry_data: Dictionary with:
                - date: ISO date string
                - source: "screenshot" or "manual"
                - data_type: "sales", "listings", or "combined"
                - floor_price_usd: float or None
                - active_listings_count: int or None
                - boxes_sold_today: int or None
                - daily_volume_usd: float or None
                - boxes_added_today: int or None
                - visible_market_cap_usd: float or None
                - estimated_total_supply: int or None
                - price_ladder: List of {price, quantity} dicts for T₊ calculation (optional)
                - raw_listings: List of individual listings (optional)
                - raw_sales: List of individual sales (optional)
                - screenshot_metadata: Dict with extraction info (optional)
        """
        all_data = self.load_historical_data()
        
        if box_id not in all_data:
            all_data[box_id] = []
        
        # Ensure date is set
        if "date" not in entry_data:
            entry_data["date"] = date.today().isoformat()
        
        # Add timestamp
        entry_data["timestamp"] = datetime.now().isoformat()
        
        # Add entry
        all_data[box_id].append(entry_data)
        
        # Sort by date
        all_data[box_id].sort(key=lambda x: x.get("date", ""))
        
        return self.save_historical_data(all_data)
    
    def entry_exists(self, box_id: str, entry_date: str, data_type: Optional[str] = None) -> bool:
        """Check if an entry exists for a box and date"""
        history = self.get_box_history(box_id)
        
        for entry in history:
            if entry.get("date") == entry_date:
                if data_type is None or entry.get("data_type") == data_type:
                    return True
        
        return False
    
    def get_latest_entry(self, box_id: str, data_type: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Get the most recent entry for a box"""
        history = self.get_box_history(box_id)
        
        if not history:
            return None
        
        # Filter by data_type if specified
        if data_type:
            history = [e for e in history if e.get("data_type") == data_type]
        
        if not history:
            return None
        
        # Sort by date and return latest
        sorted_history = sorted(history, key=lambda x: x.get("date", ""), reverse=True)
        return sorted_history[0]
    
    def merge_entries(self, box_id: str, date_str: str) -> Dict[str, Any]:
        """
        Merge all entries for a box on a specific date into a single combined entry
        
        This is useful when you have separate sales and listings screenshots for the same day
        """
        history = self.get_box_history(box_id)
        day_entries = [e for e in history if e.get("date") == date_str]
        
        if not day_entries:
            return {}
        
        # Start with the most complete entry
        merged = max(day_entries, key=lambda x: sum(1 for v in x.values() if v is not None))
        merged = merged.copy()
        
        # Merge in data from other entries
        for entry in day_entries:
            for key, value in entry.items():
                if value is not None and (merged.get(key) is None or key in ["raw_sales_data", "screenshot_metadata"]):
                    if key == "raw_sales_data":
                        # Merge sales data lists
                        if "raw_sales_data" not in merged:
                            merged["raw_sales_data"] = []
                        merged["raw_sales_data"].extend(value)
                    elif key == "screenshot_metadata":
                        # Merge metadata
                        if "screenshot_metadata" not in merged:
                            merged["screenshot_metadata"] = []
                        if isinstance(value, list):
                            merged["screenshot_metadata"].extend(value)
                        else:
                            merged["screenshot_metadata"].append(value)
                    else:
                        merged[key] = value
        
        # Mark as combined
        merged["data_type"] = "combined"
        merged["merged_from"] = len(day_entries)
        
        return merged


# Global instance
historical_data_manager = HistoricalDataManager()



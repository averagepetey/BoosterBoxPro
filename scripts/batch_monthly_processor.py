"""
Batch Monthly Data Processor
Processes multiple monthly snapshots and imports them with specified dates
"""

import sys
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.chat_data_entry import process_data_entry


def process_monthly_snapshots(
    screenshots: List[Dict[str, Any]],
    box_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    Process multiple monthly snapshots with specified dates
    
    Args:
        screenshots: List of dicts, each with:
            - image_bytes: bytes or file path
            - date: ISO date string (YYYY-MM-DD) for the month
            - box_id: Optional box ID if known
            - description: Optional description
        box_id: Optional default box ID if not specified per screenshot
    
    Returns:
        Dictionary with processing results
    """
    results = {
        "total": len(screenshots),
        "successful": 0,
        "failed": 0,
        "results": []
    }
    
    for i, screenshot in enumerate(screenshots):
        try:
            # Get image bytes
            if isinstance(screenshot.get("image_bytes"), str):
                # File path
                image_path = Path(screenshot["image_bytes"])
                if not image_path.exists():
                    results["results"].append({
                        "index": i,
                        "date": screenshot.get("date"),
                        "success": False,
                        "message": f"Image file not found: {screenshot['image_bytes']}"
                    })
                    results["failed"] += 1
                    continue
                with open(image_path, "rb") as f:
                    image_bytes = f.read()
            else:
                image_bytes = screenshot.get("image_bytes")
            
            if not image_bytes:
                results["results"].append({
                    "index": i,
                    "date": screenshot.get("date"),
                    "success": False,
                    "message": "No image bytes provided"
                })
                results["failed"] += 1
                continue
            
            # Get date
            entry_date = screenshot.get("date")
            if not entry_date:
                results["results"].append({
                    "index": i,
                    "date": None,
                    "success": False,
                    "message": "No date specified for screenshot"
                })
                results["failed"] += 1
                continue
            
            # Process the screenshot
            result = process_data_entry(
                image_bytes,
                is_image=True,
                use_ai=True,
                entry_date=entry_date
            )
            
            if result.get("success"):
                results["successful"] += 1
            else:
                results["failed"] += 1
            
            results["results"].append({
                "index": i,
                "date": entry_date,
                "success": result.get("success", False),
                "message": result.get("message", "Unknown error"),
                "box_name": result.get("box_name"),
                "calculated_metrics": result.get("calculated_metrics")
            })
            
        except Exception as e:
            results["results"].append({
                "index": i,
                "date": screenshot.get("date"),
                "success": False,
                "message": f"Error processing screenshot: {str(e)}"
            })
            results["failed"] += 1
    
    return results


def create_monthly_dates(year: int, start_month: int = 1, end_month: int = 12) -> List[str]:
    """
    Generate list of monthly dates for a year
    
    Args:
        year: Year (e.g., 2024)
        start_month: Starting month (1-12)
        end_month: Ending month (1-12)
    
    Returns:
        List of ISO date strings (YYYY-MM-DD) for the 1st of each month
    """
    dates = []
    for month in range(start_month, end_month + 1):
        # Use the 1st of each month
        date_str = f"{year}-{month:02d}-01"
        dates.append(date_str)
    return dates


if __name__ == "__main__":
    print("Batch Monthly Data Processor")
    print("Usage: Provide screenshots with dates when calling process_monthly_snapshots()")
    print("\nExample format:")
    print("""
    screenshots = [
        {
            "image_bytes": "/path/to/january_screenshot.png",
            "date": "2024-01-01",
            "description": "January 2024 data"
        },
        {
            "image_bytes": "/path/to/february_screenshot.png",
            "date": "2024-02-01",
            "description": "February 2024 data"
        },
        # ... etc
    ]
    
    results = process_monthly_snapshots(screenshots)
    """)




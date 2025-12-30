#!/usr/bin/env python3
"""
Check which boxes from Excel will match database
Quick verification script before import
"""

import sys
import os
import asyncio
import re

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import httpx
from app.config import settings


def extract_op_code(set_name: str) -> str:
    """Extract OP code from set name"""
    match = re.search(r'\(OP-(\d+)\)', set_name)
    if match:
        return f"OP-{match.group(1).zfill(2)}"
    return None


async def check_matching():
    """Check which boxes will match"""
    
    api_url = "http://localhost:8000"
    api_key = settings.admin_api_key if settings.admin_api_key else None
    
    headers = {}
    if api_key:
        headers["X-API-Key"] = api_key
    
    # Excel boxes from your data
    excel_boxes = [
        "(OP-01) Romance Dawn (Blue)",
        "(OP-01) Romance Dawn (White)",
        "(OP-02) Paramount War",
        "(OP-03) Pillars of Strength",
        "(OP-04) Kingdoms of Intrigue",
        "(OP-05) Awakening of the New Era",
        "(OP-06) Wings of the Captain",
        "(EB-01) Memorial Collection",
        "(OP-07) 500 Years in the Future",
        "(OP-08) Two Legends",
        "(PRB-01) Premium Booster",
        "(OP-09) Emperors in the New World",
        "(OP-10) Royal Blood",
        "(EB-02) Anime 25th Collection",
        "(OP-11) A Fist of Divine Speed",
        "(OP-12) Legacy of the Master",
        "(PRB-02) Premium Booster",
        "(OP-13) Carrying on His Will",
    ]
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.get(
            f"{api_url}/api/v1/admin/boxes",
            headers=headers
        )
        
        if response.status_code != 200:
            print(f"❌ Error fetching boxes: {response.status_code}")
            return
        
        boxes_data = response.json()
        boxes = boxes_data.get("boxes", [])
        
        # Create mapping
        box_mapping = {}
        for box in boxes:
            box_id = box["id"]
            if box.get("set_name"):
                box_mapping[box["set_name"]] = box_id
            if box.get("product_name"):
                box_mapping[box["product_name"]] = box_id
                if "OP-" in box["product_name"]:
                    parts = box["product_name"].split("OP-")
                    if len(parts) > 1:
                        op_code = "OP-" + parts[1].split()[0]
                        box_mapping[op_code] = box_id
        
        print("=" * 60)
        print("Box Matching Check")
        print("=" * 60)
        print()
        
        matched = []
        unmatched = []
        
        for excel_box in excel_boxes:
            op_code = extract_op_code(excel_box)
            box_id = None
            
            # Try OP code
            if op_code:
                for key, value in box_mapping.items():
                    if op_code.lower() in key.lower():
                        box_id = value
                        matched.append((excel_box, op_code))
                        break
            
            # Try full name
            if not box_id:
                for key, value in box_mapping.items():
                    if key.lower() in excel_box.lower() or excel_box.lower() in key.lower():
                        box_id = value
                        matched.append((excel_box, key))
                        break
            
            if not box_id:
                unmatched.append(excel_box)
        
        print(f"✅ Matched: {len(matched)}/{len(excel_boxes)} boxes")
        print()
        for excel_box, matched_key in matched:
            print(f"  ✅ {excel_box}")
            print(f"     → Matched: {matched_key}")
        
        if unmatched:
            print()
            print(f"⚠️  Unmatched: {len(unmatched)} boxes")
            for excel_box in unmatched:
                print(f"  ⚠️  {excel_box}")
                op_code = extract_op_code(excel_box)
                if op_code:
                    print(f"     OP Code: {op_code}")
        
        print()
        print("=" * 60)
        print(f"Summary: {len(matched)} will import, {len(unmatched)} will be skipped")
        print("=" * 60)


if __name__ == "__main__":
    asyncio.run(check_matching())


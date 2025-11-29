#!/usr/bin/env python3
"""
Flood Support SOS Data Report Generator

This script fetches SOS data from the FloodSupport API and generates
district-wise summary reports in Excel format.
"""

import requests
import pandas as pd
from collections import defaultdict
from datetime import datetime
import os


class FloodSupportReportGenerator:
    """Generate district-wise flood support reports from API data."""
    
    API_BASE_URL = "https://floodsupport.org/api/sos"
    
    def __init__(self):
        self.all_records = []
        self.stats = None
        
    def fetch_all_data(self, limit_per_page=100):
        """Fetch all SOS records from the API with pagination."""
        print("Fetching data from FloodSupport API...")
        
        page = 1
        total_pages = 1
        
        while page <= total_pages:
            print(f"  Fetching page {page}...", end=" ")
            
            try:
                response = requests.get(
                    self.API_BASE_URL,
                    params={"page": page, "limit": limit_per_page},
                    timeout=30
                )
                response.raise_for_status()
                data = response.json()
                
                if data.get("success"):
                    records = data.get("data", [])
                    self.all_records.extend(records)
                    
                    pagination = data.get("pagination", {})
                    total_pages = pagination.get("totalPages", 1)
                    
                    # Store stats from first page
                    if page == 1:
                        self.stats = data.get("stats", {})
                    
                    print(f"Got {len(records)} records")
                else:
                    print(f"API returned success=false")
                    break
                    
            except requests.RequestException as e:
                print(f"Error fetching page {page}: {e}")
                break
            
            page += 1
        
        print(f"\nTotal records fetched: {len(self.all_records)}")
        return self.all_records
    
    def generate_district_summary(self):
        """Generate district-wise summary statistics."""
        
        district_data = defaultdict(lambda: {
            "total": 0,
            "total_people": 0,
            "verified": 0,
            "missing": 0,
            "rescued": 0,
            "pending": 0,
            "cannot_contact": 0,
            "acknowledged": 0,
            "in_progress": 0,
            "completed": 0,
            "critical": 0,
            "high": 0,
            "medium": 0,
            "low": 0,
            # Emergency types
            "trapped": 0,
            "food_water": 0,
            "medical": 0,
            "rescue_assistance": 0,
            "missing_person": 0,
            "dry_food": 0,
            "other": 0,
            # Additional info
            "has_children": 0,
            "has_elderly": 0,
            "has_disabled": 0,
            "has_medical_emergency": 0,
        })
        
        for record in self.all_records:
            district = record.get("district", "").strip() or "Unknown"
            d = district_data[district]
            
            d["total"] += 1
            d["total_people"] += record.get("numberOfPeople", 0) or 0
            
            # Status counts
            status = (record.get("status") or "").upper()
            if status == "VERIFIED":
                d["verified"] += 1
            elif status == "RESCUED":
                d["rescued"] += 1
            elif status == "PENDING":
                d["pending"] += 1
            elif status == "CANNOT_CONTACT":
                d["cannot_contact"] += 1
            elif status == "ACKNOWLEDGED":
                d["acknowledged"] += 1
            elif status == "IN_PROGRESS":
                d["in_progress"] += 1
            elif status == "COMPLETED":
                d["completed"] += 1
            
            # Priority counts
            priority = (record.get("priority") or "").upper()
            if priority == "CRITICAL":
                d["critical"] += 1
            elif priority == "HIGH":
                d["high"] += 1
            elif priority == "MEDIUM":
                d["medium"] += 1
            elif priority == "LOW":
                d["low"] += 1
            
            # Emergency type counts
            emergency_type = (record.get("emergencyType") or "").upper()
            if "TRAPPED" in emergency_type:
                d["trapped"] += 1
            elif "FOOD" in emergency_type or "WATER" in emergency_type:
                d["food_water"] += 1
            elif "MEDICAL" in emergency_type:
                d["medical"] += 1
            elif "RESCUE" in emergency_type:
                d["rescue_assistance"] += 1
            elif "MISSING" in emergency_type:
                d["missing_person"] += 1
                d["missing"] += 1  # Also count in missing
            elif "DRY" in emergency_type:
                d["dry_food"] += 1
            else:
                d["other"] += 1
            
            # Vulnerable groups
            if record.get("hasChildren"):
                d["has_children"] += 1
            if record.get("hasElderly"):
                d["has_elderly"] += 1
            if record.get("hasDisabled"):
                d["has_disabled"] += 1
            if record.get("hasMedicalEmergency"):
                d["has_medical_emergency"] += 1
        
        return district_data
    
    def generate_excel_report(self, output_filename=None):
        """Generate Excel report with multiple sheets."""
        
        if not self.all_records:
            print("No data available. Please fetch data first.")
            return None
        
        if output_filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_filename = f"flood_support_report_{timestamp}.xlsx"
        
        print(f"\nGenerating Excel report: {output_filename}")
        
        district_summary = self.generate_district_summary()
        
        # Create DataFrames
        # 1. District Summary Sheet
        summary_rows = []
        for district, data in sorted(district_summary.items()):
            summary_rows.append({
                "District": district,
                "Total Cases": data["total"],
                "Total People": data["total_people"],
                "Pending": data["pending"],
                "Verified": data["verified"],
                "Acknowledged": data["acknowledged"],
                "In Progress": data["in_progress"],
                "Rescued": data["rescued"],
                "Completed": data["completed"],
                "Cannot Contact": data["cannot_contact"],
                "Missing Persons": data["missing"],
                "Critical Priority": data["critical"],
                "High Priority": data["high"],
                "Medium Priority": data["medium"],
                "Low Priority": data["low"],
            })
        
        # Add totals row
        if summary_rows:
            totals = {key: sum(row[key] for row in summary_rows) if key != "District" else "TOTAL" 
                      for key in summary_rows[0].keys()}
            summary_rows.append(totals)
        
        df_summary = pd.DataFrame(summary_rows)
        
        # 2. Emergency Type by District Sheet
        emergency_rows = []
        for district, data in sorted(district_summary.items()):
            emergency_rows.append({
                "District": district,
                "Trapped": data["trapped"],
                "Food/Water": data["food_water"],
                "Dry Food": data["dry_food"],
                "Medical": data["medical"],
                "Rescue Assistance": data["rescue_assistance"],
                "Missing Person": data["missing_person"],
                "Other": data["other"],
            })
        
        # Add totals
        if emergency_rows:
            totals = {key: sum(row[key] for row in emergency_rows) if key != "District" else "TOTAL" 
                      for key in emergency_rows[0].keys()}
            emergency_rows.append(totals)
        
        df_emergency = pd.DataFrame(emergency_rows)
        
        # 3. Vulnerable Groups by District Sheet
        vulnerable_rows = []
        for district, data in sorted(district_summary.items()):
            vulnerable_rows.append({
                "District": district,
                "Total Cases": data["total"],
                "With Children": data["has_children"],
                "With Elderly": data["has_elderly"],
                "With Disabled": data["has_disabled"],
                "Medical Emergency": data["has_medical_emergency"],
            })
        
        if vulnerable_rows:
            totals = {key: sum(row[key] for row in vulnerable_rows) if key != "District" else "TOTAL" 
                      for key in vulnerable_rows[0].keys()}
            vulnerable_rows.append(totals)
        
        df_vulnerable = pd.DataFrame(vulnerable_rows)
        
        # 4. Overall Stats Sheet
        if self.stats:
            stats_rows = [
                {"Metric": "Total People Affected", "Value": self.stats.get("totalPeople", 0)},
                {"Metric": "Missing People Count", "Value": self.stats.get("missingPeopleCount", 0)},
                {"Metric": "", "Value": ""},
                {"Metric": "--- Status Breakdown ---", "Value": ""},
            ]
            
            for status, count in self.stats.get("byStatus", {}).items():
                stats_rows.append({"Metric": f"Status: {status or 'Unknown'}", "Value": count})
            
            stats_rows.append({"Metric": "", "Value": ""})
            stats_rows.append({"Metric": "--- Priority Breakdown ---", "Value": ""})
            
            for priority, count in self.stats.get("byPriority", {}).items():
                stats_rows.append({"Metric": f"Priority: {priority}", "Value": count})
            
            df_stats = pd.DataFrame(stats_rows)
        else:
            df_stats = pd.DataFrame([{"Metric": "No stats available", "Value": ""}])
        
        # 5. Raw Data Sheet (all records)
        df_raw = pd.DataFrame(self.all_records)
        
        # Reorder columns for raw data
        preferred_columns = [
            "id", "referenceNumber", "fullName", "phoneNumber", "alternatePhone",
            "district", "address", "landmark", "latitude", "longitude",
            "emergencyType", "status", "priority", "numberOfPeople",
            "hasChildren", "hasElderly", "hasDisabled", "hasMedicalEmergency",
            "medicalDetails", "waterLevel", "buildingType", "floorLevel",
            "safeForHours", "hasFood", "hasWater", "hasPowerBank", "batteryPercentage",
            "description", "title", "internalNotes", "verifiedBy", "verifiedLocation",
            "source", "rescueTeam", "actionTaken", "actionTakenAt", "actionTakenBy",
            "acknowledgedAt", "rescuedAt", "completedAt", "createdAt", "updatedAt"
        ]
        
        # Reorder, keeping only columns that exist
        existing_columns = [col for col in preferred_columns if col in df_raw.columns]
        remaining_columns = [col for col in df_raw.columns if col not in preferred_columns]
        df_raw = df_raw[existing_columns + remaining_columns]
        
        # 6. Critical Cases Sheet
        critical_cases = [r for r in self.all_records if r.get("priority") == "CRITICAL"]
        df_critical = pd.DataFrame(critical_cases)
        if not df_critical.empty:
            df_critical = df_critical[[col for col in existing_columns if col in df_critical.columns]]
        
        # Write to Excel with multiple sheets
        with pd.ExcelWriter(output_filename, engine='openpyxl') as writer:
            df_summary.to_excel(writer, sheet_name='District Summary', index=False)
            df_emergency.to_excel(writer, sheet_name='Emergency Types', index=False)
            df_vulnerable.to_excel(writer, sheet_name='Vulnerable Groups', index=False)
            df_stats.to_excel(writer, sheet_name='Overall Stats', index=False)
            df_critical.to_excel(writer, sheet_name='Critical Cases', index=False)
            df_raw.to_excel(writer, sheet_name='All Records', index=False)
            
            # Auto-adjust column widths
            for sheet_name in writer.sheets:
                worksheet = writer.sheets[sheet_name]
                for column in worksheet.columns:
                    max_length = 0
                    column_letter = column[0].column_letter
                    for cell in column:
                        try:
                            if len(str(cell.value)) > max_length:
                                max_length = len(str(cell.value))
                        except:
                            pass
                    adjusted_width = min(max_length + 2, 50)
                    worksheet.column_dimensions[column_letter].width = adjusted_width
        
        print(f"✓ Report generated successfully: {output_filename}")
        print(f"\nSheets included:")
        print(f"  1. District Summary - Status and priority by district")
        print(f"  2. Emergency Types - Type of support needed by district")
        print(f"  3. Vulnerable Groups - Children, elderly, disabled by district")
        print(f"  4. Overall Stats - API statistics summary")
        print(f"  5. Critical Cases - All critical priority cases")
        print(f"  6. All Records - Complete raw data")
        
        return output_filename
    
    def print_summary(self):
        """Print a text summary to console."""
        if not self.all_records:
            print("No data available.")
            return
        
        district_summary = self.generate_district_summary()
        
        print("\n" + "=" * 100)
        print("FLOOD SUPPORT SOS - DISTRICT WISE SUMMARY")
        print("=" * 100)
        print(f"Report Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Total Records: {len(self.all_records)}")
        print("-" * 100)
        
        # Header
        header = f"{'District':<15} {'Total':>6} {'Pending':>8} {'Verified':>9} {'Rescued':>8} {'No Contact':>11} {'Missing':>8} {'Critical':>9} {'High':>6}"
        print(header)
        print("-" * 100)
        
        # Data rows
        totals = defaultdict(int)
        for district, data in sorted(district_summary.items()):
            row = f"{district[:14]:<15} {data['total']:>6} {data['pending']:>8} {data['verified']:>9} {data['rescued']:>8} {data['cannot_contact']:>11} {data['missing']:>8} {data['critical']:>9} {data['high']:>6}"
            print(row)
            
            for key in ['total', 'pending', 'verified', 'rescued', 'cannot_contact', 'missing', 'critical', 'high']:
                totals[key] += data[key]
        
        # Totals row
        print("-" * 100)
        row = f"{'TOTAL':<15} {totals['total']:>6} {totals['pending']:>8} {totals['verified']:>9} {totals['rescued']:>8} {totals['cannot_contact']:>11} {totals['missing']:>8} {totals['critical']:>9} {totals['high']:>6}"
        print(row)
        print("=" * 100)


def main():
    """Main entry point."""
    print("=" * 60)
    print("FLOOD SUPPORT SOS REPORT GENERATOR")
    print("=" * 60)
    
    generator = FloodSupportReportGenerator()
    
    # Fetch all data
    generator.fetch_all_data(limit_per_page=100)
    
    if generator.all_records:
        # Print summary to console
        generator.print_summary()
        
        # Generate Excel report
        output_file = generator.generate_excel_report()
        
        if output_file:
            print(f"\n✓ Report saved to: {os.path.abspath(output_file)}")
    else:
        print("Failed to fetch data from the API.")


if __name__ == "__main__":
    main()

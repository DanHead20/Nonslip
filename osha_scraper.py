#!/usr/bin/env python3
"""
OSHA Incident Scraper for Massachusetts
Searches OSHA establishment database for safety incidents
"""

import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime, timedelta
from typing import List, Dict
import time
import re

class OSHAScraper:
    """
    Scrapes OSHA inspection and incident data
    """
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        self.base_url = "https://www.osha.gov"
    
    def search_establishments(self, state: str = "MA", days_back: int = 30) -> List[Dict]:
        """
        Search OSHA establishment database for recent inspections
        """
        incidents = []
        
        try:
            # OSHA Establishment Search
            search_url = f"{self.base_url}/pls/imis/establishment.html"
            
            print(f"Searching OSHA database for {state} incidents in last {days_back} days...")
            
            # OSHA requires form submission
            # This is a template - actual implementation requires handling their form
            
            # Search parameters
            params = {
                'state': state,
                'officetype': 'All',
                'office': 'All',
                'inspectiontype': 'All',
                'violationtype': 'All'
            }
            
            # In production, this would scrape the actual OSHA database
            
        except Exception as e:
            print(f"Error searching OSHA: {e}")
        
        return incidents
    
    def get_inspection_details(self, inspection_number: str) -> Dict:
        """
        Get detailed information about a specific inspection
        """
        details = {}
        
        try:
            url = f"{self.base_url}/pls/imis/establishment.inspection_detail?id={inspection_number}"
            
            response = self.session.get(url, timeout=10)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Parse inspection details
                # Structure varies but generally includes:
                # - Establishment name
                # - Address
                # - Inspection date
                # - Violations
                # - Hazards
                
        except Exception as e:
            print(f"Error getting inspection details: {e}")
        
        return details
    
    def filter_slip_fall_incidents(self, incidents: List[Dict]) -> List[Dict]:
        """
        Filter incidents specifically for slip, trip, and fall hazards
        """
        slip_fall_keywords = [
            'slip', 'trip', 'fall', 'floor', 'walking', 'surface',
            'wet', 'housekeeping', 'guardrail', 'stair', 'ladder'
        ]
        
        filtered = []
        
        for incident in incidents:
            description = f"{incident.get('violations', '')} {incident.get('hazards', '')}".lower()
            
            if any(keyword in description for keyword in slip_fall_keywords):
                incident['priority'] = 'High'
                incident['match_reason'] = 'Slip/trip/fall related incident'
                filtered.append(incident)
        
        return filtered
    
    def search_by_county(self, counties: List[str], state: str = "MA") -> List[Dict]:
        """
        Search for incidents in specific counties
        """
        all_incidents = []
        
        for county in counties:
            print(f"Searching {county} County, {state}...")
            
            # Implementation would filter by county
            incidents = self.search_establishments(state)
            
            # Filter by county
            county_incidents = [
                i for i in incidents 
                if county.lower() in i.get('county', '').lower()
            ]
            
            all_incidents.extend(county_incidents)
            time.sleep(2)  # Be respectful
        
        return all_incidents


def scrape_osha_incidents(counties: List[str] = ['Middlesex', 'Norfolk', 'Worcester']) -> List[Dict]:
    """
    Main function to scrape OSHA incidents for target counties
    """
    scraper = OSHAScraper()
    
    # Get all incidents
    incidents = scraper.search_by_county(counties, state="MA")
    
    # Filter for slip/fall related
    slip_fall_incidents = scraper.filter_slip_fall_incidents(incidents)
    
    print(f"Total incidents found: {len(incidents)}")
    print(f"Slip/fall related: {len(slip_fall_incidents)}")
    
    return slip_fall_incidents


if __name__ == "__main__":
    incidents = scrape_osha_incidents()
    
    if incidents:
        df = pd.DataFrame(incidents)
        df.to_csv('osha_incidents.csv', index=False)
        print("Results saved to osha_incidents.csv")

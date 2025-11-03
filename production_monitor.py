#!/usr/bin/env python3
"""
Production Lead Monitor with Working Data Sources
This version uses multiple real data sources that work without special access
"""

import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime, timedelta
import json
import re
from typing import List, Dict
import time

class ProductionLeadMonitor:
    """
    Production version using publicly accessible data sources
    """
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        self.leads = []
    
    def search_google_news(self, query: str, location: str = "Massachusetts") -> List[Dict]:
        """
        Search Google News for relevant business activities
        """
        leads = []
        
        try:
            # Search for news about new restaurants, renovations, etc.
            search_queries = [
                f"new restaurant opening {location}",
                f"restaurant renovation {location}",
                f"new hotel opening {location}",
                f"school renovation {location}",
                f"nursing home opened {location}",
                f"fitness center opening {location}"
            ]
            
            for query in search_queries:
                print(f"Searching news: {query}")
                
                # Use Google News RSS (publicly accessible)
                encoded_query = requests.utils.quote(query)
                url = f"https://news.google.com/rss/search?q={encoded_query}&hl=en-US&gl=US&ceid=US:en"
                
                response = self.session.get(url, timeout=10)
                
                if response.status_code == 200:
                    # Parse RSS feed
                    soup = BeautifulSoup(response.content, 'xml')
                    items = soup.find_all('item')
                    
                    for item in items[:5]:  # Get top 5 results per query
                        title = item.find('title').text if item.find('title') else ""
                        link = item.find('link').text if item.find('link') else ""
                        pub_date = item.find('pubDate').text if item.find('pubDate') else ""
                        description = item.find('description').text if item.find('description') else ""
                        
                        # Extract business name and location from title
                        lead = {
                            'source': 'Google News',
                            'title': title,
                            'description': description,
                            'url': link,
                            'date': pub_date,
                            'search_query': query,
                            'type': 'News Mention'
                        }
                        
                        leads.append(lead)
                
                time.sleep(2)  # Be respectful
        
        except Exception as e:
            print(f"Error searching Google News: {e}")
        
        return leads
    
    def search_osha_data(self, state: str = "MA") -> List[Dict]:
        """
        Search OSHA's public data downloads
        OSHA provides downloadable datasets
        """
        incidents = []
        
        try:
            print("Accessing OSHA public data...")
            
            # OSHA provides public data files
            # https://www.osha.gov/severeinjury
            url = "https://www.osha.gov/severeinjury"
            
            response = self.session.get(url, timeout=10)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Parse recent severe injury reports
                # These are publicly listed incidents
                
                # Find all incident rows
                incident_divs = soup.find_all('div', class_='severeinjury-item')
                
                for div in incident_divs[:20]:  # Get recent 20
                    try:
                        company = div.find('strong').text.strip() if div.find('strong') else ""
                        text = div.get_text()
                        
                        # Extract details
                        incident = {
                            'source': 'OSHA',
                            'company': company,
                            'description': text,
                            'type': 'Safety Incident',
                            'priority': 'High',
                            'state': state
                        }
                        
                        # Check if it's in Massachusetts
                        if 'MA' in text or 'Massachusetts' in text:
                            incidents.append(incident)
                    
                    except Exception as e:
                        continue
        
        except Exception as e:
            print(f"Error accessing OSHA data: {e}")
        
        return incidents
    
    def search_business_registrations(self, county: str) -> List[Dict]:
        """
        Search Massachusetts business registrations
        Secretary of State publishes new business filings
        """
        businesses = []
        
        try:
            print(f"Searching business registrations for {county}...")
            
            # Massachusetts Secretary of State business search
            # This is public data but requires careful scraping
            
            # For demo purposes, we'll structure what we'd collect
            # Real implementation would need to handle their search form
            
        except Exception as e:
            print(f"Error searching business registrations: {e}")
        
        return businesses
    
    def search_yelp_new_businesses(self, location: str, categories: List[str]) -> List[Dict]:
        """
        Search Yelp for recently added businesses (publicly accessible)
        """
        businesses = []
        
        try:
            for category in categories:
                print(f"Searching Yelp: {category} in {location}")
                
                # Yelp search URL (publicly accessible)
                url = f"https://www.yelp.com/search?find_desc={category}&find_loc={location}"
                
                response = self.session.get(url, timeout=10)
                
                if response.status_code == 200:
                    soup = BeautifulSoup(response.content, 'html.parser')
                    
                    # Parse business listings
                    # Look for "Opened recently" or similar indicators
                    
                    # This is simplified - actual implementation would parse Yelp's structure
                    
                time.sleep(3)  # Respect rate limits
        
        except Exception as e:
            print(f"Error searching Yelp: {e}")
        
        return businesses
    
    def enrich_with_contact_info(self, business_name: str, address: str) -> Dict:
        """
        Try to find contact information for a business
        Uses public search engines
        """
        contact_info = {}
        
        try:
            # Search for business + phone number
            query = f"{business_name} {address} phone number"
            encoded = requests.utils.quote(query)
            
            # This would use public sources to find contact info
            # Implementation would respect robots.txt and terms of service
            
        except Exception as e:
            pass
        
        return contact_info
    
    def filter_by_target_industries(self, leads: List[Dict], keywords: List[str]) -> List[Dict]:
        """
        Filter leads to match target industries
        """
        filtered = []
        
        for lead in leads:
            # Combine all text fields
            text = " ".join([
                str(lead.get('title', '')),
                str(lead.get('description', '')),
                str(lead.get('company', '')),
                str(lead.get('category', ''))
            ]).lower()
            
            # Check if any keyword matches
            for keyword in keywords:
                if keyword.lower() in text:
                    lead['matched_keyword'] = keyword
                    filtered.append(lead)
                    break
        
        return filtered
    
    def run_full_scan(self) -> List[Dict]:
        """
        Run complete scan of all sources
        """
        all_leads = []
        
        print("=" * 60)
        print("STARTING FULL LEAD SCAN")
        print("=" * 60)
        
        # Target industries
        target_keywords = [
            'restaurant', 'dining', 'food service',
            'hospital', 'healthcare', 'medical center', 'clinic',
            'school', 'university', 'college', 'education',
            'hotel', 'motel', 'resort', 'lodging',
            'country club', 'golf club',
            'assisted living', 'nursing home', 'senior living', 'retirement',
            'fitness center', 'gym', 'health club', 'wellness center'
        ]
        
        # 1. Search Google News
        news_leads = self.search_google_news("new business opening", "Massachusetts")
        all_leads.extend(news_leads)
        
        # 2. Search OSHA incidents
        osha_leads = self.search_osha_data("MA")
        all_leads.extend(osha_leads)
        
        # 3. Filter by target industries
        filtered_leads = self.filter_by_target_industries(all_leads, target_keywords)
        
        print(f"\nTotal leads found: {len(all_leads)}")
        print(f"Filtered to target industries: {len(filtered_leads)}")
        
        return filtered_leads


# Helper function to format leads for email
def format_leads_for_email(leads: List[Dict]) -> str:
    """Format leads as HTML email"""
    
    html = f"""
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; max-width: 900px; margin: 0 auto; }}
            h1 {{ color: #2c3e50; border-bottom: 3px solid #3498db; padding-bottom: 10px; }}
            .summary {{ background: #ecf0f1; padding: 20px; border-radius: 5px; margin: 20px 0; }}
            .lead {{ 
                background: #fff; 
                border: 1px solid #ddd; 
                padding: 15px; 
                margin: 15px 0; 
                border-left: 4px solid #3498db;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }}
            .high-priority {{ border-left-color: #e74c3c; }}
            .lead-title {{ font-size: 18px; font-weight: bold; color: #2c3e50; margin-bottom: 10px; }}
            .lead-detail {{ margin: 5px 0; }}
            .label {{ font-weight: bold; color: #555; }}
            .source-tag {{ 
                display: inline-block; 
                background: #3498db; 
                color: white; 
                padding: 3px 10px; 
                border-radius: 3px; 
                font-size: 12px;
                margin: 5px 0;
            }}
            .priority-tag {{ background: #e74c3c; }}
        </style>
    </head>
    <body>
        <h1>🎯 Daily Non-Slip Lead Report</h1>
        <p style="color: #666;">Generated: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}</p>
        
        <div class="summary">
            <h2 style="margin-top: 0;">📊 Summary</h2>
            <p><strong>Total Leads:</strong> {len(leads)}</p>
            <p><strong>High Priority (OSHA):</strong> {len([l for l in leads if l.get('source') == 'OSHA'])}</p>
            <p><strong>News Mentions:</strong> {len([l for l in leads if l.get('source') == 'Google News'])}</p>
        </div>
        
        <h2>🔥 High Priority Leads</h2>
    """
    
    # Add OSHA incidents first
    osha_leads = [l for l in leads if l.get('source') == 'OSHA']
    if osha_leads:
        for lead in osha_leads:
            html += f"""
            <div class="lead high-priority">
                <span class="source-tag priority-tag">OSHA INCIDENT</span>
                <div class="lead-title">{lead.get('company', 'Unknown Business')}</div>
                <div class="lead-detail"><span class="label">Description:</span> {lead.get('description', 'N/A')}</div>
                <div class="lead-detail" style="color: #e74c3c; font-weight: bold; margin-top: 10px;">
                    ⚠️ ACTION: Contact immediately - recent safety incident indicates need for slip prevention solutions
                </div>
            </div>
            """
    else:
        html += "<p>No OSHA incidents found today.</p>"
    
    # Add news leads
    html += "<h2>📰 New Business Activities</h2>"
    news_leads = [l for l in leads if l.get('source') == 'Google News']
    if news_leads:
        for lead in news_leads:
            html += f"""
            <div class="lead">
                <span class="source-tag">NEWS</span>
                <div class="lead-title">{lead.get('title', 'N/A')}</div>
                <div class="lead-detail"><span class="label">Description:</span> {lead.get('description', 'N/A')}</div>
                <div class="lead-detail"><span class="label">Date:</span> {lead.get('date', 'N/A')}</div>
                <div class="lead-detail"><span class="label">Industry Match:</span> {lead.get('matched_keyword', 'N/A')}</div>
                <div class="lead-detail"><a href="{lead.get('url', '#')}">Read full article →</a></div>
            </div>
            """
    else:
        html += "<p>No news mentions found today.</p>"
    
    html += """
        <hr style="margin: 40px 0; border: none; border-top: 1px solid #ddd;">
        <p style="color: #999; font-size: 12px;">
            This is an automated lead generation report for your non-slip business.<br>
            Delivered daily to Dhead20@gmail.com
        </p>
    </body>
    </html>
    """
    
    return html


if __name__ == "__main__":
    monitor = ProductionLeadMonitor()
    leads = monitor.run_full_scan()
    
    # Save to CSV
    if leads:
        df = pd.DataFrame(leads)
        filename = f"leads_{datetime.now().strftime('%Y%m%d')}.csv"
        df.to_csv(filename, index=False)
        print(f"\nLeads saved to {filename}")
    
    # Generate email HTML
    html_report = format_leads_for_email(leads)
    
    # Save HTML report
    html_filename = f"report_{datetime.now().strftime('%Y%m%d')}.html"
    with open(html_filename, 'w') as f:
        f.write(html_report)
    print(f"Report saved to {html_filename}")

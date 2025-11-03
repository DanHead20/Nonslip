#!/usr/bin/env python3
"""
Non-Slip Business Lead Monitor
Monitors building permits and OSHA incidents for Massachusetts counties
Sends daily email digest to Dhead20@gmail.com
"""

import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime, timedelta
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
import json
import re
from typing import List, Dict
import time

# Configuration
TARGET_COUNTIES = ['Middlesex', 'Norfolk', 'Worcester']
TARGET_INDUSTRIES = [
    'restaurant', 'food service', 'healthcare', 'hospital', 'school', 
    'university', 'college', 'hotel', 'country club', 'assisted living',
    'nursing home', 'senior living', '55+', 'fitness center', 'gym'
]
EMAIL_RECIPIENT = 'Dhead20@gmail.com'

class LeadMonitor:
    def __init__(self):
        self.leads = []
        self.permits = []
        self.osha_incidents = []
        
    def search_ma_permits(self):
        """
        Search Massachusetts building permits
        Note: MA municipalities have separate permit systems
        """
        print("Searching Massachusetts building permits...")
        
        # Major cities in target counties
        cities = {
            'Middlesex': ['Cambridge', 'Lowell', 'Newton', 'Somerville', 'Framingham', 'Waltham', 'Malden', 'Medford'],
            'Norfolk': ['Quincy', 'Brookline', 'Weymouth', 'Braintree', 'Needham', 'Milton'],
            'Worcester': ['Worcester', 'Leominster', 'Fitchburg', 'Shrewsbury', 'Marlborough']
        }
        
        for county, city_list in cities.items():
            for city in city_list:
                try:
                    # Try to search public permit databases
                    # Note: Each city may have different systems
                    permit_data = self._search_city_permits(city, county)
                    self.permits.extend(permit_data)
                    time.sleep(1)  # Be respectful with requests
                except Exception as e:
                    print(f"Error searching {city}: {e}")
        
        return self.permits
    
    def _search_city_permits(self, city: str, county: str) -> List[Dict]:
        """
        Search for building permits in a specific city
        This is a template - actual implementation depends on city websites
        """
        permits = []
        
        # Boston/Cambridge use Citizen Portal
        if city.lower() in ['cambridge', 'boston', 'somerville']:
            # These cities often have public APIs or structured data
            # Example structure for what we'd collect
            pass
        
        # For this demo, we'll create a function that shows the structure
        # In production, you'd scrape actual city permit sites
        
        return permits
    
    def search_osha_incidents(self):
        """
        Search OSHA incident database for Massachusetts
        """
        print("Searching OSHA incidents...")
        
        try:
            # OSHA Establishment Search
            # This would query their database
            # Note: OSHA doesn't have a public API, so this requires web scraping
            
            base_url = "https://www.osha.gov/pls/imis/establishment.html"
            
            # We'll create a structure for what we'd collect
            # In production, this would actually scrape OSHA
            
            incidents = self._query_osha_data()
            self.osha_incidents.extend(incidents)
            
        except Exception as e:
            print(f"Error searching OSHA: {e}")
        
        return self.osha_incidents
    
    def _query_osha_data(self) -> List[Dict]:
        """
        Query OSHA database for recent incidents
        """
        incidents = []
        
        # OSHA data structure we'd collect:
        # - Establishment name
        # - Address
        # - Industry
        # - Incident date
        # - Incident description
        # - Inspection number
        
        return incidents
    
    def filter_by_industry(self, data: List[Dict]) -> List[Dict]:
        """
        Filter results to match target industries
        """
        filtered = []
        
        for item in data:
            text = f"{item.get('name', '')} {item.get('description', '')} {item.get('industry', '')}".lower()
            
            for industry_keyword in TARGET_INDUSTRIES:
                if industry_keyword.lower() in text:
                    filtered.append(item)
                    break
        
        return filtered
    
    def enrich_lead_data(self, lead: Dict) -> Dict:
        """
        Add additional information to leads (phone, website, etc.)
        """
        # Could integrate with:
        # - Google Places API for phone/website
        # - Yellow Pages scraping
        # - Business registry databases
        
        return lead
    
    def generate_email_report(self) -> str:
        """
        Generate HTML email report
        """
        today = datetime.now().strftime("%B %d, %Y")
        
        html = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; }}
                h1 {{ color: #2c3e50; }}
                h2 {{ color: #34495e; margin-top: 30px; }}
                .lead {{ 
                    background-color: #f8f9fa; 
                    padding: 15px; 
                    margin: 10px 0; 
                    border-left: 4px solid #3498db;
                }}
                .priority {{ border-left-color: #e74c3c; }}
                .field {{ margin: 5px 0; }}
                .label {{ font-weight: bold; }}
                .summary {{ 
                    background-color: #ecf0f1; 
                    padding: 15px; 
                    margin: 20px 0;
                }}
            </style>
        </head>
        <body>
            <h1>🎯 Daily Non-Slip Lead Report</h1>
            <p>Generated: {today}</p>
            
            <div class="summary">
                <h3>Summary</h3>
                <p><strong>New Building Permits:</strong> {len(self.permits)}</p>
                <p><strong>OSHA Incidents:</strong> {len(self.osha_incidents)}</p>
                <p><strong>Total Leads:</strong> {len(self.permits) + len(self.osha_incidents)}</p>
            </div>
        """
        
        # Add permit leads
        if self.permits:
            html += "<h2>🏗️ New Building Permits & Renovations</h2>"
            for permit in self.permits:
                html += self._format_permit_html(permit)
        else:
            html += "<h2>🏗️ New Building Permits & Renovations</h2><p>No new permits found today.</p>"
        
        # Add OSHA incidents
        if self.osha_incidents:
            html += "<h2>⚠️ OSHA Safety Incidents</h2>"
            for incident in self.osha_incidents:
                html += self._format_incident_html(incident)
        else:
            html += "<h2>⚠️ OSHA Safety Incidents</h2><p>No new incidents found today.</p>"
        
        html += """
            <hr>
            <p style="color: #7f8c8d; font-size: 12px;">
                This is an automated report. Reply to this email won't be monitored.
            </p>
        </body>
        </html>
        """
        
        return html
    
    def _format_permit_html(self, permit: Dict) -> str:
        """Format permit data as HTML"""
        priority_class = "priority" if permit.get('priority') else ""
        
        return f"""
        <div class="lead {priority_class}">
            <div class="field"><span class="label">Business:</span> {permit.get('name', 'N/A')}</div>
            <div class="field"><span class="label">Address:</span> {permit.get('address', 'N/A')}</div>
            <div class="field"><span class="label">City:</span> {permit.get('city', 'N/A')}, {permit.get('county', 'N/A')} County</div>
            <div class="field"><span class="label">Project Type:</span> {permit.get('project_type', 'N/A')}</div>
            <div class="field"><span class="label">Permit Date:</span> {permit.get('date', 'N/A')}</div>
            <div class="field"><span class="label">Industry:</span> {permit.get('industry', 'N/A')}</div>
            {f'<div class="field"><span class="label">Phone:</span> {permit.get("phone", "N/A")}</div>' if permit.get('phone') else ''}
            {f'<div class="field"><span class="label">Website:</span> <a href="{permit.get("website")}">{permit.get("website")}</a></div>' if permit.get('website') else ''}
            <div class="field"><span class="label">Estimated Value:</span> ${permit.get('value', 'N/A')}</div>
        </div>
        """
    
    def _format_incident_html(self, incident: Dict) -> str:
        """Format OSHA incident as HTML"""
        return f"""
        <div class="lead priority">
            <div class="field"><span class="label">⚠️ Business:</span> {incident.get('name', 'N/A')}</div>
            <div class="field"><span class="label">Address:</span> {incident.get('address', 'N/A')}</div>
            <div class="field"><span class="label">City:</span> {incident.get('city', 'N/A')}</div>
            <div class="field"><span class="label">Industry:</span> {incident.get('industry', 'N/A')}</div>
            <div class="field"><span class="label">Incident Date:</span> {incident.get('date', 'N/A')}</div>
            <div class="field"><span class="label">Description:</span> {incident.get('description', 'N/A')}</div>
            <div class="field"><span class="label">Inspection #:</span> {incident.get('inspection_number', 'N/A')}</div>
            {f'<div class="field"><span class="label">Phone:</span> {incident.get("phone", "N/A")}</div>' if incident.get('phone') else ''}
            <div class="field" style="color: #e74c3c; margin-top: 10px;">
                <strong>Action:</strong> High priority - facility just experienced safety incident
            </div>
        </div>
        """
    
    def send_email(self, html_content: str):
        """
        Send email report via Gmail SMTP
        Requires app password to be set in environment variable
        """
        smtp_password = os.environ.get('GMAIL_APP_PASSWORD')
        
        if not smtp_password:
            print("ERROR: GMAIL_APP_PASSWORD environment variable not set")
            print("Saving report to file instead...")
            self.save_to_file(html_content)
            return
        
        msg = MIMEMultipart('alternative')
        msg['Subject'] = f"Non-Slip Leads - {datetime.now().strftime('%B %d, %Y')}"
        msg['From'] = EMAIL_RECIPIENT  # Send from same email
        msg['To'] = EMAIL_RECIPIENT
        
        html_part = MIMEText(html_content, 'html')
        msg.attach(html_part)
        
        try:
            with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
                server.login(EMAIL_RECIPIENT, smtp_password)
                server.send_message(msg)
            print(f"Email sent successfully to {EMAIL_RECIPIENT}")
        except Exception as e:
            print(f"Error sending email: {e}")
            self.save_to_file(html_content)
    
    def save_to_file(self, html_content: str):
        """Save report to HTML file as backup"""
        filename = f"lead_report_{datetime.now().strftime('%Y%m%d')}.html"
        with open(filename, 'w') as f:
            f.write(html_content)
        print(f"Report saved to {filename}")
    
    def save_to_csv(self):
        """Save all leads to CSV for tracking"""
        all_leads = []
        
        for permit in self.permits:
            all_leads.append({
                'date_found': datetime.now().strftime('%Y-%m-%d'),
                'type': 'Permit',
                'name': permit.get('name'),
                'address': permit.get('address'),
                'city': permit.get('city'),
                'county': permit.get('county'),
                'industry': permit.get('industry'),
                'phone': permit.get('phone'),
                'website': permit.get('website'),
                'details': permit.get('project_type'),
                'priority': 'Medium'
            })
        
        for incident in self.osha_incidents:
            all_leads.append({
                'date_found': datetime.now().strftime('%Y-%m-%d'),
                'type': 'OSHA Incident',
                'name': incident.get('name'),
                'address': incident.get('address'),
                'city': incident.get('city'),
                'county': incident.get('county'),
                'industry': incident.get('industry'),
                'phone': incident.get('phone'),
                'website': incident.get('website'),
                'details': incident.get('description'),
                'priority': 'High'
            })
        
        if all_leads:
            df = pd.DataFrame(all_leads)
            filename = f"leads_{datetime.now().strftime('%Y%m%d')}.csv"
            df.to_csv(filename, index=False)
            print(f"Leads saved to {filename}")
    
    def run(self):
        """Main execution function"""
        print("=" * 50)
        print("Starting Lead Monitor...")
        print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 50)
        
        # Search for permits
        self.search_ma_permits()
        
        # Search OSHA incidents
        self.search_osha_incidents()
        
        # Filter by target industries
        self.permits = self.filter_by_industry(self.permits)
        self.osha_incidents = self.filter_by_industry(self.osha_incidents)
        
        # Generate report
        html_report = self.generate_email_report()
        
        # Send email
        self.send_email(html_report)
        
        # Save to CSV
        self.save_to_csv()
        
        print("=" * 50)
        print("Lead Monitor Complete!")
        print(f"Permits found: {len(self.permits)}")
        print(f"OSHA incidents found: {len(self.osha_incidents)}")
        print("=" * 50)


if __name__ == "__main__":
    monitor = LeadMonitor()
    monitor.run()

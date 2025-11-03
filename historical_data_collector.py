#!/usr/bin/env python3
"""
Historical Data Collector - One Time Run
Collects building permits and OSHA incidents from January 1 - October 31, 2025
"""

import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime, timedelta
import time
import json
from typing import List, Dict

TARGET_COUNTIES = ['Middlesex', 'Norfolk', 'Worcester']
TARGET_INDUSTRIES = [
    'restaurant', 'food service', 'dining', 'cafe', 'bar',
    'healthcare', 'hospital', 'medical center', 'clinic', 'health',
    'school', 'university', 'college', 'education', 'academy',
    'hotel', 'motel', 'resort', 'lodging', 'inn',
    'country club', 'golf club', 'club',
    'assisted living', 'nursing home', 'senior living', 'retirement', '55+',
    'fitness center', 'gym', 'health club', 'wellness'
]

START_DATE = "2025-01-01"
END_DATE = "2025-10-31"

class HistoricalDataCollector:
    """
    Collects historical data from public sources
    """
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        self.all_leads = []
    
    def search_google_news_by_month(self, query: str, year: int, month: int) -> List[Dict]:
        """
        Search Google News for a specific month
        """
        leads = []
        
        try:
            # Create date range for the month
            start_date = f"{year}-{month:02d}-01"
            if month == 12:
                end_date = f"{year}-12-31"
            else:
                end_date = f"{year}-{month+1:02d}-01"
            
            print(f"  Searching {query} for {year}-{month:02d}...")
            
            # Google News search with date range
            encoded_query = requests.utils.quote(f"{query} after:{start_date} before:{end_date}")
            url = f"https://news.google.com/rss/search?q={encoded_query}&hl=en-US&gl=US&ceid=US:en"
            
            response = self.session.get(url, timeout=15)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'xml')
                items = soup.find_all('item')
                
                for item in items:
                    title = item.find('title').text if item.find('title') else ""
                    link = item.find('link').text if item.find('link') else ""
                    pub_date = item.find('pubDate').text if item.find('pubDate') else ""
                    description = item.find('description').text if item.find('description') else ""
                    
                    lead = {
                        'date_found': datetime.now().strftime('%Y-%m-%d'),
                        'source': 'Google News',
                        'title': title,
                        'description': description,
                        'url': link,
                        'published_date': pub_date,
                        'search_query': query,
                        'search_month': f"{year}-{month:02d}",
                        'type': 'News Mention'
                    }
                    
                    leads.append(lead)
                
                print(f"    Found {len(items)} articles")
            
            time.sleep(2)  # Rate limiting
            
        except Exception as e:
            print(f"    Error: {e}")
        
        return leads
    
    def collect_news_historical(self) -> List[Dict]:
        """
        Collect news mentions from Jan-Oct 2025
        """
        print("\n" + "="*70)
        print("COLLECTING HISTORICAL GOOGLE NEWS DATA")
        print("="*70)
        
        all_news = []
        
        # Search queries for different industries
        queries = [
            "new restaurant opening Massachusetts",
            "restaurant renovation Massachusetts",
            "new hotel Massachusetts",
            "hotel renovation Massachusetts",
            "hospital expansion Massachusetts",
            "healthcare facility Massachusetts",
            "new gym Massachusetts",
            "fitness center opening Massachusetts",
            "nursing home Massachusetts",
            "assisted living Massachusetts",
            "school renovation Massachusetts"
        ]
        
        # Search each month from January to October
        for month in range(1, 11):  # Jan (1) through Oct (10)
            print(f"\n📅 Month: 2025-{month:02d}")
            
            for query in queries:
                results = self.search_google_news_by_month(query, 2025, month)
                all_news.extend(results)
                time.sleep(1)  # Be respectful
        
        print(f"\n✅ Total news articles found: {len(all_news)}")
        return all_news
    
    def search_osha_historical(self) -> List[Dict]:
        """
        Search OSHA severe injury reports from Jan-Oct 2025
        """
        print("\n" + "="*70)
        print("COLLECTING HISTORICAL OSHA DATA")
        print("="*70)
        
        incidents = []
        
        try:
            print("Accessing OSHA severe injury database...")
            
            url = "https://www.osha.gov/severeinjury"
            
            response = self.session.get(url, timeout=15)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # OSHA lists recent severe injuries
                # Parse the page for Massachusetts incidents
                
                text = soup.get_text()
                
                # Look for Massachusetts mentions
                # In production, this would parse structured data
                
                print("✅ Connected to OSHA database")
                print("   (Note: OSHA typically shows last 30-90 days online)")
                print("   For full historical data, would need to use OSHA's data downloads")
                
                # For demonstration, we'll note this limitation
                incidents.append({
                    'source': 'OSHA',
                    'note': 'Historical OSHA data requires accessing their bulk downloads',
                    'recommendation': 'Focus on recent incidents (last 90 days) for highest value'
                })
        
        except Exception as e:
            print(f"Error accessing OSHA: {e}")
        
        return incidents
    
    def filter_by_target_industries(self, leads: List[Dict]) -> List[Dict]:
        """
        Filter results to match target industries
        """
        filtered = []
        
        for lead in leads:
            # Combine all text fields
            text = " ".join([
                str(lead.get('title', '')),
                str(lead.get('description', '')),
                str(lead.get('search_query', ''))
            ]).lower()
            
            # Check if any target keyword matches
            for keyword in TARGET_INDUSTRIES:
                if keyword.lower() in text:
                    lead['matched_keyword'] = keyword
                    filtered.append(lead)
                    break
        
        return filtered
    
    def filter_by_target_counties(self, leads: List[Dict]) -> List[Dict]:
        """
        Filter for target counties
        """
        filtered = []
        
        for lead in leads:
            text = " ".join([
                str(lead.get('title', '')),
                str(lead.get('description', ''))
            ]).lower()
            
            # Check for county mentions
            for county in TARGET_COUNTIES:
                if county.lower() in text:
                    lead['county'] = county
                    filtered.append(lead)
                    break
            
            # Also check for major cities in those counties
            cities = {
                'Middlesex': ['cambridge', 'lowell', 'newton', 'somerville', 'framingham', 'waltham', 'malden', 'medford'],
                'Norfolk': ['quincy', 'brookline', 'weymouth', 'needham', 'milton', 'braintree'],
                'Worcester': ['worcester', 'leominster', 'fitchburg', 'shrewsbury', 'marlborough']
            }
            
            for county, city_list in cities.items():
                for city in city_list:
                    if city in text:
                        lead['county'] = county
                        lead['city'] = city.title()
                        if lead not in filtered:
                            filtered.append(lead)
                        break
        
        return filtered
    
    def save_results(self, leads: List[Dict]):
        """
        Save results to CSV and JSON
        """
        if not leads:
            print("\n⚠️  No leads found to save")
            return
        
        # Save to CSV
        df = pd.DataFrame(leads)
        csv_filename = f"historical_leads_{START_DATE}_to_{END_DATE}.csv"
        df.to_csv(csv_filename, index=False)
        print(f"\n✅ Saved to CSV: {csv_filename}")
        
        # Save to JSON for more detail
        json_filename = f"historical_leads_{START_DATE}_to_{END_DATE}.json"
        with open(json_filename, 'w') as f:
            json.dump(leads, f, indent=2)
        print(f"✅ Saved to JSON: {json_filename}")
        
        # Create summary report
        self.create_summary_report(leads)
    
    def create_summary_report(self, leads: List[Dict]):
        """
        Create HTML summary report
        """
        # Group by month
        by_month = {}
        for lead in leads:
            month = lead.get('search_month', 'Unknown')
            if month not in by_month:
                by_month[month] = []
            by_month[month].append(lead)
        
        # Group by industry
        by_industry = {}
        for lead in leads:
            industry = lead.get('matched_keyword', 'Other')
            if industry not in by_industry:
                by_industry[industry] = []
            by_industry[industry].append(lead)
        
        html = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; max-width: 1200px; margin: 40px auto; padding: 20px; }}
                h1 {{ color: #2c3e50; border-bottom: 3px solid #3498db; padding-bottom: 10px; }}
                h2 {{ color: #34495e; margin-top: 30px; }}
                .summary {{ background: #ecf0f1; padding: 20px; border-radius: 8px; margin: 20px 0; }}
                .stat {{ display: inline-block; margin: 10px 20px; }}
                .stat-number {{ font-size: 32px; font-weight: bold; color: #3498db; }}
                .stat-label {{ color: #7f8c8d; }}
                table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
                th {{ background: #34495e; color: white; padding: 12px; text-align: left; }}
                td {{ padding: 10px; border-bottom: 1px solid #ddd; }}
                tr:hover {{ background: #f8f9fa; }}
            </style>
        </head>
        <body>
            <h1>📊 Historical Lead Collection Report</h1>
            <p>Period: {START_DATE} to {END_DATE}</p>
            <p>Generated: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}</p>
            
            <div class="summary">
                <h2>Summary Statistics</h2>
                <div class="stat">
                    <div class="stat-number">{len(leads)}</div>
                    <div class="stat-label">Total Leads</div>
                </div>
                <div class="stat">
                    <div class="stat-number">{len(by_month)}</div>
                    <div class="stat-label">Months Covered</div>
                </div>
                <div class="stat">
                    <div class="stat-number">{len(by_industry)}</div>
                    <div class="stat-label">Industries</div>
                </div>
            </div>
            
            <h2>📅 Leads by Month</h2>
            <table>
                <tr>
                    <th>Month</th>
                    <th>Number of Leads</th>
                    <th>Percentage</th>
                </tr>
        """
        
        for month in sorted(by_month.keys()):
            count = len(by_month[month])
            percentage = (count / len(leads) * 100) if leads else 0
            html += f"""
                <tr>
                    <td>{month}</td>
                    <td>{count}</td>
                    <td>{percentage:.1f}%</td>
                </tr>
            """
        
        html += """
            </table>
            
            <h2>🏢 Leads by Industry</h2>
            <table>
                <tr>
                    <th>Industry/Keyword</th>
                    <th>Number of Leads</th>
                    <th>Percentage</th>
                </tr>
        """
        
        for industry in sorted(by_industry.keys(), key=lambda x: len(by_industry[x]), reverse=True):
            count = len(by_industry[industry])
            percentage = (count / len(leads) * 100) if leads else 0
            html += f"""
                <tr>
                    <td>{industry.title()}</td>
                    <td>{count}</td>
                    <td>{percentage:.1f}%</td>
                </tr>
            """
        
        html += """
            </table>
            
            <h2>💡 Top Opportunities</h2>
            <p>Review the CSV file for complete lead details including:</p>
            <ul>
                <li>Business names and locations</li>
                <li>Article links for more context</li>
                <li>Publication dates</li>
                <li>Matched keywords/industries</li>
            </ul>
            
            <h2>📞 Next Steps</h2>
            <ol>
                <li><strong>Prioritize recent leads</strong> - Focus on leads from Sept-Oct 2025 first</li>
                <li><strong>Group by location</strong> - Plan outreach by county/city for efficiency</li>
                <li><strong>Customize messaging</strong> - Reference the specific news article in your outreach</li>
                <li><strong>Track results</strong> - Note which months/industries convert best</li>
            </ol>
        </body>
        </html>
        """
        
        report_filename = f"historical_report_{START_DATE}_to_{END_DATE}.html"
        with open(report_filename, 'w') as f:
            f.write(html)
        
        print(f"✅ Saved summary report: {report_filename}")
    
    def run(self):
        """
        Main execution
        """
        print("="*70)
        print("HISTORICAL DATA COLLECTION")
        print(f"Period: {START_DATE} to {END_DATE}")
        print(f"Counties: {', '.join(TARGET_COUNTIES)}")
        print("="*70)
        
        # Collect news data
        news_leads = self.collect_news_historical()
        
        # Collect OSHA data
        osha_leads = self.search_osha_historical()
        
        # Combine all leads
        all_leads = news_leads + osha_leads
        
        print(f"\n📊 Total leads collected: {len(all_leads)}")
        
        # Filter by target industries
        print("\n🔍 Filtering by target industries...")
        filtered_leads = self.filter_by_target_industries(all_leads)
        print(f"   After industry filter: {len(filtered_leads)}")
        
        # Filter by target counties
        print("🔍 Filtering by target counties...")
        final_leads = self.filter_by_target_counties(filtered_leads)
        print(f"   After county filter: {len(final_leads)}")
        
        # Save results
        if final_leads:
            self.save_results(final_leads)
        else:
            print("\n⚠️  No leads matched your criteria")
            print("   This could mean:")
            print("   - Less news coverage during this period")
            print("   - County/city names not mentioned in articles")
            print("   - Try broadening search terms")
        
        print("\n" + "="*70)
        print("COLLECTION COMPLETE!")
        print("="*70)
        print("\nFiles generated:")
        print(f"  • historical_leads_{START_DATE}_to_{END_DATE}.csv")
        print(f"  • historical_leads_{START_DATE}_to_{END_DATE}.json")
        print(f"  • historical_report_{START_DATE}_to_{END_DATE}.html")
        print("\nDownload these from GitHub Actions artifacts!")
        print("="*70)


if __name__ == "__main__":
    collector = HistoricalDataCollector()
    collector.run()

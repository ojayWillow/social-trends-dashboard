import requests
from config import Config

class GoogleTrendsCollector:
    """Collect data from Google Trends via SerpApi"""
    
    def __init__(self):
        self.api_key = Config.SERPAPI_KEY
        self.base_url = Config.SERPAPI_BASE
    
    def get_interest_over_time(self, query, geo='', time_range='today 12-m'):
        """Get search interest over time for a query"""
        params = {
            'engine': 'google_trends',
            'q': query,
            'data_type': 'TIMESERIES',
            'api_key': self.api_key
        }
        
        if geo:
            params['geo'] = geo
        
        try:
            response = requests.get(self.base_url, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"❌ Error fetching Google Trends data: {e}")
            return None
    
    def get_related_queries(self, query, geo=''):
        """Get related queries for a search term"""
        params = {
            'engine': 'google_trends',
            'q': query,
            'data_type': 'RELATED_QUERIES',
            'api_key': self.api_key
        }
        
        if geo:
            params['geo'] = geo
        
        try:
            response = requests.get(self.base_url, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"❌ Error fetching related queries: {e}")
            return None

# Test the collector
if __name__ == '__main__':
    collector = GoogleTrendsCollector()
    print("=" * 60)
    print("📊 Testing Google Trends API (SerpApi)...")
    print("=" * 60)
    
    print("\n🔍 Search interest for 'artificial intelligence':\n")
    trends = collector.get_interest_over_time('artificial intelligence')
    
    if trends and 'interest_over_time' in trends:
        timeline = trends.get('interest_over_time', {}).get('timeline_data', [])
        print(f"   📈 Found {len(timeline)} data points\n")
        
        # Show last 5 data points
        for point in timeline[-5:]:
            date = point.get('date', 'Unknown')
            values = point.get('values', [])
            if values:
                value = values[0].get('extracted_value', 0)
                print(f"   {date}: {value}/100")
    else:
        print("   ❌ No data received")

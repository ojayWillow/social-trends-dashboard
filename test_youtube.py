import requests
from config import Config

class YouTubeCollector:
    """Collect data from YouTube Data API"""
    
    def __init__(self):
        self.api_key = Config.YOUTUBE_API_KEY
        self.base_url = Config.YOUTUBE_API_BASE
    
    def get_trending_videos(self, region_code='US', max_results=10):
        """Fetch trending videos"""
        url = f"{self.base_url}/videos"
        params = {
            'part': 'snippet,statistics',
            'chart': 'mostPopular',
            'regionCode': region_code,
            'maxResults': max_results,
            'key': self.api_key
        }
        
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"❌ Error fetching YouTube data: {e}")
            return None

# Test the collector
if __name__ == '__main__':
    collector = YouTubeCollector()
    print("🎥 Testing YouTube API...")
    
    trending = collector.get_trending_videos(max_results=5)
    if trending:
        print(f"✅ Found {len(trending.get('items', []))} trending videos")
        for video in trending.get('items', [])[:3]:
            title = video['snippet']['title']
            views = video['statistics']['viewCount']
            print(f"   - {title} ({views} views)")
    else:
        print("❌ Failed to fetch trending videos")

from apify_client import ApifyClient
from config import Config

class TikTokCollector:
    """Collect data from TikTok via Apify"""
    
    def __init__(self):
        self.client = ApifyClient(Config.APIFY_TOKEN)
    
    def scrape_hashtag(self, hashtag, max_videos=50):
        """Scrape videos for a specific hashtag"""
        run_input = {
            "hashtags": [hashtag],
            "resultsPerPage": max_videos,
            "shouldDownloadVideos": False
        }
        
        try:
            print(f"🔄 Starting TikTok scrape for #{hashtag}...")
            run = self.client.actor("clockworks/tiktok-scraper").call(run_input=run_input)
            
            # Fetch results
            items = []
            for item in self.client.dataset(run["defaultDatasetId"]).iterate_items():
                items.append(item)
            
            return items
        except Exception as e:
            print(f"❌ Error scraping TikTok: {e}")
            return []

# Test the collector
if __name__ == '__main__':
    collector = TikTokCollector()
    print("=" * 60)
    print("🎵 Testing TikTok API (Apify)...")
    print("=" * 60)
    
    print("\n🔍 Scraping videos for #ai (limit: 5)...\n")
    print("⚠️  This may take 1-2 minutes...\n")
    
    videos = collector.scrape_hashtag('ai', max_videos=5)
    
    print(f"\n✅ Found {len(videos)} videos\n")
    
    for i, video in enumerate(videos[:3], 1):
        text = video.get('text', 'No description')[:60]
        views = video.get('playCount', 0)
        likes = video.get('diggCount', 0)
        
        print(f"{i}. {text}...")
        print(f"   👁️  {views:,} views | ❤️ {likes:,} likes\n")

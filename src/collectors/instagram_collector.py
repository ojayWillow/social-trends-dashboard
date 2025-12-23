from apify_client import ApifyClient
from config import Config

class InstagramCollector:
    """Collect data from Instagram via Apify"""
    
    def __init__(self):
        self.client = ApifyClient(Config.APIFY_TOKEN)
    
    def scrape_hashtag(self, hashtag, max_posts=50):
        """Scrape posts for a specific hashtag"""
        run_input = {
            "directUrls": [f"https://www.instagram.com/explore/tags/{hashtag}/"],
            "resultsType": "posts",
            "resultsLimit": max_posts,
            "searchType": "hashtag"
        }
        
        try:
            print(f"🔄 Starting Instagram scrape for #{hashtag}...")
            run = self.client.actor("apify/instagram-scraper").call(run_input=run_input)
            
            # Fetch results
            items = []
            for item in self.client.dataset(run["defaultDatasetId"]).iterate_items():
                items.append(item)
            
            return items
        except Exception as e:
            print(f"❌ Error scraping Instagram: {e}")
            return []

# Test the collector
if __name__ == '__main__':
    collector = InstagramCollector()
    print("=" * 60)
    print("📷 Testing Instagram API (Apify)...")
    print("=" * 60)
    
    print("\n🔍 Scraping posts for #ai (limit: 5)...\n")
    posts = collector.scrape_hashtag('ai', max_posts=5)
    
    print(f"✅ Found {len(posts)} posts\n")
    
    for i, post in enumerate(posts[:3], 1):
        caption = post.get('caption', 'No caption')[:60]
        likes = post.get('likesCount', 0)
        comments = post.get('commentsCount', 0)
        
        print(f"{i}. {caption}...")
        print(f"   ❤️  {likes} likes | 💬 {comments} comments\n")

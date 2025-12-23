from apify_client import ApifyClient
from config import Config

class TwitterCollector:
    """Collect data from Twitter/X via Apify"""
    
    def __init__(self):
        self.client = ApifyClient(Config.APIFY_TOKEN)
    
    def search_tweets(self, query, max_tweets=50):
        """
        Search for tweets by query/keywords
        
        Args:
            query: Search query (keywords, hashtags, @mentions)
            max_tweets: Maximum number of tweets to fetch (default: 50)
        """
        run_input = {
            "searchTerms": [query],
            "maxTweets": max_tweets,
            "addUserInfo": True,
            "scrapeTweetReplies": False
        }
        
        try:
            print(f"🔍 Starting Twitter search for '{query}'...")
            run = self.client.actor("apidojo/tweet-scraper").call(run_input=run_input)
            
            # Fetch results
            items = []
            for item in self.client.dataset(run["defaultDatasetId"]).iterate_items():
                items.append(item)
            
            return items
            
        except Exception as e:
            print(f"❌ Error scraping Twitter: {e}")
            return []
    
    def get_user_tweets(self, username, max_tweets=50):
        """
        Get tweets from a specific user
        
        Args:
            username: Twitter username (without @)
            max_tweets: Maximum number of tweets to fetch
        """
        run_input = {
            "handles": [username],
            "tweetsDesired": max_tweets,
            "addUserInfo": True
        }
        
        try:
            print(f"🔍 Fetching tweets from @{username}...")
            run = self.client.actor("apidojo/tweet-scraper").call(run_input=run_input)
            
            items = []
            for item in self.client.dataset(run["defaultDatasetId"]).iterate_items():
                items.append(item)
            
            return items
            
        except Exception as e:
            print(f"❌ Error fetching user tweets: {e}")
            return []
    
    def get_trending_tweets(self, hashtag, max_tweets=50):
        """
        Get trending tweets for a specific hashtag
        
        Args:
            hashtag: Hashtag to search (with or without #)
            max_tweets: Maximum number of tweets
        """
        # Ensure hashtag starts with #
        if not hashtag.startswith('#'):
            hashtag = f"#{hashtag}"
        
        return self.search_tweets(hashtag, max_tweets)


# Test the collector
if __name__ == "__main__":
    collector = TwitterCollector()
    
    print("\n🔥 Testing Twitter Collector...")
    print("=" * 60)
    
    # Test: Search for tweets
    print("\n1️⃣ Searching for tweets about 'python programming'...")
    results = collector.search_tweets("python programming", max_tweets=5)
    
    if results:
        print(f"✅ Found {len(results)} tweets")
        for i, tweet in enumerate(results[:3], 1):
            print(f"\n{i}. {tweet.get('full_text', 'N/A')[:100]}...")
            print(f"   By: @{tweet.get('user', {}).get('screen_name', 'unknown')}")
            print(f"   Likes: {tweet.get('favorite_count', 0)} | Retweets: {tweet.get('retweet_count', 0)}")
    else:
        print("❌ No tweets found")
    
    print("\n" + "=" * 60)
    print("✅ Twitter Collector Test Complete!\n")

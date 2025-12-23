import requests
from config import Config

class RedditCollector:
    """Collect data from Reddit JSON API (no authentication needed)"""
    
    def __init__(self):
        self.base_url = Config.REDDIT_API_BASE
        self.headers = {
            'User-Agent': 'SocialMediaDashboard/1.0'
        }
    
    def get_hot_posts(self, subreddit, limit=25):
        """Fetch hot posts from a subreddit"""
        url = f"{self.base_url}/r/{subreddit}/hot.json"
        params = {'limit': limit}
        
        try:
            response = requests.get(url, params=params, headers=self.headers)
            response.raise_for_status()
            data = response.json()
            return data.get('data', {}).get('children', [])
        except requests.exceptions.RequestException as e:
            print(f"❌ Error fetching Reddit data: {e}")
            return []
    
    def get_top_posts(self, subreddit, time_filter='day', limit=25):
        """Fetch top posts from a subreddit"""
        url = f"{self.base_url}/r/{subreddit}/top.json"
        params = {
            'limit': limit,
            't': time_filter  # hour, day, week, month, year, all
        }
        
        try:
            response = requests.get(url, params=params, headers=self.headers)
            response.raise_for_status()
            data = response.json()
            return data.get('data', {}).get('children', [])
        except requests.exceptions.RequestException as e:
            print(f"❌ Error fetching Reddit top posts: {e}")
            return []
    
    def search_posts(self, subreddit, query, limit=25):
        """Search posts in a subreddit"""
        url = f"{self.base_url}/r/{subreddit}/search.json"
        params = {
            'q': query,
            'limit': limit,
            'restrict_sr': 'true'
        }
        
        try:
            response = requests.get(url, params=params, headers=self.headers)
            response.raise_for_status()
            data = response.json()
            return data.get('data', {}).get('children', [])
        except requests.exceptions.RequestException as e:
            print(f"❌ Error searching Reddit: {e}")
            return []

# Test the collector
if __name__ == '__main__':
    collector = RedditCollector()
    print("=" * 60)
    print("👽 Testing Reddit API...")
    print("=" * 60)
    
    # Test hot posts
    print("\n🔥 Hot posts from r/technology:\n")
    hot_posts = collector.get_hot_posts('technology', limit=5)
    for post in hot_posts:
        data = post.get('data', {})
        title = data.get('title', 'No title')
        score = data.get('score', 0)
        comments = data.get('num_comments', 0)
        print(f"   📄 {title}")
        print(f"      ⬆️  {score} upvotes | 💬 {comments} comments\n")
    
    # Test top posts
    print("\n⭐ Top posts today from r/startups:\n")
    top_posts = collector.get_top_posts('startups', time_filter='day', limit=3)
    for post in top_posts:
        data = post.get('data', {})
        title = data.get('title', 'No title')
        score = data.get('score', 0)
        print(f"   📄 {title}")
        print(f"      ⬆️  {score} upvotes\n")

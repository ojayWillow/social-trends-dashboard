import requests
from config import Config

class HackerNewsCollector:
    """Collect data from Hacker News Firebase API"""
    
    def __init__(self):
        self.base_url = Config.HACKERNEWS_API_BASE
    
    def get_top_stories(self, limit=30):
        """Fetch top story IDs"""
        url = f"{self.base_url}/topstories.json"
        
        try:
            response = requests.get(url)
            response.raise_for_status()
            story_ids = response.json()
            return story_ids[:limit]
        except requests.exceptions.RequestException as e:
            print(f"❌ Error fetching HN top stories: {e}")
            return []
    
    def get_new_stories(self, limit=30):
        """Fetch new story IDs"""
        url = f"{self.base_url}/newstories.json"
        
        try:
            response = requests.get(url)
            response.raise_for_status()
            story_ids = response.json()
            return story_ids[:limit]
        except requests.exceptions.RequestException as e:
            print(f"❌ Error fetching HN new stories: {e}")
            return []
    
    def get_item(self, item_id):
        """Fetch item details by ID"""
        url = f"{self.base_url}/item/{item_id}.json"
        
        try:
            response = requests.get(url)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"❌ Error fetching HN item {item_id}: {e}")
            return None
    
    def get_top_stories_with_details(self, limit=10):
        """Fetch top stories with full details"""
        story_ids = self.get_top_stories(limit)
        stories = []
        
        for story_id in story_ids:
            story = self.get_item(story_id)
            if story:
                stories.append(story)
        
        return stories

# Test the collector
if __name__ == '__main__':
    collector = HackerNewsCollector()
    print("=" * 60)
    print("🔶 Testing Hacker News API...")
    print("=" * 60)
    
    print("\n📰 Top 5 stories on Hacker News:\n")
    stories = collector.get_top_stories_with_details(limit=5)
    
    for i, story in enumerate(stories, 1):
        title = story.get('title', 'No title')
        score = story.get('score', 0)
        comments = story.get('descendants', 0)
        url = story.get('url', 'No URL')
        
        print(f"{i}. {title}")
        print(f"   ⬆️  {score} points | 💬 {comments} comments")
        print(f"   🔗 {url}\n")

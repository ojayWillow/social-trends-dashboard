import requests
from config import Config
import time

class TwitterApifyCollector:
    """Collect data from Twitter/X using Apify API"""
    
    def __init__(self):
        self.api_key = Config.APIFY_TOKEN
        self.base_url = Config.APIFY_API_BASE
        self.actor_id = 'apify/twitter-scraper'  # Official Apify Twitter scraper
    
    def search_tweets(self, query, max_tweets=50, sort='Latest'):
        """Search tweets by query/hashtag"""
        run_input = {
            'searchTerms': [query],
            'maxTweets': max_tweets,
            'sort': sort,  # Latest, Top, Photos, Videos
            'tweetLanguage': 'en',
            'addUserInfo': True
        }
        
        return self._run_actor(run_input)
    
    def get_trending_topics(self, location='Worldwide'):
        """Get trending topics (Note: This requires Twitter API access)"""
        # Alternative: Search for popular hashtags
        popular_hashtags = [
            '#AI', '#Tech', '#Crypto', '#Fitness', '#Business',
            '#Marketing', '#Startup', '#Programming', '#Design'
        ]
        
        all_tweets = []
        for hashtag in popular_hashtags[:5]:  # Limit to avoid rate limits
            tweets = self.search_tweets(hashtag, max_tweets=20, sort='Top')
            if tweets:
                all_tweets.extend(tweets)
            time.sleep(2)  # Rate limiting
        
        return all_tweets
    
    def get_user_tweets(self, username, max_tweets=50):
        """Get tweets from a specific user"""
        run_input = {
            'handles': [username],
            'tweetsDesired': max_tweets,
            'addUserInfo': True
        }
        
        return self._run_actor(run_input)
    
    def search_by_niche(self, niche_keywords, max_tweets=100):
        """Search tweets by niche keywords"""
        query = ' OR '.join(niche_keywords)
        return self.search_tweets(query, max_tweets=max_tweets, sort='Top')
    
    def _run_actor(self, run_input):
        """Run Apify actor and wait for results"""
        url = f"{self.base_url}/acts/{self.actor_id}/runs"
        headers = {'Authorization': f'Bearer {self.api_key}'}
        
        try:
            # Start the actor
            response = requests.post(url, json={'input': run_input}, headers=headers)
            response.raise_for_status()
            run_data = response.json()
            run_id = run_data['data']['id']
            
            # Wait for completion
            status_url = f"{self.base_url}/actor-runs/{run_id}"
            max_wait = 120  # 2 minutes
            waited = 0
            
            while waited < max_wait:
                time.sleep(5)
                waited += 5
                
                status_response = requests.get(status_url, headers=headers)
                status_data = status_response.json()
                status = status_data['data']['status']
                
                if status == 'SUCCEEDED':
                    # Get results
                    dataset_id = status_data['data']['defaultDatasetId']
                    results_url = f"{self.base_url}/datasets/{dataset_id}/items"
                    results_response = requests.get(results_url, headers=headers)
                    return results_response.json()
                
                elif status in ['FAILED', 'ABORTED', 'TIMED-OUT']:
                    print(f"❌ Actor run failed with status: {status}")
                    return None
            
            print("⏰ Timeout waiting for actor results")
            return None
            
        except requests.exceptions.RequestException as e:
            print(f"❌ Error running Twitter scraper: {e}")
            return None
    
    def extract_trending_data(self, tweets):
        """Extract and structure trending data from tweets"""
        if not tweets:
            return {'tweets': [], 'hashtags': [], 'keywords': []}
        
        from collections import Counter
        import re
        
        structured_tweets = []
        all_hashtags = []
        all_keywords = []
        
        for tweet in tweets:
            # Extract basic info
            structured_tweets.append({
                'text': tweet.get('text', ''),
                'username': tweet.get('author', {}).get('userName', ''),
                'name': tweet.get('author', {}).get('name', ''),
                'likes': tweet.get('likeCount', 0),
                'retweets': tweet.get('retweetCount', 0),
                'replies': tweet.get('replyCount', 0),
                'views': tweet.get('viewCount', 0),
                'url': tweet.get('url', ''),
                'created': tweet.get('createdAt', ''),
                'media': tweet.get('media', [])
            })
            
            # Extract hashtags
            text = tweet.get('text', '')
            hashtags = re.findall(r'#\w+', text)
            all_hashtags.extend([h.lower() for h in hashtags])
            
            # Extract keywords (simple word extraction)
            words = re.findall(r'\b[a-zA-Z]{4,}\b', text.lower())
            all_keywords.extend(words)
        
        # Count frequencies
        hashtag_counts = Counter(all_hashtags)
        keyword_counts = Counter(all_keywords)
        
        return {
            'tweets': sorted(structured_tweets, key=lambda x: x['likes'] + x['retweets'], reverse=True)[:20],
            'top_hashtags': [{'hashtag': k, 'count': v} for k, v in hashtag_counts.most_common(15)],
            'top_keywords': [{'keyword': k, 'count': v} for k, v in keyword_counts.most_common(15)],
            'total_engagement': sum(t['likes'] + t['retweets'] + t['replies'] for t in structured_tweets)
        }


if __name__ == '__main__':
    collector = TwitterApifyCollector()
    print("="*60)
    print("🐦 Testing Twitter/X API (Apify)...")
    print("="*60)
    
    print("\n🔍 Searching for #AI tweets...\n")
    tweets = collector.search_tweets('#AI', max_tweets=10)
    
    if tweets:
        data = collector.extract_trending_data(tweets)
        print(f"✅ Found {len(data['tweets'])} tweets")
        print(f"📊 Total engagement: {data['total_engagement']}")
        
        if data['top_hashtags']:
            print("\n🏷️ Top hashtags:")
            for hashtag in data['top_hashtags'][:5]:
                print(f"   {hashtag['hashtag']}: {hashtag['count']}")
    else:
        print("❌ No tweets found")

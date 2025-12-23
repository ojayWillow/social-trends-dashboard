import json
import os
from datetime import datetime
from collections import Counter
import re
from typing import Dict, List, Any

from src.collectors.google_trends_collector import GoogleTrendsCollector
from src.collectors.reddit_collector import RedditCollector
from src.collectors.hackernews_collector import HackerNewsCollector
from src.collectors.youtube_collector import YouTubeCollector
from config import Config


class TrendAggregator:
    """Aggregate and analyze trending content from all platforms"""
    
    def __init__(self):
        self.google_collector = GoogleTrendsCollector()
        self.reddit_collector = RedditCollector()
        self.hn_collector = HackerNewsCollector()
        self.youtube_collector = YouTubeCollector()
        
        # Create data directories
        os.makedirs(Config.PROCESSED_DATA_DIR, exist_ok=True)
    
    def extract_hashtags(self, text: str) -> List[str]:
        """Extract hashtags from text"""
        if not text:
            return []
        return re.findall(r'#\w+', text.lower())
    
    def extract_keywords(self, text: str, min_length: int = 4) -> List[str]:
        """Extract keywords from text (simple word extraction)"""
        if not text:
            return []
        # Remove special characters and split
        words = re.findall(r'\b[a-zA-Z]{' + str(min_length) + r',}\b', text.lower())
        # Filter out common stop words
        stop_words = {'this', 'that', 'with', 'from', 'have', 'been', 'will', 'your', 'their', 'what', 'when', 'where', 'which', 'about', 'there', 'these', 'those'}
        return [w for w in words if w not in stop_words]
    
    def get_youtube_trends(self, max_results: int = 25) -> Dict[str, Any]:
        """Get trending content from YouTube"""
        print("\n📺 Fetching YouTube trends...")
        
        data = self.youtube_collector.get_trending_videos(max_results=max_results)
        
        if not data or 'items' not in data:
            return {'videos': [], 'top_titles': [], 'total_views': 0}
        
        videos = []
        all_keywords = []
        total_views = 0
        
        for item in data['items']:
            snippet = item.get('snippet', {})
            stats = item.get('statistics', {})
            
            title = snippet.get('title', '')
            views = int(stats.get('viewCount', 0))
            likes = int(stats.get('likeCount', 0))
            comments = int(stats.get('commentCount', 0))
            
            videos.append({
                'title': title,
                'channel': snippet.get('channelTitle', ''),
                'views': views,
                'likes': likes,
                'comments': comments,
                'published': snippet.get('publishedAt', ''),
                'tags': snippet.get('tags', [])[:5]  # Top 5 tags
            })
            
            # Extract keywords from title
            all_keywords.extend(self.extract_keywords(title))
            total_views += views
        
        # Get most common keywords
        keyword_counts = Counter(all_keywords)
        top_keywords = [{'keyword': k, 'count': v} for k, v in keyword_counts.most_common(10)]
        
        return {
            'videos': sorted(videos, key=lambda x: x['views'], reverse=True)[:10],
            'top_keywords': top_keywords,
            'total_views': total_views,
            'total_videos': len(videos)
        }
    
    def get_reddit_trends(self, subreddits: List[str] = None, limit: int = 25) -> Dict[str, Any]:
        """Get trending content from Reddit"""
        print("\n👽 Fetching Reddit trends...")
        
        if subreddits is None:
            subreddits = ['all', 'popular', 'technology', 'programming', 'startups']
        
        all_posts = []
        all_keywords = []
        hashtags = []
        
        for subreddit in subreddits:
            posts = self.reddit_collector.get_hot_posts(subreddit, limit=limit)
            
            for post in posts:
                data = post.get('data', {})
                title = data.get('title', '')
                score = data.get('score', 0)
                
                all_posts.append({
                    'title': title,
                    'subreddit': data.get('subreddit', ''),
                    'score': score,
                    'comments': data.get('num_comments', 0),
                    'url': data.get('url', ''),
                    'author': data.get('author', ''),
                    'created': data.get('created_utc', 0)
                })
                
                # Extract keywords and hashtags
                all_keywords.extend(self.extract_keywords(title))
                hashtags.extend(self.extract_hashtags(title))
        
        # Get most common items
        keyword_counts = Counter(all_keywords)
        hashtag_counts = Counter(hashtags)
        
        return {
            'posts': sorted(all_posts, key=lambda x: x['score'], reverse=True)[:10],
            'top_keywords': [{'keyword': k, 'count': v} for k, v in keyword_counts.most_common(10)],
            'top_hashtags': [{'hashtag': k, 'count': v} for k, v in hashtag_counts.most_common(10)],
            'total_posts': len(all_posts),
            'subreddits_analyzed': subreddits
        }
    
    def get_hackernews_trends(self, limit: int = 30) -> Dict[str, Any]:
        """Get trending content from Hacker News"""
        print("\n🔶 Fetching Hacker News trends...")
        
        stories = self.hn_collector.get_top_stories_with_details(limit=limit)
        
        all_keywords = []
        
        for story in stories:
            title = story.get('title', '')
            all_keywords.extend(self.extract_keywords(title))
        
        keyword_counts = Counter(all_keywords)
        
        return {
            'stories': [
                {
                    'title': s.get('title', ''),
                    'score': s.get('score', 0),
                    'comments': s.get('descendants', 0),
                    'url': s.get('url', ''),
                    'author': s.get('by', ''),
                    'time': s.get('time', 0)
                }
                for s in stories[:10]
            ],
            'top_keywords': [{'keyword': k, 'count': v} for k, v in keyword_counts.most_common(10)],
            'total_stories': len(stories)
        }
    
    def get_google_trends(self, queries: List[str] = None) -> Dict[str, Any]:
        """Get trending searches from Google Trends"""
        print("\n📊 Fetching Google Trends...")
        
        if queries is None:
            # Use some default trending topics
            queries = ['ai', 'cryptocurrency', 'climate change', 'technology', 'startup']
        
        trends_data = []
        
        for query in queries:
            data = self.google_collector.get_interest_over_time(query)
            
            if data and 'interest_over_time' in data:
                timeline = data.get('interest_over_time', {}).get('timeline_data', [])
                
                if timeline:
                    # Get latest interest value
                    latest = timeline[-1]
                    values = latest.get('values', [])
                    
                    if values:
                        trends_data.append({
                            'query': query,
                            'interest': values[0].get('extracted_value', 0),
                            'date': latest.get('date', ''),
                            'trend_direction': self._calculate_trend_direction(timeline)
                        })
        
        return {
            'trends': sorted(trends_data, key=lambda x: x['interest'], reverse=True),
            'queries_analyzed': queries
        }
    
    def _calculate_trend_direction(self, timeline: List[Dict]) -> str:
        """Calculate if trend is rising, falling, or stable"""
        if len(timeline) < 2:
            return 'stable'
        
        recent_values = []
        for point in timeline[-5:]:
            values = point.get('values', [])
            if values:
                recent_values.append(values[0].get('extracted_value', 0))
        
        if len(recent_values) < 2:
            return 'stable'
        
        avg_first_half = sum(recent_values[:len(recent_values)//2]) / (len(recent_values)//2)
        avg_second_half = sum(recent_values[len(recent_values)//2:]) / (len(recent_values) - len(recent_values)//2)
        
        diff_percent = ((avg_second_half - avg_first_half) / avg_first_half * 100) if avg_first_half > 0 else 0
        
        if diff_percent > 10:
            return 'rising'
        elif diff_percent < -10:
            return 'falling'
        else:
            return 'stable'
    
    def aggregate_all_trends(self) -> Dict[str, Any]:
        """Aggregate trends from all platforms"""
        print("\n" + "="*60)
        print("🚀 AGGREGATING TRENDS FROM ALL PLATFORMS")
        print("="*60)
        
        results = {
            'timestamp': datetime.now().isoformat(),
            'youtube': {},
            'reddit': {},
            'hackernews': {},
            'google_trends': {},
            'global_keywords': []
        }
        
        # Collect from each platform
        try:
            results['youtube'] = self.get_youtube_trends()
        except Exception as e:
            print(f"❌ YouTube error: {e}")
            results['youtube'] = {'error': str(e)}
        
        try:
            results['reddit'] = self.get_reddit_trends()
        except Exception as e:
            print(f"❌ Reddit error: {e}")
            results['reddit'] = {'error': str(e)}
        
        try:
            results['hackernews'] = self.get_hackernews_trends()
        except Exception as e:
            print(f"❌ Hacker News error: {e}")
            results['hackernews'] = {'error': str(e)}
        
        try:
            results['google_trends'] = self.get_google_trends()
        except Exception as e:
            print(f"❌ Google Trends error: {e}")
            results['google_trends'] = {'error': str(e)}
        
        # Aggregate global keywords across all platforms
        all_keywords = []
        
        for platform in ['youtube', 'reddit', 'hackernews']:
            if 'top_keywords' in results[platform]:
                for kw in results[platform]['top_keywords']:
                    all_keywords.extend([kw['keyword']] * kw['count'])
        
        if all_keywords:
            global_keyword_counts = Counter(all_keywords)
            results['global_keywords'] = [
                {'keyword': k, 'count': v} 
                for k, v in global_keyword_counts.most_common(20)
            ]
        
        # Save to file
        self._save_results(results)
        
        print("\n✅ Trend aggregation complete!")
        return results
    
    def _save_results(self, results: Dict[str, Any]):
        """Save results to JSON file"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"trends_{timestamp}.json"
        filepath = os.path.join(Config.PROCESSED_DATA_DIR, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        # Also save as latest.json for easy access
        latest_path = os.path.join(Config.PROCESSED_DATA_DIR, 'latest.json')
        with open(latest_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 Results saved to: {filepath}")


if __name__ == '__main__':
    aggregator = TrendAggregator()
    results = aggregator.aggregate_all_trends()
    
    # Print summary
    print("\n" + "="*60)
    print("📊 TRENDS SUMMARY")
    print("="*60)
    
    if 'youtube' in results and 'videos' in results['youtube']:
        print(f"\n📺 YouTube: {len(results['youtube']['videos'])} trending videos")
    
    if 'reddit' in results and 'posts' in results['reddit']:
        print(f"👽 Reddit: {len(results['reddit']['posts'])} top posts")
    
    if 'hackernews' in results and 'stories' in results['hackernews']:
        print(f"🔶 Hacker News: {len(results['hackernews']['stories'])} top stories")
    
    if 'global_keywords' in results and results['global_keywords']:
        print("\n🔥 Top 5 Global Keywords:")
        for kw in results['global_keywords'][:5]:
            print(f"   • {kw['keyword']}: {kw['count']} mentions")

"""
Aggregator module to collect and analyze trending content from all platforms
"""
from collections import Counter
import re
from datetime import datetime

class TrendingAggregator:
    """Aggregate and analyze trending content from multiple platforms"""
    
    def __init__(self, collectors):
        """
        Initialize with collector instances
        collectors: dict with keys 'google', 'reddit', 'hackernews', 'youtube'
        """
        self.collectors = collectors
        self.trends_data = {}
    
    def extract_hashtags(self, text):
        """Extract hashtags from text"""
        if not text:
            return []
        hashtag_pattern = r'#\w+'
        return re.findall(hashtag_pattern, text.lower())
    
    def extract_keywords(self, text, min_length=4):
        """Extract potential keywords from text"""
        if not text:
            return []
        # Remove common words and extract meaningful keywords
        common_words = {'the', 'and', 'for', 'with', 'this', 'that', 'from', 'have', 'will', 'your', 'what', 'when', 'where', 'about'}
        words = re.findall(r'\b[a-z]{' + str(min_length) + r',}\b', text.lower())
        return [w for w in words if w not in common_words]
    
    def collect_google_trends(self, queries=['technology', 'artificial intelligence', 'crypto']):
        """Collect trending topics from Google Trends"""
        collector = self.collectors.get('google')
        if not collector:
            return None
        
        trends = []
        for query in queries:
            data = collector.get_interest_over_time(query)
            if data and 'interest_over_time' in data:
                timeline = data.get('interest_over_time', {}).get('timeline_data', [])
                if timeline:
                    latest = timeline[-1]
                    trends.append({
                        'query': query,
                        'interest': latest.get('values', [{}])[0].get('extracted_value', 0),
                        'date': latest.get('date', 'Unknown')
                    })
        
        # Sort by interest
        trends.sort(key=lambda x: x['interest'], reverse=True)
        return trends
    
    def collect_reddit_trends(self, subreddits=['technology', 'programming', 'startups'], limit=25):
        """Collect trending posts from Reddit"""
        collector = self.collectors.get('reddit')
        if not collector:
            return None
        
        all_posts = []
        hashtags = []
        keywords = []
        
        for subreddit in subreddits:
            posts = collector.get_hot_posts(subreddit, limit=limit)
            
            for post in posts:
                data = post.get('data', {})
                title = data.get('title', '')
                score = data.get('score', 0)
                comments = data.get('num_comments', 0)
                url = data.get('url', '')
                
                # Extract hashtags and keywords
                hashtags.extend(self.extract_hashtags(title))
                keywords.extend(self.extract_keywords(title))
                
                all_posts.append({
                    'platform': 'Reddit',
                    'subreddit': subreddit,
                    'title': title,
                    'score': score,
                    'comments': comments,
                    'engagement': score + comments,
                    'url': url
                })
        
        # Sort by engagement
        all_posts.sort(key=lambda x: x['engagement'], reverse=True)
        
        return {
            'posts': all_posts[:50],  # Top 50
            'trending_hashtags': Counter(hashtags).most_common(10),
            'trending_keywords': Counter(keywords).most_common(20)
        }
    
    def collect_hackernews_trends(self, limit=30):
        """Collect trending stories from Hacker News"""
        collector = self.collectors.get('hackernews')
        if not collector:
            return None
        
        stories = collector.get_top_stories_with_details(limit=limit)
        keywords = []
        
        processed_stories = []
        for story in stories:
            title = story.get('title', '')
            score = story.get('score', 0)
            comments = story.get('descendants', 0)
            url = story.get('url', '')
            
            # Extract keywords
            keywords.extend(self.extract_keywords(title))
            
            processed_stories.append({
                'platform': 'Hacker News',
                'title': title,
                'score': score,
                'comments': comments,
                'engagement': score + (comments * 2),  # Weight comments more
                'url': url
            })
        
        # Sort by engagement
        processed_stories.sort(key=lambda x: x['engagement'], reverse=True)
        
        return {
            'stories': processed_stories[:30],
            'trending_keywords': Counter(keywords).most_common(20)
        }
    
    def collect_youtube_trends(self, region='US', max_results=25):
        """Collect trending videos from YouTube"""
        collector = self.collectors.get('youtube')
        if not collector:
            return None
        
        data = collector.get_trending_videos(region_code=region, max_results=max_results)
        if not data or 'items' not in data:
            return None
        
        videos = []
        hashtags = []
        keywords = []
        
        for video in data.get('items', []):
            snippet = video.get('snippet', {})
            stats = video.get('statistics', {})
            
            title = snippet.get('title', '')
            channel = snippet.get('channelTitle', '')
            views = int(stats.get('viewCount', 0))
            likes = int(stats.get('likeCount', 0))
            comments = int(stats.get('commentCount', 0))
            video_id = video.get('id', '')
            
            # Extract hashtags and keywords
            description = snippet.get('description', '')
            hashtags.extend(self.extract_hashtags(title + ' ' + description))
            keywords.extend(self.extract_keywords(title))
            
            videos.append({
                'platform': 'YouTube',
                'title': title,
                'channel': channel,
                'views': views,
                'likes': likes,
                'comments': comments,
                'engagement': views + (likes * 10) + (comments * 5),
                'url': f'https://www.youtube.com/watch?v={video_id}'
            })
        
        # Sort by engagement
        videos.sort(key=lambda x: x['engagement'], reverse=True)
        
        return {
            'videos': videos[:25],
            'trending_hashtags': Counter(hashtags).most_common(10),
            'trending_keywords': Counter(keywords).most_common(20)
        }
    
    def aggregate_all_trends(self, **kwargs):
        """
        Collect trends from all platforms
        
        Returns a comprehensive dictionary with all trending data
        """
        print("🔄 Collecting trends from all platforms...")
        
        results = {
            'timestamp': datetime.now().isoformat(),
            'google_trends': None,
            'reddit': None,
            'hackernews': None,
            'youtube': None,
            'overall_keywords': [],
            'overall_hashtags': []
        }
        
        # Google Trends
        if 'google' in self.collectors:
            print("📊 Fetching Google Trends...")
            results['google_trends'] = self.collect_google_trends(
                queries=kwargs.get('google_queries', ['technology', 'AI', 'crypto'])
            )
        
        # Reddit
        if 'reddit' in self.collectors:
            print("👽 Fetching Reddit trends...")
            results['reddit'] = self.collect_reddit_trends(
                subreddits=kwargs.get('reddit_subs', ['technology', 'programming', 'startups']),
                limit=kwargs.get('reddit_limit', 25)
            )
        
        # Hacker News
        if 'hackernews' in self.collectors:
            print("🔶 Fetching Hacker News trends...")
            results['hackernews'] = self.collect_hackernews_trends(
                limit=kwargs.get('hn_limit', 30)
            )
        
        # YouTube
        if 'youtube' in self.collectors:
            print("🎥 Fetching YouTube trends...")
            results['youtube'] = self.collect_youtube_trends(
                region=kwargs.get('youtube_region', 'US'),
                max_results=kwargs.get('youtube_limit', 25)
            )
        
        # Aggregate overall keywords and hashtags
        all_keywords = []
        all_hashtags = []
        
        if results['reddit']:
            all_keywords.extend([kw for kw, _ in results['reddit'].get('trending_keywords', [])])
            all_hashtags.extend([ht for ht, _ in results['reddit'].get('trending_hashtags', [])])
        
        if results['hackernews']:
            all_keywords.extend([kw for kw, _ in results['hackernews'].get('trending_keywords', [])])
        
        if results['youtube']:
            all_keywords.extend([kw for kw, _ in results['youtube'].get('trending_keywords', [])])
            all_hashtags.extend([ht for ht, _ in results['youtube'].get('trending_hashtags', [])])
        
        results['overall_keywords'] = Counter(all_keywords).most_common(30)
        results['overall_hashtags'] = Counter(all_hashtags).most_common(15)
        
        print("✅ All trends collected!")
        
        return results
    
    def get_top_items_summary(self, aggregated_data, top_n=10):
        """
        Generate a summary of top items across all platforms
        """
        summary = {
            'top_reddit_posts': [],
            'top_hackernews_stories': [],
            'top_youtube_videos': [],
            'top_keywords': [],
            'top_hashtags': []
        }
        
        # Top Reddit posts
        if aggregated_data['reddit']:
            summary['top_reddit_posts'] = aggregated_data['reddit']['posts'][:top_n]
        
        # Top HN stories
        if aggregated_data['hackernews']:
            summary['top_hackernews_stories'] = aggregated_data['hackernews']['stories'][:top_n]
        
        # Top YouTube videos
        if aggregated_data['youtube']:
            summary['top_youtube_videos'] = aggregated_data['youtube']['videos'][:top_n]
        
        # Overall top keywords and hashtags
        summary['top_keywords'] = aggregated_data['overall_keywords'][:top_n]
        summary['top_hashtags'] = aggregated_data['overall_hashtags'][:top_n]
        
        return summary

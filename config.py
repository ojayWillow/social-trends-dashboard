import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Application configuration"""
    
    # API Keys
    YOUTUBE_API_KEY = os.getenv('YOUTUBE_API_KEY')
    SERPAPI_KEY = os.getenv('SERPAPI_KEY')
    APIFY_TOKEN = os.getenv('APIFY_TOKEN')
    
    # Database
    DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///social_media_dashboard.db')
    
    # App Settings
    DEBUG = os.getenv('DEBUG', 'True').lower() == 'true'
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    DATA_FETCH_INTERVAL = int(os.getenv('DATA_FETCH_INTERVAL', 3600))
    
    # API URLs
    YOUTUBE_API_BASE = 'https://www.googleapis.com/youtube/v3'
    REDDIT_API_BASE = 'https://www.reddit.com'
    HACKERNEWS_API_BASE = 'https://hacker-news.firebaseio.com/v0'
    SERPAPI_BASE = 'https://serpapi.com/search.json'
    APIFY_API_BASE = 'https://api.apify.com/v2'
    
    # Data Storage
    DATA_DIR = 'data'
    RAW_DATA_DIR = os.path.join(DATA_DIR, 'raw')
    PROCESSED_DATA_DIR = os.path.join(DATA_DIR, 'processed')
    
    # Tracked Niches
    NICHES = {
        'tech': ['ai', 'saas', 'startup', 'programming', 'tech'],
        'fitness': ['workout', 'gym', 'health', 'fitness', 'wellness'],
        'finance': ['crypto', 'stocks', 'trading', 'investing', 'defi'],
        'marketing': ['seo', 'ads', 'growth', 'marketing', 'content']
    }
    
    # Platforms
    PLATFORMS = ['youtube', 'instagram', 'tiktok', 'twitter', 'reddit', 'hackernews', 'google_trends']
    
    @classmethod
    def validate(cls):
        """Validate that all required config is present"""
        required = ['YOUTUBE_API_KEY', 'SERPAPI_KEY', 'APIFY_TOKEN']
        missing = [key for key in required if not getattr(cls, key)]
        
        if missing:
            raise ValueError(f"Missing required configuration: {', '.join(missing)}")
        
        return True

# Validate config on import
if __name__ == '__main__':
    Config.validate()
    print("✅ Configuration validated successfully!")

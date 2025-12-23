import streamlit as st
import json
import os
from datetime import datetime
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from collections import Counter
import re
from config import Config

# Page configuration
st.set_page_config(
    page_title="🚀 Social Trends - Niche Explorer",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
    
    * {
        font-family: 'Inter', sans-serif;
    }
    
    .main-header {
        font-size: 3.5rem;
        font-weight: 700;
        text-align: center;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        padding: 2rem 0 1rem 0;
        margin-bottom: 0;
    }
    
    .subtitle {
        text-align: center;
        color: #666;
        font-size: 1.2rem;
        margin-bottom: 2rem;
    }
    
    .niche-selector {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 15px;
        color: white;
        margin: 2rem 0;
    }
    
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 12px;
        color: white;
        text-align: center;
        box-shadow: 0 8px 16px rgba(0,0,0,0.1);
        transition: transform 0.3s ease;
    }
    
    .metric-card:hover {
        transform: translateY(-5px);
    }
    
    .platform-card {
        background: white;
        border: 2px solid #f0f0f0;
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 4px 8px rgba(0,0,0,0.05);
    }
    
    .trend-item {
        background: linear-gradient(to right, #f8f9fa, #ffffff);
        padding: 1.2rem;
        margin: 0.8rem 0;
        border-radius: 10px;
        border-left: 4px solid #667eea;
        transition: all 0.3s ease;
    }
    
    .trend-item:hover {
        box-shadow: 0 6px 12px rgba(102, 126, 234, 0.15);
        transform: translateX(5px);
    }
    
    .hashtag-badge {
        display: inline-block;
        padding: 0.4rem 1rem;
        margin: 0.3rem;
        background: linear-gradient(135deg, #667eea, #764ba2);
        color: white;
        border-radius: 25px;
        font-size: 0.9rem;
        font-weight: 600;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    .video-embed {
        border-radius: 12px;
        overflow: hidden;
        box-shadow: 0 8px 16px rgba(0,0,0,0.1);
        margin: 1rem 0;
    }
    
    .cross-platform-match {
        background: linear-gradient(135deg, #ffeaa7 0%, #fdcb6e 100%);
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
        border-left: 5px solid #f39c12;
    }
    
    .engagement-bar {
        background: #e0e0e0;
        border-radius: 10px;
        overflow: hidden;
        height: 25px;
        margin: 0.5rem 0;
    }
    
    .engagement-fill {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        height: 100%;
        display: flex;
        align-items: center;
        justify-content: flex-end;
        padding-right: 10px;
        color: white;
        font-size: 0.8rem;
        font-weight: 600;
    }
    
    .stTabs [data-baseweb="tab-list"] {
        gap: 2rem;
    }
    
    .stTabs [data-baseweb="tab"] {
        height: 60px;
        padding: 0 2rem;
        background-color: #f8f9fa;
        border-radius: 10px 10px 0 0;
        font-weight: 600;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'selected_niche' not in st.session_state:
    st.session_state.selected_niche = 'tech'
if 'data' not in st.session_state:
    st.session_state.data = None
if 'cross_platform_trends' not in st.session_state:
    st.session_state.cross_platform_trends = []

# Define niches
NICHES = {
    'tech': {
        'name': '💻 Technology & AI',
        'keywords': ['ai', 'machine learning', 'tech', 'saas', 'startup', 'coding', 'programming'],
        'emoji': '💻',
        'color': '#667eea'
    },
    'fitness': {
        'name': '💪 Fitness & Health',
        'keywords': ['fitness', 'workout', 'gym', 'health', 'wellness', 'exercise', 'nutrition'],
        'emoji': '💪',
        'color': '#ee5a6f'
    },
    'finance': {
        'name': '💰 Finance & Crypto',
        'keywords': ['crypto', 'bitcoin', 'stocks', 'trading', 'investing', 'defi', 'finance'],
        'emoji': '💰',
        'color': '#f39c12'
    },
    'marketing': {
        'name': '📊 Marketing & Business',
        'keywords': ['marketing', 'seo', 'content', 'growth', 'business', 'strategy', 'branding'],
        'emoji': '📊',
        'color': '#26de81'
    },
    'lifestyle': {
        'name': '✨ Lifestyle & Travel',
        'keywords': ['travel', 'lifestyle', 'fashion', 'food', 'photography', 'adventure'],
        'emoji': '✨',
        'color': '#fd79a8'
    },
    'gaming': {
        'name': '🎮 Gaming & Esports',
        'keywords': ['gaming', 'esports', 'twitch', 'gamer', 'game', 'streaming', 'console'],
        'emoji': '🎮',
        'color': '#a29bfe'
    }
}

# Header
st.markdown('<h1 class="main-header">🚀 Social Trends Niche Explorer</h1>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">Discover what\'s trending in your niche across YouTube, Reddit, Hacker News & Twitter</p>', unsafe_allow_html=True)

# Niche Selector
st.markdown('### 🎯 Select Your Niche')

cols = st.columns(6)
for idx, (niche_id, niche_info) in enumerate(NICHES.items()):
    with cols[idx]:
        if st.button(
            f"{niche_info['emoji']} {niche_info['name'].split()[1]}",
            key=niche_id,
            use_container_width=True,
            type='primary' if st.session_state.selected_niche == niche_id else 'secondary'
        ):
            st.session_state.selected_niche = niche_id
            st.rerun()

st.markdown('---')

# Sidebar
with st.sidebar:
    st.header('⚙️ Dashboard Controls')
    
    current_niche = NICHES[st.session_state.selected_niche]
    st.markdown(f"### Current Niche: {current_niche['emoji']} {current_niche['name'].split()[1]}")
    
    st.markdown('---')
    
    # Data fetch button
    if st.button('🔄 Fetch Trends for This Niche', type='primary', use_container_width=True):
        with st.spinner(f'Collecting {current_niche["name"]} trends...'):
            # Here you would call your collectors with niche-specific keywords
            st.info('Note: Connect your API keys in .env file to fetch real data')
            # Simulated data structure
            st.session_state.data = {
                'niche': st.session_state.selected_niche,
                'timestamp': datetime.now().isoformat()
            }
    
    st.markdown('---')
    
    # Platform filters
    st.subheader('🎯 Platforms')
    show_youtube = st.checkbox('📺 YouTube', value=True)
    show_reddit = st.checkbox('👽 Reddit', value=True)
    show_hackernews = st.checkbox('🔶 Hacker News', value=True)
    show_twitter = st.checkbox('🐦 Twitter/X', value=True)
    
    st.markdown('---')
    
    # Engagement filters
    st.subheader('📊 Filters')
    min_engagement = st.slider('Min Engagement', 0, 10000, 100)
    time_range = st.selectbox('Time Range', ['Today', 'This Week', 'This Month', 'All Time'])
    
    st.markdown('---')
    st.info('💡 Tip: Click on trend items to see cross-platform matches')

# Main content area
current_niche = NICHES[st.session_state.selected_niche]

# Display niche overview
st.markdown(f"## {current_niche['emoji']} {current_niche['name']} Trends")
st.markdown(f"**Tracking keywords:** {', '.join(current_niche['keywords'])}")

# Metrics row
col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.metric('📺 YouTube Videos', '125', '+12')
with col2:
    st.metric('👽 Reddit Posts', '89', '+8')
with col3:
    st.metric('🔶 HN Stories', '34', '+5')
with col4:
    st.metric('🐦 Tweets', '1.2K', '+156')
with col5:
    st.metric('🔥 Hot Topics', '23', '+3')

st.markdown('---')

# Cross-platform trending topics
st.markdown('### 🌐 Cross-Platform Trending Topics')
st.markdown('Topics trending across multiple platforms simultaneously')

cross_trends = [
    {'topic': 'GPT-4 Updates', 'platforms': ['📺', '👽', '🔶', '🐦'], 'score': 9.5},
    {'topic': 'New iPhone Release', 'platforms': ['📺', '👽', '🐦'], 'score': 8.7},
    {'topic': 'Startup Funding', 'platforms': ['👽', '🔶', '🐦'], 'score': 7.9},
]

for trend in cross_trends:
    col1, col2, col3 = st.columns([3, 1, 1])
    with col1:
        st.markdown(f"**{trend['topic']}**")
        st.caption(' '.join(trend['platforms']) + ' platforms')
    with col2:
        st.metric('Trend Score', f"{trend['score']}/10")
    with col3:
        if st.button('View Details', key=f"cross_{trend['topic']}"):
            st.session_state.selected_cross_trend = trend['topic']

st.markdown('---')

# Platform tabs
tab1, tab2, tab3, tab4 = st.tabs([
    '📺 YouTube',
    '👽 Reddit', 
    '🔶 Hacker News',
    '🐦 Twitter/X'
])

# YouTube Tab
with tab1:
    st.markdown('### Top Trending Videos in ' + current_niche['name'])
    
    # Sample video data
    videos = [
        {
            'title': 'Building AI Agents with GPT-4: Complete Tutorial',
            'channel': 'Tech With Tim',
            'views': 245000,
            'likes': 12500,
            'video_id': 'dQw4w9WgXcQ',
            'thumbnail': 'https://img.youtube.com/vi/dQw4w9WgXcQ/maxresdefault.jpg',
            'tags': ['AI', 'GPT-4', 'Tutorial', 'Python']
        },
        {
            'title': 'The Future of AI in 2025',
            'channel': 'Fireship',
            'views': 892000,
            'likes': 45000,
            'video_id': 'dQw4w9WgXcQ',
            'thumbnail': 'https://img.youtube.com/vi/dQw4w9WgXcQ/maxresdefault.jpg',
            'tags': ['AI', 'Future', 'Tech']
        }
    ]
    
    for i, video in enumerate(videos, 1):
        col1, col2 = st.columns([1, 2])
        
        with col1:
            # Video embed
            st.markdown(f'<div class="video-embed">', unsafe_allow_html=True)
            st.video(f"https://www.youtube.com/watch?v={video['video_id']}")
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"### {i}. {video['title']}")
            st.caption(f"🎥 {video['channel']}")
            
            col_a, col_b, col_c = st.columns(3)
            with col_a:
                st.metric('👁️ Views', f"{video['views']:,}")
            with col_b:
                st.metric('👍 Likes', f"{video['likes']:,}")
            with col_c:
                engagement_rate = (video['likes'] / video['views'] * 100)
                st.metric('📊 Engagement', f"{engagement_rate:.1f}%")
            
            # Tags
            tags_html = ' '.join([f'<span class="hashtag-badge">{tag}</span>' for tag in video['tags']])
            st.markdown(tags_html, unsafe_allow_html=True)
        
        st.markdown('---')

# Reddit Tab
with tab2:
    st.markdown('### Hot Posts in ' + current_niche['name'])
    
    posts = [
        {
            'title': 'I built an AI that codes for me and it\'s actually good',
            'subreddit': 'programming',
            'author': 'coder123',
            'score': 4500,
            'comments': 234,
            'url': 'https://reddit.com/r/programming',
            'hashtags': ['#AI', '#coding', '#automation']
        },
        {
            'title': 'Show HN: Open source alternative to GPT-4',
            'subreddit': 'MachineLearning',
            'author': 'ml_enthusiast',
            'score': 3200,
            'comments': 189,
            'url': 'https://reddit.com/r/MachineLearning',
            'hashtags': ['#opensource', '#AI', '#GPT']
        }
    ]
    
    for i, post in enumerate(posts, 1):
        st.markdown(f'<div class="trend-item">', unsafe_allow_html=True)
        
        col1, col2 = st.columns([4, 1])
        
        with col1:
            st.markdown(f"### {i}. {post['title']}")
            st.caption(f"r/{post['subreddit']} • u/{post['author']}")
            
            # Hashtags
            tags_html = ' '.join([f'<span class="hashtag-badge">{tag}</span>' for tag in post['hashtags']])
            st.markdown(tags_html, unsafe_allow_html=True)
        
        with col2:
            st.metric('⬆️', post['score'])
            st.caption(f"💬 {post['comments']} comments")
        
        # Engagement bar
        max_score = 5000
        fill_percent = min((post['score'] / max_score) * 100, 100)
        st.markdown(f"""
        <div class="engagement-bar">
            <div class="engagement-fill" style="width: {fill_percent}%">
                {post['score']} upvotes
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
        st.markdown('<br>', unsafe_allow_html=True)

# Hacker News Tab
with tab3:
    st.markdown('### Top Stories in ' + current_niche['name'])
    
    stories = [
        {
            'title': 'OpenAI releases GPT-5 with reasoning capabilities',
            'author': 'techguru',
            'score': 892,
            'comments': 456,
            'url': 'https://news.ycombinator.com'
        },
        {
            'title': 'Show HN: I made a CLI tool that optimizes your code with AI',
            'author': 'hacker42',
            'score': 567,
            'comments': 123,
            'url': 'https://news.ycombinator.com'
        }
    ]
    
    for i, story in enumerate(stories, 1):
        st.markdown(f'<div class="trend-item">', unsafe_allow_html=True)
        
        col1, col2 = st.columns([5, 1])
        
        with col1:
            st.markdown(f"### {i}. {story['title']}")
            st.caption(f"by {story['author']} • [{story['url']}]({story['url']})")
        
        with col2:
            st.metric('⬆️ Points', story['score'])
            st.caption(f"💬 {story['comments']}")
        
        st.markdown('</div>', unsafe_allow_html=True)
        st.markdown('<br>', unsafe_allow_html=True)

# Twitter Tab
with tab4:
    st.markdown('### Trending Tweets in ' + current_niche['name'])
    
    st.info('📌 Note: Connect Twitter/X collector (Apify) to see real tweets. Add APIFY_TOKEN to your .env file.')
    
    tweets = [
        {
            'text': 'Just tested GPT-5 and it\'s mind-blowing. The reasoning capabilities are on another level. 🤯 #AI #Tech',
            'username': 'techinfluencer',
            'name': 'Tech Influencer',
            'likes': 12500,
            'retweets': 3400,
            'replies': 567,
            'verified': True
        },
        {
            'text': 'Built my first AI agent today. It automated 3 hours of work in 10 minutes. The future is here. #AI #automation #coding',
            'username': 'developer_life',
            'name': 'Dev Life',
            'likes': 8900,
            'retweets': 2100,
            'replies': 234,
            'verified': False
        }
    ]
    
    for i, tweet in enumerate(tweets, 1):
        st.markdown(f'<div class="trend-item">', unsafe_allow_html=True)
        
        col1, col2 = st.columns([4, 1])
        
        with col1:
            verified_badge = '✅' if tweet['verified'] else ''
            st.markdown(f"**{tweet['name']}** {verified_badge} @{tweet['username']}")
            st.markdown(tweet['text'])
        
        with col2:
            st.metric('❤️', f"{tweet['likes']:,}")
            st.caption(f"🔁 {tweet['retweets']:,} • 💬 {tweet['replies']}")
        
        st.markdown('</div>', unsafe_allow_html=True)
        st.markdown('<br>', unsafe_allow_html=True)

st.markdown('---')

# Keyword Analysis Section
st.markdown('## 🔑 Keyword Analysis Across All Platforms')

# Sample keyword data
keywords_data = {
    'Keyword': ['AI', 'GPT-4', 'Machine Learning', 'Automation', 'Python', 'OpenAI', 'Neural Networks'],
    'YouTube': [145, 89, 67, 45, 123, 78, 34],
    'Reddit': [234, 156, 89, 67, 98, 134, 45],
    'HN': [89, 67, 45, 34, 56, 78, 23],
    'Twitter': [456, 345, 234, 189, 267, 345, 123]
}

df = pd.DataFrame(keywords_data)
df['Total'] = df[['YouTube', 'Reddit', 'HN', 'Twitter']].sum(axis=1)
df = df.sort_values('Total', ascending=False)

fig = go.Figure(data=[
    go.Bar(name='YouTube', x=df['Keyword'], y=df['YouTube'], marker_color='#FF0000'),
    go.Bar(name='Reddit', x=df['Keyword'], y=df['Reddit'], marker_color='#FF4500'),
    go.Bar(name='Hacker News', x=df['Keyword'], y=df['HN'], marker_color='#FF6600'),
    go.Bar(name='Twitter', x=df['Keyword'], y=df['Twitter'], marker_color='#1DA1F2')
])

fig.update_layout(
    title='Keyword Mentions Across Platforms',
    xaxis_title='Keywords',
    yaxis_title='Mentions',
    barmode='stack',
    height=500
)

st.plotly_chart(fig, use_container_width=True)

# Footer
st.markdown('---')
st.markdown("""
<div style='text-align: center; color: gray; padding: 2rem;'>
    <p><strong>🚀 Social Trends Niche Explorer</strong></p>
    <p>Real-time trend analysis across YouTube, Reddit, Hacker News & Twitter/X</p>
    <p style='font-size: 0.9rem; margin-top: 1rem;'>
        Powered by: YouTube Data API • Reddit JSON API • Hacker News API • Apify Twitter Scraper
    </p>
</div>
""", unsafe_allow_html=True)

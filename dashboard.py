import streamlit as st
import json
import os
from datetime import datetime
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from src.aggregator import TrendAggregator
from config import Config

# Page configuration
st.set_page_config(
    page_title="Social Media Trends Dashboard",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        padding: 1rem 0;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .platform-header {
        font-size: 1.8rem;
        font-weight: bold;
        margin-top: 2rem;
        margin-bottom: 1rem;
        padding: 0.5rem;
        border-left: 5px solid #667eea;
        padding-left: 1rem;
    }
    .trend-item {
        background: #f8f9fa;
        padding: 1rem;
        margin: 0.5rem 0;
        border-radius: 8px;
        border-left: 3px solid #667eea;
    }
    .keyword-badge {
        display: inline-block;
        padding: 0.3rem 0.8rem;
        margin: 0.2rem;
        background: #667eea;
        color: white;
        border-radius: 20px;
        font-size: 0.9rem;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'data' not in st.session_state:
    st.session_state.data = None
if 'last_update' not in st.session_state:
    st.session_state.last_update = None

# Header
st.markdown('<h1 class="main-header">🚀 Social Media Trends Dashboard</h1>', unsafe_allow_html=True)
st.markdown('---')

# Sidebar
with st.sidebar:
    st.header('⚙️ Settings')
    
    # Refresh button
    if st.button('🔄 Fetch Latest Trends', type='primary', use_container_width=True):
        with st.spinner('Collecting trends from all platforms...'):
            try:
                aggregator = TrendAggregator()
                st.session_state.data = aggregator.aggregate_all_trends()
                st.session_state.last_update = datetime.now()
                st.success('Trends updated successfully!')
            except Exception as e:
                st.error(f'Error fetching trends: {e}')
    
    # Load latest data button
    if st.button('💾 Load Saved Data', use_container_width=True):
        latest_path = os.path.join(Config.PROCESSED_DATA_DIR, 'latest.json')
        if os.path.exists(latest_path):
            with open(latest_path, 'r', encoding='utf-8') as f:
                st.session_state.data = json.load(f)
                st.session_state.last_update = datetime.fromisoformat(st.session_state.data.get('timestamp', datetime.now().isoformat()))
            st.success('Data loaded successfully!')
        else:
            st.warning('No saved data found. Click "Fetch Latest Trends" to collect new data.')
    
    st.markdown('---')
    
    # Platform filters
    st.subheader('🎯 Platform Filters')
    show_youtube = st.checkbox('YouTube', value=True)
    show_reddit = st.checkbox('Reddit', value=True)
    show_hackernews = st.checkbox('Hacker News', value=True)
    show_google = st.checkbox('Google Trends', value=True)
    
    st.markdown('---')
    
    # Display last update time
    if st.session_state.last_update:
        st.info(f'🕓 Last updated:\n{st.session_state.last_update.strftime("%Y-%m-%d %H:%M:%S")}')

# Main content
if st.session_state.data is None:
    st.info('👋 Welcome! Click "Fetch Latest Trends" or "Load Saved Data" to get started.')
    st.stop()

data = st.session_state.data

# Global metrics row
col1, col2, col3, col4 = st.columns(4)

with col1:
    yt_count = len(data.get('youtube', {}).get('videos', []))
    st.metric('📺 YouTube Videos', yt_count)

with col2:
    reddit_count = len(data.get('reddit', {}).get('posts', []))
    st.metric('👽 Reddit Posts', reddit_count)

with col3:
    hn_count = len(data.get('hackernews', {}).get('stories', []))
    st.metric('🔶 HN Stories', hn_count)

with col4:
    total_keywords = len(data.get('global_keywords', []))
    st.metric('🔑 Unique Keywords', total_keywords)

st.markdown('---')

# Global Keywords Section
st.markdown('<h2 class="platform-header">🌍 Global Trending Keywords</h2>', unsafe_allow_html=True)

if data.get('global_keywords'):
    # Create visualization
    keywords_df = pd.DataFrame(data['global_keywords'][:20])
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        fig = px.bar(
            keywords_df, 
            x='count', 
            y='keyword', 
            orientation='h',
            title='Top 20 Keywords Across All Platforms',
            labels={'count': 'Mentions', 'keyword': 'Keyword'},
            color='count',
            color_continuous_scale='Viridis'
        )
        fig.update_layout(height=600, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader('Top Keywords')
        for i, kw in enumerate(data['global_keywords'][:10], 1):
            st.markdown(f"**{i}. {kw['keyword']}** - {kw['count']} mentions")

st.markdown('---')

# YouTube Section
if show_youtube and 'youtube' in data and 'videos' in data['youtube']:
    st.markdown('<h2 class="platform-header">📺 YouTube Trending Videos</h2>', unsafe_allow_html=True)
    
    yt_data = data['youtube']
    
    # Metrics
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric('Total Videos Analyzed', yt_data.get('total_videos', 0))
    with col2:
        total_views = yt_data.get('total_views', 0)
        st.metric('Total Views', f"{total_views:,}")
    with col3:
        avg_views = total_views // yt_data.get('total_videos', 1) if yt_data.get('total_videos', 0) > 0 else 0
        st.metric('Avg Views per Video', f"{avg_views:,}")
    
    # Top videos
    st.subheader('🏆 Top 10 Trending Videos')
    
    for i, video in enumerate(yt_data['videos'][:10], 1):
        with st.container():
            col1, col2 = st.columns([3, 1])
            with col1:
                st.markdown(f"**{i}. {video['title']}**")
                st.caption(f"🎥 {video['channel']}")
                if video.get('tags'):
                    tags_html = ' '.join([f'<span class="keyword-badge">{tag}</span>' for tag in video['tags'][:5]])
                    st.markdown(tags_html, unsafe_allow_html=True)
            with col2:
                st.metric('👁️ Views', f"{video['views']:,}")
                st.caption(f"👍 {video['likes']:,} | 💬 {video['comments']:,}")
        st.markdown('---')
    
    # Keywords
    if yt_data.get('top_keywords'):
        st.subheader('🔑 Most Common Keywords in Titles')
        kw_df = pd.DataFrame(yt_data['top_keywords'][:10])
        fig = px.bar(kw_df, x='keyword', y='count', title='YouTube Title Keywords')
        st.plotly_chart(fig, use_container_width=True)

st.markdown('---')

# Reddit Section
if show_reddit and 'reddit' in data and 'posts' in data['reddit']:
    st.markdown('<h2 class="platform-header">👽 Reddit Hot Topics</h2>', unsafe_allow_html=True)
    
    reddit_data = data['reddit']
    
    # Metrics
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric('Total Posts Analyzed', reddit_data.get('total_posts', 0))
    with col2:
        st.metric('Subreddits', len(reddit_data.get('subreddits_analyzed', [])))
    with col3:
        total_score = sum(p['score'] for p in reddit_data['posts'])
        st.metric('Total Upvotes (Top 10)', f"{total_score:,}")
    
    # Create tabs for different views
    tab1, tab2, tab3 = st.tabs(['🔥 Hot Posts', '🔑 Keywords', '#️⃣ Hashtags'])
    
    with tab1:
        st.subheader('🏆 Top 10 Posts')
        for i, post in enumerate(reddit_data['posts'][:10], 1):
            with st.container():
                col1, col2 = st.columns([4, 1])
                with col1:
                    st.markdown(f"**{i}. {post['title']}**")
                    st.caption(f"r/{post['subreddit']} • u/{post['author']}")
                with col2:
                    st.metric('⬆️ Score', post['score'])
                    st.caption(f"💬 {post['comments']} comments")
            st.markdown('---')
    
    with tab2:
        if reddit_data.get('top_keywords'):
            kw_df = pd.DataFrame(reddit_data['top_keywords'][:15])
            fig = px.treemap(
                kw_df, 
                path=['keyword'], 
                values='count',
                title='Reddit Keywords Treemap'
            )
            st.plotly_chart(fig, use_container_width=True)
    
    with tab3:
        if reddit_data.get('top_hashtags'):
            st.subheader('Most Used Hashtags')
            for hashtag in reddit_data['top_hashtags'][:10]:
                st.markdown(f"**{hashtag['hashtag']}** - {hashtag['count']} times")
        else:
            st.info('No hashtags found in titles')

st.markdown('---')

# Hacker News Section
if show_hackernews and 'hackernews' in data and 'stories' in data['hackernews']:
    st.markdown('<h2 class="platform-header">🔶 Hacker News Top Stories</h2>', unsafe_allow_html=True)
    
    hn_data = data['hackernews']
    
    # Metrics
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric('Total Stories', hn_data.get('total_stories', 0))
    with col2:
        total_score = sum(s['score'] for s in hn_data['stories'])
        st.metric('Total Points', f"{total_score:,}")
    with col3:
        total_comments = sum(s['comments'] for s in hn_data['stories'])
        st.metric('Total Comments', f"{total_comments:,}")
    
    # Stories and keywords
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader('🏆 Top Stories')
        for i, story in enumerate(hn_data['stories'][:10], 1):
            with st.container():
                st.markdown(f"**{i}. {story['title']}**")
                st.caption(f"by {story['author']} • ⬆️ {story['score']} points • 💬 {story['comments']} comments")
                if story.get('url'):
                    st.caption(f"🔗 [{story['url']}]({story['url']})")
            st.markdown('---')
    
    with col2:
        if hn_data.get('top_keywords'):
            st.subheader('🔑 Top Keywords')
            for kw in hn_data['top_keywords'][:10]:
                st.markdown(f"**{kw['keyword']}** - {kw['count']}")

st.markdown('---')

# Google Trends Section
if show_google and 'google_trends' in data and 'trends' in data['google_trends']:
    st.markdown('<h2 class="platform-header">📊 Google Trends</h2>', unsafe_allow_html=True)
    
    gt_data = data['google_trends']
    
    if gt_data.get('trends'):
        trends_df = pd.DataFrame(gt_data['trends'])
        
        # Create visualization
        fig = go.Figure()
        
        colors = {'rising': 'green', 'falling': 'red', 'stable': 'gray'}
        
        for direction in ['rising', 'falling', 'stable']:
            filtered = trends_df[trends_df['trend_direction'] == direction]
            if not filtered.empty:
                fig.add_trace(go.Bar(
                    x=filtered['query'],
                    y=filtered['interest'],
                    name=direction.capitalize(),
                    marker_color=colors[direction]
                ))
        
        fig.update_layout(
            title='Search Interest by Query',
            xaxis_title='Query',
            yaxis_title='Interest Level',
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Details table
        st.subheader('Trend Details')
        for trend in gt_data['trends']:
            direction_emoji = {'rising': '📈', 'falling': '📉', 'stable': '➡️'}
            emoji = direction_emoji.get(trend['trend_direction'], '➡️')
            
            col1, col2, col3 = st.columns([2, 1, 1])
            with col1:
                st.markdown(f"**{trend['query']}**")
            with col2:
                st.metric('Interest', trend['interest'])
            with col3:
                st.markdown(f"{emoji} **{trend['trend_direction'].upper()}**")
            st.markdown('---')

# Footer
st.markdown('---')
st.markdown("""
<div style='text-align: center; color: gray; padding: 2rem;'>
    <p>🚀 Social Media Trends Dashboard | Built with Streamlit</p>
    <p>Data sources: YouTube, Reddit, Hacker News, Google Trends</p>
</div>
""", unsafe_allow_html=True)

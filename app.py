import streamlit as st
import requests
import time
import json
from datetime import datetime

# Page configuration
st.set_page_config(
    page_title="AI Storyteller Pro",
    page_icon="📖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================
# Helper Functions (Defined FIRST)
# ============================================================
def display_story(story, language, metadata, prompt):
    """Display the generated story with proper formatting"""
    
    st.markdown("---")
    
    # Success message
    st.markdown(f"""
    <div class="success-message">
        ✅ Story generated successfully!
    </div>
    """, unsafe_allow_html=True)
    
    # Metadata
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("📚 Language", "Urdu" if language == "urdu" else "English")
    with col2:
        st.metric("🎭 Genre", metadata.get('genre', 'General').capitalize())
    with col3:
        word_count = len(story.split())
        st.metric("📝 Words", word_count)
    with col4:
        st.metric("🎨 Temperature", f"{metadata.get('temperature', 0.85):.2f}")
    
    # Story display with proper formatting
    st.markdown("### 📖 Your Story")
    
    if language == "urdu":
        st.markdown(f"""
        <div class="story-container urdu-text">
            {story}
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class="story-container english-text">
            {story}
        </div>
        """, unsafe_allow_html=True)
    
    # Download button
    st.download_button(
        label="📥 Download Story as Text",
        data=story,
        file_name=f"story_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
        mime="text/plain",
        use_container_width=True
    )

# ============================================================
# Custom CSS
# ============================================================
st.markdown("""
<style>
    /* Main container styling */
    .main {
        padding: 0rem 1rem;
    }
    
    /* Story container with gradient border */
    .story-container {
        background: linear-gradient(145deg, #1e1e1e, #2d2d2d);
        padding: 30px;
        border-radius: 15px;
        border-left: 6px solid #ff6b6b;
        margin: 20px 0;
        line-height: 2;
        color: #e0e0e0;
        box-shadow: 0 8px 32px rgba(0,0,0,0.3);
    }
    
    /* Urdu text styling */
    .urdu-text {
        font-family: 'Noto Naskh Arabic', 'Arial', sans-serif;
        direction: rtl;
        font-size: 1.2em;
        line-height: 2.2;
        text-align: right;
    }
    
    /* English text styling */
    .english-text {
        font-family: 'Georgia', serif;
        font-size: 1.1em;
        line-height: 1.8;
        text-align: left;
    }
    
    /* Button styling */
    .stButton > button {
        background: linear-gradient(135deg, #ff6b6b, #ee5a24);
        color: white;
        font-weight: bold;
        border-radius: 10px;
        padding: 12px 30px;
        width: 100%;
        border: none;
        transition: all 0.3s ease;
    }
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 20px rgba(255,107,107,0.4);
    }
    
    /* Sidebar styling */
    .sidebar-content {
        background: #2d2d2d;
        padding: 20px;
        border-radius: 10px;
    }
    
    /* Success message */
    .success-message {
        background: linear-gradient(135deg, #00b894, #00a381);
        padding: 15px;
        border-radius: 10px;
        color: white;
        font-weight: bold;
        text-align: center;
        margin: 10px 0;
    }
    
    /* Metadata box */
    .metadata-box {
        background: #2d2d2d;
        padding: 15px;
        border-radius: 10px;
        border: 1px solid #4a4a4a;
        margin: 10px 0;
    }
    
    /* Divider */
    hr {
        border: 0;
        height: 2px;
        background: linear-gradient(to right, #ff6b6b, transparent);
        margin: 30px 0;
    }
    
    /* Warning and info boxes */
    .stAlert {
        border-radius: 10px;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================
# Session State Initialization
# ============================================================
if 'generated_stories' not in st.session_state:
    st.session_state.generated_stories = []
if 'current_story' not in st.session_state:
    st.session_state.current_story = None
if 'api_url' not in st.session_state:
    st.session_state.api_url = ""
if 'prompt_input' not in st.session_state:
    st.session_state.prompt_input = ""

# ============================================================
# Sidebar Configuration
# ============================================================
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/000000/storybook.png", width=80)
    st.title("📖 Storyteller Pro")
    st.markdown("---")
    
    # API Endpoint Configuration
    st.subheader("🔗 API Configuration")
    
    # Manual API endpoint input
    api_url_input = st.text_input(
        "API Endpoint URL",
        value=st.session_state.api_url,
        placeholder="https://your-url.trycloudflare.com",
        help="Paste your Cloudflare/ngrok URL here"
    )
    
    if api_url_input:
        st.session_state.api_url = api_url_input.rstrip('/')
    
    # Connection status
    if st.session_state.api_url:
        try:
            test_response = requests.get(f"{st.session_state.api_url}/health", timeout=5)
            if test_response.status_code == 200:
                st.success("✅ Connected to API")
            else:
                st.warning("⚠️ API responding but may be unhealthy")
        except:
            st.error("❌ Cannot connect to API")
    
    st.markdown("---")
    
    # Story Settings
    st.subheader("⚙️ Story Settings")
    
    # Language Selection
    language = st.selectbox(
        "🌐 Language",
        ["english", "urdu"],
        format_func=lambda x: "English" if x == "english" else "اردو",
        help="Select story language"
    )
    
    # Genre Selection with emojis
    genres = {
        "general": "📝 General",
        "fantasy": "🐉 Fantasy",
        "scifi": "🚀 Sci-Fi",
        "mystery": "🔍 Mystery",
        "romance": "❤️ Romance",
        "adventure": "🗺️ Adventure",
        "horror": "👻 Horror"
    }
    
    genre = st.selectbox(
        "🎭 Genre",
        list(genres.keys()),
        format_func=lambda x: genres[x]
    )
    
    # Story Length
    story_length = st.select_slider(
        "📏 Story Length",
        options=["short", "medium", "long", "epic"],
        value="medium",
        format_func=lambda x: {
            "short": "Short (300-500 words)",
            "medium": "Medium (500-1000 words)",
            "long": "Long (1000-2000 words)",
            "epic": "Epic (2000+ words)"
        }[x]
    )
    
    # Creativity
    temperature = st.slider(
        "🎨 Creativity",
        min_value=0.1,
        max_value=1.5,
        value=0.85,
        step=0.05,
        help="Higher = more creative, Lower = more focused"
    )
    
    # Max tokens based on story length
    token_map = {
        "short": 512,
        "medium": 1024,
        "long": 2048,
        "epic": 3072
    }
    max_tokens = token_map[story_length]
    
    st.info(f"📊 Max Tokens: {max_tokens}")
    
    st.markdown("---")
    
    # Example Prompts
    st.subheader("💡 Quick Prompts")
    
    example_prompts = {
        "english": [
            "A young wizard discovers an ancient prophecy",
            "A detective who can see ghosts solves crimes",
            "A time traveler stranded in medieval times",
            "A robot learning to paint and express emotions",
            "A girl who travels through dreams",
            "A magical library where books come alive"
        ],
        "urdu": [
            "ایک نوجوان جادوگر جو ایک قدیم پیشین گوئی دریافت کرتا ہے",
            "ایک جاسوس جو بھوت دیکھ سکتا ہے",
            "ایک وقت کا مسافر جو قرون وسطی میں پھنس گیا",
            "ایک روبوٹ جو پینٹ کرنا سیکھتا ہے",
            "ایک لڑکی جو خوابوں میں سفر کرتی ہے",
            "ایک جادوئی لائبریری جہاں کتابیں زندہ ہو جاتی ہیں"
        ]
    }
    
    for prompt in example_prompts.get(language, example_prompts["english"])[:4]:
        if st.button(f"📌 {prompt[:30]}...", key=f"example_{prompt}"):
            st.session_state.prompt_input = prompt
    
    st.markdown("---")
    
    # Story History
    st.subheader("📚 Story History")
    if st.session_state.generated_stories:
        st.write(f"Total stories: {len(st.session_state.generated_stories)}")
        if st.button("🗑️ Clear History"):
            st.session_state.generated_stories = []
            st.rerun()
    else:
        st.caption("No stories generated yet")

# ============================================================
# Main Content Area
# ============================================================
st.title("📖 AI Storyteller Pro")
st.markdown("Generate **long, detailed stories** in English or Urdu")

# Check API connection
if not st.session_state.api_url:
    st.warning("⚠️ Please enter your API endpoint URL in the sidebar")
    st.stop()

# Main input
st.subheader("✍️ Story Idea")
prompt = st.text_area(
    "Enter your story idea",
    value=st.session_state.get('prompt_input', ''),
    placeholder="Example: A young wizard discovers an ancient prophecy that could destroy the world...",
    height=120
)

# Generate options in columns
col1, col2, col3 = st.columns([1, 1, 1])
with col1:
    generate_button = st.button("🚀 Generate Story", use_container_width=True)
with col2:
    if st.button("🔄 Regenerate", use_container_width=True) and st.session_state.current_story:
        # Reuse last prompt
        if st.session_state.generated_stories:
            last_prompt = st.session_state.generated_stories[-1].get('prompt', '')
            prompt = last_prompt
            generate_button = True
with col3:
    if st.button("📥 Download Story", use_container_width=True) and st.session_state.current_story:
        story_text = st.session_state.current_story
        st.download_button(
            label="📥 Download as Text",
            data=story_text,
            file_name=f"story_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
            mime="text/plain"
        )

# ============================================================
# Generation Logic
# ============================================================
if generate_button and prompt:
    with st.spinner("📝 Crafting your story... (This may take 1-2 minutes for long stories)"):
        try:
            # Prepare payload
            payload = {
                "prompt": prompt,
                "max_tokens": max_tokens,
                "temperature": temperature,
                "genre": genre,
                "story_length": story_length,
                "language": language
            }
            
            # Show progress
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            status_text.text("🔄 Connecting to API...")
            progress_bar.progress(20)
            
            # Make API request
            start_time = time.time()
            response = requests.post(
                f"{st.session_state.api_url}/generate",
                json=payload,
                timeout=300
            )
            
            progress_bar.progress(80)
            status_text.text("📝 Processing story...")
            
            if response.status_code == 200:
                data = response.json()
                story = data.get("generated_text", "")
                metadata = data.get("metadata", {})
                
                # If story is still short, try the long endpoint
                if len(story.split()) < 100 and story_length in ["long", "epic"]:
                    status_text.text("📖 Generating longer version...")
                    try:
                        long_response = requests.post(
                            f"{st.session_state.api_url}/generate_long",
                            json={
                                "prompt": prompt,
                                "temperature": temperature,
                                "genre": genre,
                                "language": language
                            },
                            timeout=300
                        )
                        if long_response.status_code == 200:
                            long_data = long_response.json()
                            long_story = long_data.get("generated_text", "")
                            if len(long_story.split()) > len(story.split()):
                                story = long_story
                                metadata = long_data.get("metadata", metadata)
                    except:
                        pass  # Keep original story if long endpoint fails
                
                progress_bar.progress(100)
                status_text.text(f"✅ Story generated in {int(time.time() - start_time)} seconds!")
                
                # Store in session
                st.session_state.current_story = story
                st.session_state.generated_stories.append({
                    'prompt': prompt,
                    'story': story,
                    'timestamp': datetime.now(),
                    'language': language,
                    'genre': genre,
                    'length': story_length
                })
                
                # Display the story
                display_story(story, language, metadata, prompt)
                
            else:
                st.error(f"❌ API Error: {response.status_code}")
                st.text(response.text[:500])  # Show first 500 chars of error
                
        except requests.exceptions.Timeout:
            st.error("⏰ Request timed out. Try with a shorter story length.")
        except requests.exceptions.ConnectionError:
            st.error("🔌 Cannot connect to API. Check your URL and network.")
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")
            
elif generate_button and not prompt:
    st.warning("⚠️ Please enter a story idea first!")

# ============================================================
# Display History
# ============================================================
if st.session_state.generated_stories:
    st.markdown("---")
    st.subheader("📚 Story History")
    
    for idx, story_data in enumerate(reversed(st.session_state.generated_stories[-5:])):
        with st.expander(f"📖 Story {len(st.session_state.generated_stories) - idx} - {story_data.get('timestamp', datetime.now()).strftime('%Y-%m-%d %H:%M')}"):
            st.caption(f"**Prompt:** {story_data.get('prompt', '')}")
            st.caption(f"**Language:** {story_data.get('language', 'english')} | **Genre:** {story_data.get('genre', 'general')}")
            
            story_text = story_data.get('story', '')
            if story_data.get('language') == 'urdu':
                st.markdown(f'<div class="urdu-text">{story_text}</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="english-text">{story_text}</div>', unsafe_allow_html=True)
            
            if st.button(f"📋 Copy Story {len(st.session_state.generated_stories) - idx}", key=f"copy_{idx}"):
                st.code(story_text, language='text')

# ============================================================
# Footer
# ============================================================
st.markdown("---")
st.caption("""
⚡ Powered by **Storyteller-Llama3-GGUF** • Hosted on Kaggle with Cloudflare Tunnel  
📚 Supports **English** and **Urdu** • Stories up to **3000+ tokens**
""")

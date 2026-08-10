import streamlit as st
from openai import OpenAI

st.set_page_config(page_title="Llama 3.1 Storyteller", page_icon="🔮", layout="centered")
st.title("🔮 Storyteller Llama 3.1 AI")
st.subheader("Fine-Tuned Adapter + Free Serverless OpenAI Pipeline")

# 1. Verification of the Streamlit Secrets Token
if "HF_TOKEN" not in st.secrets:
    st.error("Missing token entry! Go to Streamlit Dashboard -> Advanced Settings -> Secrets and add: HF_TOKEN = 'your_token'")
    st.stop()

HF_TOKEN = st.secrets["HF_TOKEN"]

# 2. Configure the client using Hugging Face's official OpenAI-compatible gateway
@st.cache_resource
def get_ai_client():
    return OpenAI(
        base_url="https://huggingface.co",
        api_key=HF_TOKEN
    )

client = get_ai_client()

# 3. User Interface View Elements
user_prompt = st.text_area("Provide a prompt or seed for your custom story:", "Deep inside an ancient forest, a mysterious door appeared...")
max_tokens = st.slider("Maximum Generation Length (Tokens)", min_value=50, max_value=500, value=200, step=50)

if st.button("Unleash the Storyteller"):
    if not user_prompt.strip():
        st.warning("Please input text first.")
    else:
        # Visual anchor loader indicator
        with st.spinner("Connecting to the serverless cluster..."):
            try:
                # Swapped to a standard non-streaming request to safely capture cold-start locks
                response = client.chat.completions.create(
                    model="UH32/Storyteller-Llama3", 
                    messages=[{"role": "user", "content": user_prompt}],
                    max_tokens=max_tokens,
                    stream=False  
                )
                
                # Extract out response text sequences successfully 
                story_text = response.choices[0].message.content
                
                if story_text:
                    st.success("✨ Your Custom Story:")
                    st.write(story_text)
                else:
                    st.warning("The model responded with empty text. Try a different prompt.")
                        
            except Exception as e:
                error_str = str(e).lower()
                # Safely catch the free-tier model wakeup behavior
                if "loading" in error_str or "estimated time" in error_str or "423" in error_str:
                    st.info("🎯 Hugging Face is mounting your adapter to the base weights in its GPU cluster. Please wait 45 seconds and click unleash again!")
                else:
                    st.error(f"Pipeline System Error: {e}")

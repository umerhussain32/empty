import streamlit as st
from huggingface_hub import InferenceClient

st.set_page_config(page_title="Llama 3.1 Storyteller", page_icon="🔮", layout="centered")
st.title("🔮 Storyteller Llama 3.1 AI")
st.subheader("Fine-tuned Adapter + Free Serverless API")

# 1. Safely load your token from secrets
if "HF_TOKEN" not in st.secrets:
    st.error("Missing HF_TOKEN inside Streamlit Secrets!")
    st.stop()

HF_TOKEN = st.secrets["HF_TOKEN"]

# 2. Use the stable InferenceClient which handles DNS routing internally
MODEL_ID = "UH32/Storyteller-Llama3"

@st.cache_resource
def get_inference_client(token):
    return InferenceClient(token=token)

client = get_inference_client(HF_TOKEN)

# 3. Create the UI interface layout
user_prompt = st.text_area("Provide a prompt or seed for your custom story:", "Deep inside an ancient forest, a mysterious door appeared...")
max_tokens = st.slider("Maximum Generation Length (Tokens)", min_value=50, max_value=1000, value=250, step=50)

if st.button("Unleash the Storyteller"):
    if not user_prompt.strip():
        st.warning("Please input some text to give the storyteller direction.")
    else:
        with st.spinner("Hugging Face API is generating your story using cloud GPUs..."):
            
            # Format standard Llama 3.1 Prompt Template formatting structure
            formatted_prompt = f"<|begin_of_text|><|start_header_id|>user<|end_header_id|>\n\n{user_prompt}<|eot_id|><|start_header_id|>assistant<|end_header_id|>\n\n"
            
            try:
                # Use the dedicated text_generation pipeline to force the correct routing
                story_text = client.text_generation(
                    prompt=formatted_prompt,
                    model=MODEL_ID,
                    max_new_tokens=max_tokens,
                    stop=["<|eot_id|>", "<|end_of_text|>"]
                )
                
                if story_text:
                    st.success("✨ Your Custom Story:")
                    st.write(story_text)
                else:
                    st.warning("API returned an empty text string response.")
                    
            except Exception as e:
                error_str = str(e).lower()
                # Catch and explain the free-tier cold start warming cycle safely
                if "loading" in error_str or "estimated time" in error_str:
                    st.info("🎯 Hugging Face is mounting your adapter to Meta's Llama 3.1 base weights. Please wait 45 seconds and click the button again!")
                else:
                    st.error(f"HF System Message: {e}")

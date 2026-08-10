import streamlit as st
from huggingface_hub import hf_hub_download
from llama_cpp import Llama
import os

st.set_page_config(page_title="Llama 3.1 Storyteller", page_icon="🔮", layout="centered")
st.title("🔮 Storyteller Llama 3.1 AI")
st.subheader("Running 100% Free locally on Streamlit CPU via GGUF")

# 1. Download the GGUF file from your Hugging Face repo into the server cache
@st.cache_resource
def load_storyteller_model():
    with st.spinner("Downloading GGUF model (~4.8GB) from Hugging Face... This takes 1-2 minutes on the very first load."):
        model_path = hf_hub_download(
            repo_id="UH32/Storyteller-Llama3-GGUF", 
            filename="Storyteller-Llama3-Q4_K_M.gguf" # Verify exact name from your hub files
        )
    with st.spinner("Loading model into server memory..."):
        # n_ctx sets text limit, n_threads optimizes for Streamlit free CPU cores
        llm = Llama(model_path=model_path, n_ctx=1024, n_threads=2)
    return llm

try:
    llm = load_storyteller_model()
    st.success("The Storyteller is ready!")
except Exception as e:
    st.error(f"Failed to initialize model: {e}")
    st.stop()

# 2. UI Layout
user_prompt = st.text_area("Provide a prompt or seed for your custom story:", "Deep inside an ancient forest, a mysterious door appeared...")
max_tokens = st.slider("Maximum Generation Length (Tokens)", min_value=50, max_value=500, value=200, step=50)

if st.button("Unleash the Storyteller"):
    if not user_prompt.strip():
        st.warning("Please input text first.")
    else:
        with st.spinner("The Storyteller is writing your piece... (CPU generation takes a brief moment)"):
            try:
                # Format standard Llama 3.1 Prompt structure
                formatted_prompt = f"<|begin_of_text|><|start_header_id|>user<|end_header_id|>\n\n{user_prompt}<|eot_id|><|start_header_id|>assistant<|end_header_id|>\n\n"
                
                # Execute CPU local inference
                output = llm(
                    formatted_prompt,
                    max_tokens=max_tokens,
                    stop=["<|eot_id|>", "<|end_of_text|>"],
                    echo=False
                )
                
                story_text = output['choices'][0]['text']
                st.success("✨ Your Custom Story:")
                st.write(story_text)
                
            except Exception as e:
                st.error(f"Generation Error: {e}")

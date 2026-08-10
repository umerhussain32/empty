import streamlit as st
import requests

st.set_page_config(page_title="Llama 3.1 Storyteller", page_icon="🔮", layout="centered")
st.title("🔮 Storyteller Llama 3.1 AI")
st.subheader("Fine-Tuned GGUF + Modern Serverless API Router")

# 1. Verification of the Streamlit Secrets Token
if "HF_TOKEN" not in st.secrets:
    st.error("Missing token entry! Go to Streamlit Dashboard -> Advanced Settings -> Secrets and add: HF_TOKEN = 'your_token'")
    st.stop()

HF_TOKEN = st.secrets["HF_TOKEN"]

# 2. FIXED: Using the active, modern Hugging Face Router endpoint surface
API_URL = "https://huggingface.co"
headers = {"Authorization": f"Bearer {HF_TOKEN}"}

# 3. User Interface View Elements
user_prompt = st.text_area("Provide a prompt or seed for your custom story:", "Deep inside an ancient forest, a mysterious door appeared...")
max_tokens = st.slider("Maximum Generation Length (Tokens)", min_value=50, max_value=500, value=200, step=50)

if st.button("Unleash the Storyteller"):
    if not user_prompt.strip():
        st.warning("Please input text first.")
    else:
        with st.spinner("The modern router cluster is running the model query..."):
            
            # Format standard Llama 3.1 Prompt structure
            formatted_prompt = f"<|begin_of_text|><|start_header_id|>user<|end_header_id|>\n\n{user_prompt}<|eot_id|><|start_header_id|>assistant<|end_header_id|>\n\n"
            
            payload = {
                "inputs": formatted_prompt,
                "parameters": {
                    "max_new_tokens": max_tokens,
                    "return_full_text": False,
                    "stop": ["<|eot_id|>", "<|end_of_text|>"]
                }
            }
            
            try:
                # Direct HTTP Request post
                response = requests.post(API_URL, headers=headers, json=payload)
                
                # Check for standard server-side system blocks before decoding JSON
                if response.status_code != 200:
                    st.error(f"Server Connection Issue (HTTP {response.status_code}): {response.text}")
                else:
                    result = response.json()
                    
                    # Check for server loading queues
                    if isinstance(result, dict) and "error" in result:
                        error_msg = result["error"]
                        if "loading" in error_msg.lower():
                            st.info("🎯 The base Llama instance is initializing. Please wait 30 seconds and click unleash again!")
                        else:
                            st.error(f"Hugging Face Router Error: {error_msg}")
                            
                    # Extract response text successfully
                    elif isinstance(result, list) and len(result) > 0:
                        story_text = result[0].get("generated_text", "")
                        st.success("✨ Your Custom Story:")
                        st.write(story_text)
                    else:
                        st.error(f"Unexpected data payload returned: {result}")
                    
            except Exception as e:
                st.error(f"Pipeline Interface Error: {e}")

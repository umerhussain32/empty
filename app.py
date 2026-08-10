import streamlit as st
import requests

st.set_page_config(page_title="Llama 3.1 Storyteller", page_icon="🔮", layout="centered")
st.title("🔮 Storyteller Llama 3.1 AI")
st.subheader("Fine-Tuned GGUF + Free Serverless API Wrapper")

# 1. Verification of the Streamlit Secrets Token
if "HF_TOKEN" not in st.secrets:
    st.error("Missing token entry! Go to Streamlit Dashboard -> Advanced Settings -> Secrets and add: HF_TOKEN = 'your_token'")
    st.stop()

HF_TOKEN = st.secrets["HF_TOKEN"]

# 2. Hardcoded direct endpoint to prevent any concatenation string typos
API_URL = "https://huggingface.co"
headers = {"Authorization": f"Bearer {HF_TOKEN}"}

# 3. User Interface View Elements
user_prompt = st.text_area("Provide a prompt or seed for your custom story:", "Deep inside an ancient forest, a mysterious door appeared...")
max_tokens = st.slider("Maximum Generation Length (Tokens)", min_value=50, max_value=500, value=200, step=50)

if st.button("Unleash the Storyteller"):
    if not user_prompt.strip():
        st.warning("Please input text first.")
    else:
        with st.spinner("The serverless cluster is running your fine-tuned model..."):
            
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
                result = response.json()
                
                # Check for standard server-side system status returns
                if isinstance(result, dict) and "error" in result:
                    error_msg = result["error"]
                    if "loading" in error_msg.lower():
                        st.info("🎯 The Hugging Face serverless instance is waking up your GGUF file repository. Please wait 45 seconds and click generation again!")
                    else:
                        st.error(f"Hugging Face Core Error: {error_msg}")
                        
                # Extract out response text sequences successfully 
                elif isinstance(result, list) and len(result) > 0:
                    # Target list element structure correctly
                    story_text = result[0].get("generated_text", "")
                    st.success("✨ Your Custom Story:")
                    st.write(story_text)
                else:
                    st.error(f"Unexpected data payload signature received: {result}")
                    
            except Exception as e:
                st.error(f"Network Pipeline Error: {e}")

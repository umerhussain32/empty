import streamlit as st
import requests

st.set_page_config(page_title="Llama 3.1 Storyteller", page_icon="🔮", layout="centered")
st.title("🔮 Storyteller Llama 3.1 AI")
st.subheader("Fine-tuned Adapter + Free Serverless API")

# 1. Safely load your token
if "HF_TOKEN" not in st.secrets:
    st.error("Missing HF_TOKEN inside Streamlit Secrets!")
    st.stop()

HF_TOKEN = st.secrets["HF_TOKEN"]

# 2. Configure endpoint URLs
MODEL_ID = "UH32/Storyteller-Llama3"
API_URL = f"https://huggingface.co{MODEL_ID}"
headers = {"Authorization": f"Bearer {HF_TOKEN}"}

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
            
            payload = {
                "inputs": formatted_prompt,
                "parameters": {
                    "max_new_tokens": max_tokens,
                    "return_full_text": False,
                    "stop": ["<|eot_id|>", "<|end_of_text|>"]
                }
            }
            
            try:
                # Direct HTTP request for more verbose error capture
                response = requests.post(API_URL, headers=headers, json=payload)
                result = response.json()
                
                # Handle dictionary format errors (like cold starts)
                if isinstance(result, dict) and "error" in result:
                    error_msg = result["error"]
                    if "loading" in error_msg.lower():
                        st.info("🎯 Hugging Face is mounting your adapter to Meta's Llama 3.1 base weights. Please wait 45 seconds and click the button again!")
                    else:
                        st.error(f"HF System Message: {error_msg}")
                        
                # Handle successful generation response array
                elif isinstance(result, list) and len(result) > 0:
                    story_text = result[0].get("generated_text", "")
                    st.success("✨ Your Custom Story:")
                    st.write(story_text)
                else:
                    st.error(f"Unexpected API Format received: {result}")
                    
            except Exception as e:
                st.error(f"Network Connection Error: {e}")

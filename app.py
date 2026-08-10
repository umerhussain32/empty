import streamlit as st
from huggingface_hub import InferenceClient

st.set_page_config(page_title="Llama 3.1 Storyteller", page_icon="🔮", layout="centered")
st.title("🔮 Storyteller Llama 3.1 AI")
st.subheader("Fine-tuned Adapter + Free Serverless API")

# 1. Load your Hugging Face Token from Streamlit Cloud Secrets
HF_TOKEN = st.secrets["HF_TOKEN"]

# 2. Setup your adapter repo location
MODEL_ID = "UH32/Storyteller-Llama3"
client = InferenceClient(model=MODEL_ID, token=HF_TOKEN)

# 3. Create the UI interface layout
user_prompt = st.text_area("Provide a prompt or seed for your custom story:", "Deep inside an ancient forest, a mysterious door appeared...")
max_tokens = st.slider("Maximum Generation Length (Tokens)", min_value=50, max_value=1000, value=250, step=50)

if st.button("Unleash the Storyteller"):
    if not user_prompt.strip():
        st.warning("Please input some text to give the storyteller direction.")
    else:
        with st.spinner("Hugging Face API is generating your story using cloud GPUs..."):
            try:
                # Standard Llama 3.1 Prompt Template formatting structure
                formatted_prompt = f"<|begin_of_text|><|start_header_id|>user<|end_header_id|>\n\n{user_prompt}<|eot_id|><|start_header_id|>assistant<|end_header_id|>\n\n"
                
                # Make the serverless request
                response = client.text_generation(
                    formatted_prompt, 
                    max_new_tokens=max_tokens,
                    stop=["<|eot_id|>", "<|end_of_text|>"]
                )
                
                st.success("✨ Your Custom Story:")
                st.write(response)
                
            except Exception as e:
                # Catch and explain the free-tier cold start warming cycle
                if "loading" in str(e).lower():
                    st.info("Hugging Face is currently downloading the base Llama 3.1 weights and attaching your adapter. Please wait 45 seconds and click the button again!")
                else:
                    st.error(f"API Error Encountered: {e}")

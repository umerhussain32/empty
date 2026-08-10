import streamlit as st
from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline

st.set_page_config(page_title="Llama 3.1 Storyteller", page_icon="🔮", layout="centered")
st.title("🔮 Storyteller Llama 3.1 AI")
st.subheader("Running 100% Free locally via Transformers GGUF")

# 1. Download and CACHE the model using Streamlit's cloud data
@st.cache_resource
def load_transformers_gguf():
    # Pass the repository name directly to from_pretrained instead of downloading via hf_hub_download
    repo_id = "UH32/Storyteller-Llama3-GGUF"
    gguf_filename = "llama-3.1-8b.Q4_K_M.gguf"
    
    with st.spinner("Downloading and loading GGUF weights directly to Streamlit Cloud memory... (Takes 1-2 mins on first load, uses 0% of your data)"):
        # Explicitly configure transformers to fetch and load the GGUF file
        model = AutoModelForCausalLM.from_pretrained(
            repo_id,
            gguf_file=gguf_filename,
            device_map="cpu"
        )
        
        # Load a standard matching tokenizer to parse the text correctly
        tokenizer = AutoTokenizer.from_pretrained("meta-llama/Llama-3.1-8B-Instruct")
        
        # Build the local generation text pipeline
        pipe = pipeline("text-generation", model=model, tokenizer=tokenizer)
    return pipe

try:
    story_pipeline = load_transformers_gguf()
    st.success("The Cloud Storyteller is permanently cached and ready!")
except Exception as e:
    st.error(f"Failed to initialize model: {e}")
    st.stop()

# 2. UI Layout Setup
user_prompt = st.text_area("Provide a prompt or seed for your custom story:", "Deep inside an ancient forest, a mysterious door appeared...")
max_tokens = st.slider("Maximum Generation Length (Tokens)", min_value=50, max_value=500, value=200, step=50)

if st.button("Unleash the Storyteller"):
    if not user_prompt.strip():
        st.warning("Please input text first.")
    else:
        with st.spinner("The Storyteller is crafting your piece... (Processing via cloud CPU)"):
            try:
                # Format standard Llama 3.1 Prompt structure
                formatted_prompt = f"<|begin_of_text|><|start_header_id|>user<|end_header_id|>\n\n{user_prompt}<|eot_id|><|start_header_id|>assistant<|end_header_id|>\n\n"
                
                # Execute inference directly in server memory
                outputs = story_pipeline(
                    formatted_prompt,
                    max_new_tokens=max_tokens,
                    do_sample=True,
                    temperature=0.7,
                    top_p=0.9
                )
                
                # Extract and clean response text safely
                story_text = outputs[0]["generated_text"]
                clean_story = story_text.replace(formatted_prompt, "").strip()
                
                st.success("✨ Your Custom Story:")
                st.write(clean_story)
                
            except Exception as e:
                st.error(f"Generation Error: {e}")

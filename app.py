import streamlit as st
from huggingface_hub import hf_hub_download
from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline

st.set_page_config(page_title="Llama 3.1 Storyteller", page_icon="🔮", layout="centered")
st.title("🔮 Storyteller Llama 3.1 AI")
st.subheader("Running 100% Free locally via Transformers GGUF")

# 1. Download and cache the model using pure Python tools
@st.cache_resource
def load_transformers_gguf():
    with st.spinner("Downloading GGUF weights (~4.8GB)... This takes 1-2 minutes on first load."):
        # Download the file to local server cache
        model_file = hf_hub_download(
            repo_id="UH32/Storyteller-Llama3-GGUF", 
            filename="Storyteller-Llama3-Q4_K_M.gguf"
        )
    
    with st.spinner("Loading architecture into CPU memory..."):
        # Explicitly configure the model to load GGUF format natively
        model = AutoModelForCausalLM.from_pretrained(
            model_file,
            gguf=True,
            device_map="cpu"
        )
        # Load a standard matching Llama 3.1 tokenizer to decode words
        tokenizer = AutoTokenizer.from_pretrained("meta-llama/Llama-3.1-8B-Instruct")
        
        # Build text generation pipeline
        pipe = pipeline("text-generation", model=model, tokenizer=tokenizer)
    return pipe

try:
    story_pipeline = load_transformers_gguf()
    st.success("The Storyteller is ready!")
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
        with st.spinner("The Storyteller is crafting your piece... (CPU processing takes a moment)"):
            try:
                # Format standard Llama 3.1 Prompt structure
                formatted_prompt = f"<|begin_of_text|><|start_header_id|>user<|end_header_id|>\n\n{user_prompt}<|eot_id|><|start_header_id|>assistant<|end_header_id|>\n\n"
                
                # Execute inference
                outputs = story_pipeline(
                    formatted_prompt,
                    max_new_tokens=max_tokens,
                    do_sample=True,
                    temperature=0.7,
                    top_p=0.9
                )
                
                # Extract response text safely
                story_text = outputs[0]["generated_text"]
                # Clean up prompt prefix if visible
                clean_story = story_text.replace(formatted_prompt, "").strip()
                
                st.success("✨ Your Custom Story:")
                st.write(clean_story)
                
            except Exception as e:
                st.error(f"Generation Error: {e}")

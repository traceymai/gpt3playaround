from transformers import GPT2TokenizerFast
from write_prompts_token import write_prompts_all_text
tokenizer = GPT2TokenizerFast.from_pretrained("gpt2")
prompt = write_prompts_all_text("sm_text_sentiment_training.txt").strip()

tokens = tokenizer.encode(prompt)
num_tokens = len(tokens)

print(f"Token Count: {num_tokens}")

# GPT-3 Experiments for Sentiment and Arousal Analysis  
##Instructions:  
- Specify all necessary input configs in input_config.json.  
- If you're labelling Sentiment, it is recommended that you specify "prompt_type" under
"prompt_design" in the config as "long", and use engine "davinci-instruct-beta" or 
  "cushman-alpha" for higher accuracy. An ideal prompt in this situation would look like:  
  
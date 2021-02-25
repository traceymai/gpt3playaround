# GPT-3 Experiments for Sentiment and Arousal Analysis  
##Instructions:  
- Specify all necessary input configs in input_config.json.  
- If you're labelling Sentiment, it is recommended that you specify "train_mode/train_or_zeroshot"
  as "train" to prime the model with training instances, specify "prompt_type" under
"prompt_design" in the config as "long", use engine "davinci-instruct-beta" or 
  "cushman-alpha" for higher accuracy, replace "prompt_design/prompt" with your prompt of choice, choose "train" under "train_or_zeroshot",
  train with 1 instance/category in "num_lines_per_category" and choose batch size 5 in
  "num_lines_per_batch".
  An ideal prompt in this situation would look like: (also format of "long" prompt)
  

  <img align="middle" src="https://i.imgur.com/MNu2AVp.png" width="700">
Then specify input prefix (replace "Tweet") and output prefix ("Output") of choice, specify
number of training instances per category you want to prime GPT-3 with (to maintain balance in training data).
Note that input text file should be in the format

<img align="middle" src="https://i.imgur.com/mjcGJ1h.png" width="700">  

- If you're labelling Arousal, it is recommended that you specify "train_mode/train_or_zeroshot"
  as "zeroshot" to perform zeroshot training, specify "prompt_type" under "prompt_desisgn"
in the config as "short", use engine "davinci-instruct-beta" for higher accuracy, replace
  "prompt_design/prompt" with your own descriptive prompt. An ideal prompt in this situation would
  look like: (also format of "short" prompt)
  
<img align="middle" src="https://i.imgur.com/uDZHAj2.png" height="70" width="900">

Explanations of config variables:
  * gpt3_engine: OpenAI's GPT-3 engine to that takes in prompt inputs and generates output text.
All config setting variables in this section pertain to OpenAI's trainable parameters as documented through
    OpenAI's official documentation.
    
* classification_task: Choose between "valence" and "arousal" for Sentiment and Arousal
Classification, respectively.
  
* train_or_zeroshot: Choose between passing in training instances to prime the transformer
  ("train")
or doing zeroshot learning ("zeroshot")(using pretrained weights to make classification predictions)
  
* output_dir: Directory to put prediction output text file into.
* output_filename: Desired name of output file.
* num_lines_per_category: If "train_or_zeroshot" is specified as "train", the number of training
instances per sentiment/arousal category to prime the transformer with.
  
* num_lines_per_batch: If "prompt_type" is specified as "long", the number of instances
to be passed to the transformer to get GPT-3 output from.
  
* input_file_to_label: Testing input file whose sentences will be passed to GPT-3 to obtain
classification output for.
  Note: This file should be formatted with no heading, with each sentence being in the format:
  "Sentiment/Arousal_score, Phrase_text\n"
  
* train_input_file: If "train_or_zeroshot" is specified as "train", the input file to obtain
training instances from.
  Note: This file should be formatted with heading "Sentiment_class_label:->Phrase_text",
  with each sentence having the format "Sentiment/Arousal_score:->Phrase_text\n"
  
* descriptive_prompt: If "train_or_zeroshot" is specified as "zeroshot", the prompt to use
as a single sentence to prime the transformer before testing input is sent.
  
* prompt: If "train_or_zeroshot" is specified as "train", the prompt to use to prime the transformer
before testing input is sent.
  
* prompt_type: "long" or "short" (see example above)
* input_prefix: Prefix to go before passing input sentences
* output_prefix: Prefix to nudge GPT-3 to return classification prediction.


  
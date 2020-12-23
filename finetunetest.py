import jsonlines

sample_1 = {"data": {"text_list": ["<joke>", "What do you call an Autobot who works in an overpriced makeup store at the mall ? Ulta Magnus!"], "loss_weights": [0, 1]}}
sample_2 = {"text_list": ["<joke>", "Why did the bicycle fall over? Because it was two-tired"], "loss_weights": [0, 1]}}

with jsonlines.open('finetunetest.jsonl', 'w') as writer:
    writer.write_all(sample)
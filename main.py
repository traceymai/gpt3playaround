import pandas as pd
import sys
import json
from gpt import GPT
import openai
import sys
from pathlib import Path

def init_gpt(_gpt_info_dict):
    _engine = _gpt_info_dict["engine"]
    _temperature = _gpt_info_dict["temperature"]
    _max_tokens = _gpt_info_dict["max_tokens"]
    # _input_prefix = _prompt_design_dict["input_prefix"]
    # _input_suffix = ""
    # _output_prefix = _prompt_design_dict["output_prefix"]
    # _output_suffix = ""
    _stop = _gpt_info_dict["stop_sequence"]
    _frequency_penalty = _gpt_info_dict["frequency_penalty"]
    _presence_penalty = _gpt_info_dict["presence_penalty"]
    _top_p=_gpt_info_dict["top_p"]
    _n=_gpt_info_dict["n"]
    _logprobs = _gpt_info_dict["logprobs"]
    with open('arousal/GPT_SECRET_KEY.json') as f:
        data = json.load(f)
    openai.api_key = data["API_KEY"]
    _gpt_instance = GPT(engine = _engine,
                        temperature=_temperature,
                        max_tokens=_max_tokens,
                        stop=_stop,
                        top_p = _top_p,
                        n = _n,
                        frequency_penalty=_frequency_penalty,
                        presence_penalty=_presence_penalty,
                        logprobs=_logprobs)
    return _gpt_instance

def change_to_strings_sentiment(sent_score):
    if sent_score.strip() == "1.0":
        return "Positive"
    elif sent_score.strip() == "0.0":
        return "Neutral"
    elif sent_score.strip() == "-1.0":
        return "Negative"
    else:
        raise ValueError("Training sentiment score needs to be 1.0 (Positive), 0.0 (Neutral) or -1.0 (Negative)")
def get_input_prams():
    if len(sys.argv) > 1:
        _configPath = sys.argv[1]
    else:
        _configPath = input("Please enter path to JSON config file: ")
    with open(_configPath, encoding="utf8") as _jsonDataFile:
        _data = json.load(_jsonDataFile)
        _gptInfoDict = _data["gpt3_engine"]
        _promptDesignInfoDict = _data["prompt_design"]
        _trainModeDict = _data["train_mode"]
        # if _trainMode == "train":
        #     _trainModeDict = _data["train_mode"]["train"]
        # elif _trainMode == "zeroshot":
        #     _trainModeDict = _data["train_mode"]["zeroshot"]
        # _trainModeDict["input_file_to_label"] = _data["train_mode"]["input_file_to_label"]
        _classificationTask = _data["classification_task"]
        _jsonDataFile.close()
        return _gptInfoDict, _trainModeDict, _promptDesignInfoDict, _classificationTask




def prefill_prompt(_gpt_info_dict, _input_prompt, _train_mode_dict, _prompt_design_info_dict, _classification_task):
    _stop_sequence = _gpt_info_dict["stop_sequence"]
    _input_file_to_label = _train_mode_dict["input_file_to_label"]
    _train_mode = _train_mode_dict["train_or_zeroshot"]
    _prompt = _prompt_design_info_dict["prompt"]
    _inputPrefix = _prompt_design_info_dict["input_prefix"]
    _outputPrefix = _prompt_design_info_dict["output_prefix"]
    _input_prompt += _prompt + "\n"

    with open(_input_file_to_label, "r", encoding="utf8") as _f:
        _allDataList = _f.readlines()
        _allDataList = [x.strip("\r\n") for x in _allDataList]
        _allDataList = [x.split(",", 1) for x in _allDataList]
        _labelList = [x[0] for x in _allDataList]
        _phraseList = [x[1] for x in _allDataList]
        _f.close()

    if _train_mode == "train":
        _trainDict = _train_mode_dict["train"]
        _trainInputFile = _trainDict["train_input_file"]
        _numLinesPerBatch = _trainDict["num_lines_per_batch"]
        with open(_trainInputFile, "r", encoding="utf8") as _f:
            _trainDataList = _f.readlines()[1:]
            _trainDataList = [x.strip("\r\n") for x in _trainDataList]
            _trainDataList = [x.split(":->",1) for x in _trainDataList]
            _labelTrainList = [x[0] for x in _trainDataList]
            _labelTrainList = [change_to_strings_sentiment(x) for x in _labelTrainList]
            _phraseTrainList = [x[1].strip() for x in _trainDataList]
            for _ind in range(len(_phraseTrainList)):
                _input_prompt += _inputPrefix + _phraseTrainList[_ind] + "\n"
                _input_prompt += _outputPrefix + _labelTrainList[_ind] + "\n"
                _input_prompt += _stop_sequence + "\n"
            _input_prompt += "Tweet text\n"
            for _ind in range(1, len(_phraseTrainList) + 1):
                _input_prompt += str(_ind) + ". " + _phraseTrainList[_ind - 1] + "\n"
            _input_prompt += "Tweet sentiment ratings:\n"
            for _ind in range(1, len(_labelTrainList) + 1):
                _input_prompt += str(_ind) + ": " + _labelTrainList[_ind - 1] + "\n"
            _input_prompt += "###\n"
            _input_prompt += "Tweet text\n"
            _f.close()
    elif _train_mode == "zeroshot":
        _zeroshotDict = _train_mode_dict["zeroshot"]
        _zeroshotDescriptivePrompt = _zeroshotDict["descriptive_prompt"]
        _input_prompt += _zeroshotDescriptivePrompt + "\n"
    return _input_prompt, _phraseList

def submit_gpt_request(_train_mode_dict, _phrase_list):
    _numLinesInBatch = _train_mode_dict["num_lines_in_batch"]
    _outputDir = _train_mode_dict["output_dir"]
    _numBatchesNeeded = (len(_phrase_list) // _numLinesInBatch) + 1
    _startIndex = 0


if __name__ == "__main__":
    gptInfoDict, trainModeDict, promptDesignInfoDict, classificationTask = get_input_prams()
    gptInstance = init_gpt(gptInfoDict)
    sentimentPrompt = ""
    sentimentPrompt, phraseList = prefill_prompt(gptInfoDict, sentimentPrompt, trainModeDict, promptDesignInfoDict, classificationTask)
    no_lines_in_batch = 10
    no_batches_needed = (len(phraseList) // no_lines_in_batch) + 1
    start_ind = 0
    with open("valence/gpt_in_longer_prompt_valence.txt", "r+", encoding="utf8") as f:
        f.truncate(0)
        f.close()
    for batch in range(1, no_batches_needed + 1):
        # for each batch of no_lines_in_batch input lines passed through
        if batch == 1 or batch == 2:
            gpt_instance = init_gpt(no_lines_in_batch)
            end_ind = start_ind + no_lines_in_batch
            if end_ind > len(phraseList):
                end_ind = len(phraseList)
            for ind in range(start_ind, end_ind):
                if ind % no_lines_in_batch == 0:
                    sentimentPrompt += str(ind % no_lines_in_batch + 1) + ". " + phraseList[ind] + "\n"
                    with open("valence/gpt_in_longer_prompt_valence.txt", "a", encoding="utf8") as f:
                        f.write(str(ind + 1) + ". " + phraseList[ind] + "\n")
                else:
                    sentimentPrompt += str(ind % no_lines_in_batch + 1) + ". " + phraseList[ind] + "\n"
                    with open("valence/gpt_in_longer_prompt_valence.txt", "a", encoding="utf8") as f:
                        f.write(str(ind + 1) + ". " + phraseList[ind] + "\n")
            start_ind += no_lines_in_batch
            sentimentPrompt += "Tweet sentiment ratings:\n"
            sentimentPrompt += "1."
            print("BATCH {}".format(batch))
            print(sentimentPrompt)
            response = gpt_instance.submit_request(prompt=sentimentPrompt).choices[0].text
            print("GPT response is", response)
            if batch == 1:
                with open("valence/gpt_out_longer_prompt_valence.txt", "w") as f:
                    f.truncate(0)
                    f.write(response + "\n")
                    f.close()
            else:
                with open("valence/gpt_out_longer_prompt_valence.txt", "a") as f:
                    f.write(response + "\n")
                    f.close()
            sentimentPrompt = ""
            sentimentPrompt += prefill_prompt()[0]

        else:
            break
    print("FINISH")







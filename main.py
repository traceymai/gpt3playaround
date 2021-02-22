import pandas as pd
import sys
import json
from gpt import GPT
import openai
import sys
from pathlib import Path


def init_gpt(_gpt_info_dict, _prompt_design_info_dict):
    _engine = _gpt_info_dict["engine"]
    _temperature = _gpt_info_dict["temperature"]
    _max_tokens = _gpt_info_dict["max_tokens"]
    _promptType = _prompt_design_info_dict["prompt_type"]
    # _input_prefix = _prompt_design_dict["input_prefix"]
    # _input_suffix = ""
    # _output_prefix = _prompt_design_dict["output_prefix"]
    # _output_suffix = ""
    if _promptType == "long":
        _stop = _gpt_info_dict["stop_sequence"]
    elif _promptType == "short":
        _stop = "\n"
    _frequency_penalty = _gpt_info_dict["frequency_penalty"]
    _presence_penalty = _gpt_info_dict["presence_penalty"]
    _top_p = _gpt_info_dict["top_p"]
    _n = _gpt_info_dict["n"]
    _logprobs = _gpt_info_dict["logprobs"]
    with open('arousal/GPT_SECRET_KEY.json') as f:
        data = json.load(f)
    openai.api_key = data["API_KEY"]
    _gpt_instance = GPT(engine=_engine,
                        temperature=_temperature,
                        max_tokens=_max_tokens,
                        stop=_stop,
                        top_p=_top_p,
                        n=_n,
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


def change_to_strings_arousal(arousal_score):
    if arousal_score.strip() == "1.0":
        return "High Activation"
    elif arousal_score.strip() == "0.0":
        return "Medium Activation"
    elif arousal_score.strip() == "-1.0":
        return "Medium Deactivation"
    elif arousal_score.strip() == "-2.0":
        return "High Deactivation"
    else:
        raise ValueError(
            "Training arousal score needs to be 1.0 (High Activation), 0.0 (Medium Activation), -1.0 (Medium Deactivation)" \
            "or -2.0 (High Deactivation)")


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
        if _trainModeDict["train_or_zeroshot"] == "zeroshot":
            _gptInfoDict["stop_sequence"] = "\n\n"
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
    _promptType = _prompt_design_info_dict["prompt_type"]
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
        _numLinesPerCate = _train_mode_dict["num_lines_per_category"]
        with open(_trainInputFile, "r", encoding="utf8") as _f:
            _trainDataList = _f.readlines()[1:]
            _trainDataList = [x.strip("\r\n") for x in _trainDataList]
            _trainDataList = [x.split(":->", 1) for x in _trainDataList]
            _trainDataDf = pd.DataFrame(_trainDataList, columns = [_classification_task, "Phrase"])
            _trainDataDf = _trainDataDf.groupby(_classification_task).apply(lambda row: row.sample(_numLinesPerCate)).reset_index(drop=True)
            _labelTrainList = _trainDataDf[_classification_task].tolist()
            _phraseTrainList = _trainDataDf["Phrase"].tolist()
            # _labelTrainList = [x[0] for x in _trainDataList]
            _f.close()
        if _classification_task == "valence":
            _labelTrainList = [change_to_strings_sentiment(x) for x in _labelTrainList]
        elif _classification_task == "arousal":
            _labelTrainList = [change_to_strings_arousal(x) for x in _labelTrainList]
        # _phraseTrainList = [x[1].strip() for x in _trainDataList]

    elif _train_mode == "zeroshot":
        _zeroshotDict = _train_mode_dict["zeroshot"]
        _zeroshotDescriptivePrompt = _zeroshotDict["descriptive_prompt"]
    if _promptType == "long":
        if _train_mode == "train":
            for _ind in range(len(_phraseTrainList)):
                _input_prompt += _inputPrefix + _phraseTrainList[_ind] + "\n"
                _input_prompt += _outputPrefix + _labelTrainList[_ind] + "\n"
                _input_prompt += _stop_sequence + "\n"
            _input_prompt += "Tweet text\n"
            for _ind in range(1, len(_phraseTrainList) + 1):
                _input_prompt += str(_ind) + ". " + _phraseTrainList[_ind - 1] + "\n"
            if _classification_task == "valence":
                _input_prompt += "Tweet sentiment ratings:\n"
            elif _classification_task == "arousal":
                _input_prompt += "Tweet arousal ratings:\n"
            for _ind in range(1, len(_labelTrainList) + 1):
                _input_prompt += str(_ind) + ": " + _labelTrainList[_ind - 1] + "\n"
            _input_prompt += "###\n"
        elif _train_mode == "zeroshot":
            _input_prompt += _zeroshotDescriptivePrompt + "\n"
        _input_prompt += "Tweet text:\n"
        return _input_prompt, _phraseList
    elif _promptType == "short":
        if _train_mode == "train":
            for _ind in range(len(_phraseTrainList)):
                _input_prompt += _inputPrefix + _phraseTrainList[_ind] + "\n"
                _input_prompt += _outputPrefix + _labelTrainList[_ind] + "\n"
        return _input_prompt, _phraseList

    #     if _train_mode == "train":
    #         _trainDict = _train_mode_dict["train"]
    #         _trainInputFile = _trainDict["train_input_file"]
    #         _numLinesPerBatch = _trainDict["num_lines_per_batch"]



def submit_gpt_request(_gpt_instance, _train_mode_dict, _phrase_list, _sentiment_prompt, _classification_task, _gpt_info_dict, _prompt_design_info_dict):
    _outputDir = _train_mode_dict["output_dir"]
    _outputFile = _train_mode_dict["output_filename"]
    _outputFolder = Path(_outputDir)
    _outputFolder.mkdir(parents=True, exist_ok=True)
    _filePath = _outputFolder / _outputFile
    with _filePath.open("w+", encoding="utf8") as _f:
        _f.truncate(0)
        _f.close()
    if _prompt_design_info_dict["prompt_type"] == "long":
        _numLinesInBatch = _train_mode_dict["num_lines_per_batch"]
        _numBatchesNeeded = (len(_phrase_list) // _numLinesInBatch) + 1
        _startIndex = 0
        for _batch in range(1, _numBatchesNeeded + 1):
            _endIndex = _startIndex + _numLinesInBatch
            if _endIndex > len(_phrase_list):
                _endIndex = len(_phrase_list)
            for _ind in range(_startIndex, _endIndex):
                _sentiment_prompt += str(_ind % _numLinesInBatch + 1) + ". " + _phrase_list[_ind] + "\n"
            _startIndex += _numLinesInBatch
            if _classification_task == "valence":
                _sentiment_prompt += "Tweet sentiment ratings:\n"
            elif _classification_task == "arousal":
                _sentiment_prompt += "Tweet arousal ratings:\n"
            _sentiment_prompt += "1."
            print("BATCH {}".format(_batch))
            print(_sentiment_prompt)
            _response = _gpt_instance.submit_request(prompt=_sentiment_prompt).choices[0].text
            print("GPT response is", _response)
            with _filePath.open("a", encoding="utf8") as _f:
                _f.write(_response + "\n")
                _f.close()
            _sentiment_prompt = ""
            _sentiment_prompt += prefill_prompt(_gpt_info_dict, _sentiment_prompt, _train_mode_dict, _prompt_design_info_dict, _classification_task)[0]
    elif _prompt_design_info_dict["prompt_type"] == "short":
        _inputPrefix = _prompt_design_info_dict["input_prefix"]
        _outputPrefix = _prompt_design_info_dict["output_prefix"]
        _stopSequence = "\n"
        for index, phrase in enumerate(_phrase_list):
            _sentiment_prompt += _inputPrefix + phrase + "\n"
            _sentiment_prompt += _outputPrefix
            print("prompt is")
            print(_sentiment_prompt)
            _response = _gpt_instance.submit_request(prompt=_sentiment_prompt).choices[0].text.lower().strip()
            print("GPT response is", _response)
            with _filePath.open("a", encoding="utf8") as _f:
                _f.write(str(index + 1) + ". " + phrase + ":->" + _response + "\n")
                _f.close()
            _sentiment_prompt = ""
            _sentiment_prompt += prefill_prompt(_gpt_info_dict, _sentiment_prompt, _train_mode_dict, _prompt_design_info_dict,
                           _classification_task)[0]



if __name__ == "__main__":
    gptInfoDict, trainModeDict, promptDesignInfoDict, classificationTask = get_input_prams()
    gptInstance = init_gpt(gptInfoDict, promptDesignInfoDict)
    sentimentPrompt = ""
    sentimentPrompt, phraseList = prefill_prompt(gptInfoDict, sentimentPrompt, trainModeDict, promptDesignInfoDict,
                                                 classificationTask)
    # no_lines_in_batch = 10
    # no_batches_needed = (len(phraseList) // no_lines_in_batch) + 1
    submit_gpt_request(gptInstance, trainModeDict, phraseList, sentimentPrompt, classificationTask, gptInfoDict, promptDesignInfoDict)
    print("FINISH")

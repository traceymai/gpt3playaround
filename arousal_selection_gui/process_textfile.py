
def process_textfile(filename):
    infile = open(filename, "r", encoding="utf8")
    all_content = sorted(infile.readlines(), key=str.casefold)
    all_content = [line.strip('\r\n') for line in all_content]
    all_content = [x.rsplit(",", 3) for x in all_content]
    phrase_dict = {}
    remove_dict = {}
    for idx in range(len(all_content)):
        line = all_content[idx]
        phrase = line[0]
        if phrase not in phrase_dict:
            phrase_dict[phrase] = (1, idx)
        else:
            if phrase not in remove_dict:
                remove_dict[phrase] = [idx]
            elif phrase in remove_dict:
                remove_dict[phrase].append(idx)
            phrase_dict[phrase] = ((phrase_dict[phrase][0] + 1), idx)
    print([(key, phrase_dict[key]) for key in phrase_dict if phrase_dict[key][0] > 1])
    print(len([(key, phrase_dict[key]) for key in phrase_dict if phrase_dict[key][0] > 1]))
    #idx_content_to_remove = [phrase_dict[key][1] for key in phrase_dict.keys() if phrase_dict[key][0] > 1]
    idx_content_to_remove = []
    for val in remove_dict.values():
        for ele in val:
            idx_content_to_remove.append(ele)
    content_to_remove = [all_content[i][0] for i in idx_content_to_remove]
    with open("outfremove.txt", "w") as f:
        for line in content_to_remove:
            f.write(line + "\n")
        f.close()
    all_content_new = []
    for idx in range(len(all_content)):
        if idx not in idx_content_to_remove:
            all_content_new.append(all_content[idx])
    print("length of all content new", len(all_content_new))
    newfile = "cleaned_{}".format(filename)
    with open(newfile, "r+", encoding="utf8") as newf:
        newf.truncate(0)
        for line in all_content_new:
            line = ", ".join(line)
            line += "\n"
            # try:
            #     newf.write(line)
            # except UnicodeEncodeError:
            #     print(line)
            newf.write(line)
    newf.close()
    return newfile, content_to_remove
# with open("cleanedfile.txt", "a") as outfile:
#     for line in all_content:

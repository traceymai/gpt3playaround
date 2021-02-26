# Arousal Validation GUI
### Instructions:
- Create a clean Anaconda virtual environment (using Python 3.7) through Anaconda Navigator
  (this avoids unnecessary package installations through Anaconda Prompt)
  
- Run ```arousal_selection_gui\main.py``` from any IDE of choice.
- GUI display:

<img align="middle" src="https://i.imgur.com/X8l2zod.png" width="900">  
  
- GUI sections explanation:
  + Phrase Text: Sentence whose GPT-3 arousal classification outputs are collected through non-descriptive
  and descriptive prompts
    
  + Arousal 1: GPT-3 arousal output on shorter, less descriptive prompt. If choosing this label, click
    "Submit" button underneath the label
  + Arousal 2: GPT-3 arousal output on longer, more descriptive prompt. If choosing this label, click
    "Submit" button underneath the label
    (**Note: 1.0 for High Activation, 0.0 for Medium Activation, -1.0 for Medium Deactivation, -2.0 for High
    Deactivation**)
    
  + Human Label: If neither output GPT-3 generated is appropriate, input a floating point corresponding
  to appropriate arousal category (as described above), then click "Submit" button underneath the label
    
  + After 1 of the 3 "Submit" buttons is clicked, hit "next" to move on to the next sentence.
  + Use "previous" button to move back to the previous sentence to check validated arousal label ("Submit"
    button highlighted in red or smaller pop-up tag to the right of Human Label's "Submit" button if a human label
    was inputted), or modify existing validated arousal label.
    
  + Input a line number into the long bar underneath Human Label's "Submit" button and hit "jump" to jump to
  inputted sentence.
    
  + Hit "save all" to save all inputted sentences (including existingly validated sentences) into "conclusive_labels_final.txt"
  as defined by default or any text file of choice by specifying outFinal under class MyFirstGUI definition in the
    main script.
    
  + When GUI is launched from IDE, all existingly validated sentences from "conclusive_labels_final.txt"
  are read and corresponding validated labels are highlighted in red.
    
  + When exiting GUI, choose between "Quit and Save All" to save all label validation results into 
    "conclusive_labels_final.txt", or "Quit
    and Not Save" to discard all label validation of current session.
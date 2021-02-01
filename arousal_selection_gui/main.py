import tkinter as tk
from tkinter import *
import tkinter.messagebox as tkmessagebox
import tkinter.font as tkfont
from process_textfile import process_textfile
import math

## TODO: Get rid of all unused code


class MyFirstGUI:
    fileName = "outmergedmissing.txt"
    fileName, contentToRemove = process_textfile(fileName)
    outFile = "conclusive_labels_linebyline.txt"
    outFinal = "conclusive_labels_final.txt"
    line_button_number = 15
    index = 0
    allText = None
    displays = None
    correctLabels = None
    button_previous = None
    button_next = None
    button_save = None
    button_jump = None
    submitbutton_label1 = None
    submitbutton_label2 = None
    human_label_entry = None
    button_show_entry = None
    txt_jump = None
    entryLabel = None
    correctLabel = None

    def __init__(self, window):
        self.window = window
        self.font = tkfont.Font(size=15)
        window.protocol("WM_DELETE_WINDOW", lambda arg=window: self.messageWindow())
        self.get_all_text()
        self.get_correct_labels_existing()
        self.set_up_labels()
        self.get_a_line_unmatched()

    def ask_quit(self):
        self.save_all_lines()
        self.window.destroy()


    def only_quit(self):
        self.window.destroy()


    def messageWindow(self):
        #TODO: Resize window, options: Quit, Quit & Save, make message smaller

        win = Toplevel()
        win.title("About to Quit...")
        message = "Did you wish to quit and save all?"
        Label(win, text=message).pack()
        Button(win, text="Quit and save all", command=self.ask_quit).pack()
        Button(win, text="Quit and not save", command=self.only_quit).pack()



    def get_correct_labels_existing(self):
        #TODO: Refactor code to be consistent in coding style
        self.correctLabels = {}
        with open(self.outFinal) as outFinal:
            existing_content = outFinal.readlines()
        print("Existing content:")
        print(existing_content)
        if existing_content != [] and existing_content[0] != '\n' and existing_content[0] != '': # There is existing content
            existing_content = [line.strip('\r\n') for line in existing_content]
            for line in existing_content:
                line = line.rsplit(",", 1)
                line = [word.strip() for word in line]
                sentence = line[0]
                self.correctLabels[sentence] = line[-1]
        print("correctLabels after appending existing info:")
        print(self.correctLabels)
        outFinal.close()

    def go_previous(self):
        print("Going previous")
        print(self.index)
        print(self.correctLabels)
        if self.index >= 1:
            self.index -= 1
            self.submitbutton_label1['bg'] = 'white'
            self.submitbutton_label2['bg'] = 'white'
            self.button_show_entry['bg'] = 'white'
        if self.entryLabel != None:
            self.entryLabel.destroy()
        self.get_a_line_unmatched()

    def go_next(self):
        print("Going next")
        print(self.correctLabels)
        if self.correctLabel != None:
            self.correctLabels[self.list_line_eles[0].strip()] = self.correctLabel
            print(self.correctLabels)
            if self.index + 1 < len(self.allText):
                self.index += 1
            self.correctLabel = None
            self.submitbutton_label1['bg'] = 'white'
            self.submitbutton_label2['bg'] = 'white'
            self.button_show_entry['bg'] = 'white'
            if self.entryLabel != None:
                self.entryLabel.destroy()
            self.get_a_line_unmatched()

    def go_save(self):
        self.save_a_line()

    def go_jump(self):
        content = self.txt_jump.get()
        if len(content) > 0:
            test_index = int(content) - 1
            if 0 <= test_index < len(self.allText):
                self.index = test_index
                self.submitbutton_label1['bg'] = 'white'
                self.submitbutton_label2['bg'] = 'white'
                self.button_show_entry['bg'] = 'white'
                if self.entryLabel != None:
                    self.entryLabel.destroy()
                self.get_a_line_unmatched()

    def save_all_lines(self):
        print("About to save all lines to outfinal")
        if self.correctLabel != None:
            self.correctLabels[self.list_line_eles[0].strip()] = self.correctLabel
            print(self.correctLabels)
        outf = open(self.outFinal, "r+")
        outf.truncate(0)
        if len(self.correctLabels) >= 1:
            for sent in self.correctLabels:
                conclusive_label = self.correctLabels[sent]
                line_ele = [sent, conclusive_label]
                line = ', '.join(line_ele)
                fileOutFinal = open(self.outFinal, "a")
                fileOutFinal.write(line + "\n")
            fileOutFinal.close()

    #TODO: Rename these functions below
    def arousal1_submit_button(self):
        self.submitbutton_label1['bg'] = "pink"
        if self.submitbutton_label2['bg'] == "pink" or self.button_show_entry['bg'] == "pink":
            self.submitbutton_label2['bg'] = "white"
            self.button_show_entry['bg'] = "white"
        self.correctLabel = self.Label1.cget("text")
    def clicked_2(self):
        self.submitbutton_label2['bg'] = "pink"
        if self.submitbutton_label1['bg'] == "pink" or self.button_show_entry['bg'] == "pink":
            self.submitbutton_label1['bg'] = "white"
            self.button_show_entry['bg'] = "white"
        self.correctLabel = self.Label2.cget("text")
    def color_change_1(self):
        if self.submitbutton_label2['bg'] == "pink" or self.button_show_entry['bg']=="pink":
            self.submitbutton_label2['bg'] = "white"
            self.button_show_entry['bg'] = "white"
        print("YES")
        self.submitbutton_label1['bg'] = "pink"

    def color_change_2(self):
        if self.submitbutton_label1['bg'] == "pink" or self.button_show_entry['bg']=="pink":
            self.submitbutton_label1['bg'] = "white"
            self.button_show_entry['bg'] = "white"
        self.submitbutton_label2['bg'] = "pink"
    def color_change_3(self):
        self.button_show_entry['bg'] = "pink"
        if self.submitbutton_label1['bg'] == "pink" or self.submitbutton_label2['bg']=="pink":
            self.submitbutton_label1['bg'] = "white"
            self.submitbutton_label2['bg'] = "white"
        try:
            float(self.human_label_entry.get())
        except ValueError:
            print("ERROR! Please enter a floating point in [1.0, 0.0, -1.0, -2.0]")
        else:
            assert float(self.human_label_entry.get()) in [1.0, 0.0, -1.0, -2.0], "Please enter a floating point in [1.0, 0.0, -1.0, -2.0]"
            self.correctLabel = self.human_label_entry.get()
    def set_up_labels(self):
        print(self.allText)
        print("content to remove is", self.contentToRemove)
        print("Total content to remove is", 2 * len(self.contentToRemove))
        row = 0
        column = 0
        label_text = tk.Label(self.window, font=self.font, text="Phrase Text", bg='#49A')
        label_text.grid(row=row, column=column, padx=10, pady=10)
        column += 2
        label_prompt1 = tk.Label(self.window, font = self.font, text = "Arousal 1", bg='#49A')
        label_prompt1.grid(row = row, column = column)
        column += 1
        label_prompt2 = tk.Label(self.window, font=self.font, text="Arousal 2", bg="#49A")
        label_prompt2.grid(row=row, column=column)
        column += 1
        label_prompt3 = tk.Label(self.window, font=self.font, text="Human Label", bg="#49A")
        label_prompt3.grid(row=row, column=column)
        self.submitbutton_label1 = tk.Button(self.window, text="Submit", padx=10, pady=10, font=self.font)
        self.submitbutton_label1.grid(row=2, column=2, padx=10, pady=10, sticky="nsew")
        self.submitbutton_label2 = tk.Button(self.window, text="Submit", padx=10, pady=10, font=self.font)
        self.submitbutton_label2.grid(row=2, column=3, padx=10, pady=10, sticky="nsew")
        self.button_show_entry = tk.Button(self.window, text="Submit", font=self.font,
                                           padx=10, pady=10)
        self.button_show_entry.grid(row=2, column=4, padx=10, pady=10, sticky="nsew")
    def get_a_line_unmatched(self):
        # if self.displays is not None:
        #     for display in self.displays:
        #         display.destroy()
        #         display = None
        #     self.button_previous.destroy()
        #     self.button_previous = None
        #     self.button_next.destroy()
        #     self.button_next = None
        #     self.button_jump.destroy()
        #     self.button_jump = None
        #     self.button_save.destroy()
        #     self.button_save = None
        #     self.txt_jump.destroy()
        #     self.txt_jump = None
        row = 1
        column = 0
        print("current self.index is", self.index)
        line = self.allText[self.index]
        self.displays = []
        self.list_line_eles = line.rsplit(", ", 3)[:3]
        phrase = self.list_line_eles[0].strip()
        print(phrase)
        print(self.correctLabels)
        # if phrase in self.correctLabels:
        #     print("It is not None")
        #     self.correctLabel = self.correctLabels[phrase]
        self.correctLabel = self.correctLabels.get(phrase)
        if self.correctLabel == None:
            self.submitbutton_label2['bg'] = 'white'
            self.submitbutton_label1['bg'] = 'white'
            self.button_show_entry['bg'] = 'white'
        matched = line.split(",")[-1].strip()
        for index, word in enumerate(self.list_line_eles):
            print((index, word))
            if index == 0: # This is a Phrase_text instance
                word = word.strip()
                T = tk.Label(self.window, font = self.font, text=word)
                T.grid(column=column, row=row, sticky = "nsew", columnspan=2, rowspan=1, padx=10, pady=10)
                #S = tk.Scrollbar(self.window, command=T.yview, orient="vertical")
                #S.grid(row=1, column=1, sticky = "ns")
                #S.pack(side = tk.RIGHT, fill = tk.Y)
                #T.pack(side = tk.LEFT, fill = tk.Y)
                #S.config(command = T.yview)
                #T.config(yscrollcommand = S.set)
                ##quote = word
                ##T.insert(tk.END, quote)
                ##T.config(state='disabled')
                self.displays.append(T)
                column += 2

            elif index == 1: # This is the first label
                self.Label1 = tk.Label(self.window, font=self.font, text=word)
                self.Label1.grid(column=column, row=row, sticky="nsew", padx=10, pady=10)
                if self.correctLabel == self.Label1.cget("text"):
                    self.submitbutton_label1['bg'] = "pink"
                    #self.change_col_again = False
                if matched == "F":
                    self.Label1.config(bg="IndianRed1")
                elif matched == "T":
                    self.Label1.config(bg="green yellow")
                # arousal_label1 = word
                # Label1.insert(tk.END, arousal_label1)
                # Label1.config(state="disabled")
                self.Label1.grid(column=column, row=row, sticky="nsew", padx=10, pady=10)
                self.displays.append(self.Label1)
                # self.submitbutton_label1 = tk.Button(self.window, text="Submit", padx=10,pady=10, font=self.font)
                # self.submitbutton_label1.grid(row=row+1, column=column, padx=10, pady=10, sticky="nsew")
                self.submitbutton_label1.config(command=self.arousal1_submit_button)
                #print(self.correctLabels)
                column += 1
            elif index == 2: # This is the second label
                self.Label2 = tk.Label(self.window, font=self.font, text=word)
                self.Label2.grid(column=column, row=row, sticky="nsew", padx=10, pady=10)
                if self.correctLabel == self.Label2.cget("text") and self.submitbutton_label1['bg'] == "white":
                    self.submitbutton_label2['bg'] = 'pink'
                print(row, column)
                if matched == "F":
                    self.Label2.config(bg="IndianRed1")
                elif matched == "T":
                    self.Label2.config(bg="green yellow")
                # arousal_label2 = word
                # Label2.insert(tk.END, arousal_label2)
                # Label2.config(state="disabled")
                self.displays.append(self.Label2)
                # self.submitbutton_label2 = tk.Button(self.window, text="Submit", padx=10, pady=10, font=self.font)
                # self.submitbutton_label2.grid(row=row + 1, column=column, padx=10, pady=10, sticky="nsew")
                self.submitbutton_label2.config(command=self.clicked_2)
                column += 1
        # if self.submitbutton_label1['bg'] == 'white' and self.submitbutton_label2['bg'] == 'white' and phrase in self.correctLabels:
        if phrase in self.correctLabels and self.correctLabels[phrase] != self.list_line_eles[1] and self.correctLabels[phrase] != self.list_line_eles[2]:
            self.entryLabel = tk.Label(self.window, font=self.font, text=self.correctLabels[phrase])
            self.entryLabel.grid(row=2, column=5, padx=5, pady=5)
            self.button_show_entry['bg'] = 'pink'
        self.human_label_entry = tk.Entry(self.window)
        self.human_label_entry.place(width=150, height=50)
        self.human_label_entry.grid(row=1, column=4, padx=10, pady=10, ipady=5)
        self.button_show_entry.config(command=self.color_change_3)
        # self.human_label_entry = tk.Entry(self.window)
        # self.human_label_entry.place(width=150, height=50)
        # self.human_label_entry.grid(row=row, column=column, padx=10, pady=10, ipady=5)
        row += 1
        # self.button_show_entry = tk.Button(self.window, text="Submit", font = self.font, command=self.color_change_3, padx = 10, pady=10)
        # self.button_show_entry.grid(row=row, column=column, padx=10, pady=10,sticky="nsew")
        row += 2
        column -= 2
        # self.button_save = tk.Button(self.window, text="save line", padx=15, font=self.font, bg="pink")
        # self.button_save.config(command=self.go_save)
        # self.button_save.grid(row=4, column=3)

        self.button_previous = tk.Button(self.window, text='previous', padx=1, font=self.font, bg='cyan')
        self.button_previous.config(command=self.go_previous)
        self.button_previous.grid(row=3, column=2)

        self.txt_jump = tk.Entry(self.window, width=15)
        self.txt_jump.grid(row=3, column=4)

        self.button_jump = tk.Button(self.window, text='jump', padx=15, font=self.font, bg='green')
        self.button_jump.config(command=self.go_jump)
        self.button_jump.grid(row=3, column=5)

        self.button_save_all = tk.Button(self.window, text="save all", height=2, padx=15, font=self.font, bg="cyan")
        self.button_save_all.config(command=self.save_all_lines)
        self.button_save_all.grid(row=5, column=5, padx=10, pady=10)

        self.button_next = tk.Button(self.window, text='next', padx=15, font=self.font, bg='red')
        self.button_next.config(command=self.go_next)
        self.button_next.grid(row=3, column=3)

        self.window.title('Line: ' + str(self.index + 1))
        """if word.endswith(self.keyword_sign):
            word = word.strip(self.keyword_sign)
            button = tk.Button(self.window, height=3, text=word, padx=1, font=self.font, bg=self.keyword_color)
        else:
            button = tk.Button(self.window, height=3, text=word, padx=1, font=self.font, bg=self.normal_color)
        button.config(command=lambda arg=button: self.select_button(arg))
        if column > self.line_button_number:
            row += 1
            column = 0
        button.grid(row=row, column=column)
        column += 1"""

        """row_last = math.ceil(len(line.split()) / self.line_button_number) + 1

        self.button_save = tk.Button(self.window, height=3, text='save', padx=15, font=self.font, bg='pink')
        self.button_save.config(command=self.go_save)
        self.button_save.grid(row=row_last, column=self.line_button_number-4)

        self.button_previous = tk.Button(self.window, height=3, text='previous', padx=1, font=self.font, bg='cyan')
        self.button_previous.config(command=self.go_previous)
        self.button_previous.grid(row=row_last, column=self.line_button_number-3)

        self.txt_jump = tk.Entry(self.window, width=10)
        self.txt_jump.grid(row=row_last, column=self.line_button_number-2)

        self.button_jump = tk.Button(self.window, height=3, text='jump', padx=15, font=self.font, bg='green')
        self.button_jump.config(command=self.go_jump)
        self.button_jump.grid(row=row_last, column=self.line_button_number-1)

        self.button_next = tk.Button(self.window, height=3, text='next', padx=15, font=self.font, bg='red')
        self.button_next.config(command=self.go_next)
        self.button_next.grid(row=row_last, column=self.line_button_number)

        self.window.title('Line: ' + str(self.index + 1))"""

    def get_all_text(self):
        print("filename is", self.fileName)
        with open(self.fileName, encoding = "utf-8") as fileIn:
            textIn = fileIn.readlines()
        self.allText = [line.strip('\r\n') for line in textIn]
        #self.allText = sorted(list(set(self.allText)), key=str.casefold)
        print("allText has", len(self.allText))
        fileIn.close()


tkWindow = tk.Tk()
tkWindow.title("Label comparison GUI")
#tkWindow.geometry('1000x400')
tkWindow.geometry("")
tkWindow.configure(bg='#49A')
for row in range(5):
    tkWindow.grid_rowconfigure(row, weight = 1)
for column in range(6):
    tkWindow.grid_columnconfigure(column, weight = 1)
my_gui = MyFirstGUI(tkWindow)
tkWindow.mainloop()

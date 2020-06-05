"""
此程序写于2020年6月4日，为应聘神经所软件工程师题目
"""
import tkinter as tk
import random
import time
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.ticker as mtick
import pandas as pd

COLORS = ['red', 'orange', 'yellow', 'green', 'blue', 'indigo', 'purple']


class Window:

    def __init__(self):
        self.root = tk.Tk()
        self.root.title('stroop')

        # prevent from being covered taskbar
        self.root.attributes("-topmost", True)

        # tips and start&end button
        self.tips_label = tk.Label(self.root, text="Report the Meaning", fg='black', font=("Arial", 20))
        self.tips_label.pack()
        self.statistics_button = tk.Button(master=self.root, text="STATISTICS", bg="blue", fg="white", width=15,
                                           command=self.data_statistics)
        self.statistics_button.pack(side=tk.BOTTOM)
        self.end_button = tk.Button(master=self.root, text="STOP & SAVE", bg="red", fg="white", width=15,
                                    command=self.stop_test_and_save_data)
        self.end_button.pack(side=tk.BOTTOM)
        self.start_button = tk.Button(master=self.root, text="START", bg="green", fg="white", width=15,
                                      command=self.start_test)
        self.start_button.pack(side=tk.BOTTOM)

        # color label
        self.color_word = tk.StringVar()
        self.word_color = tk.StringVar()
        self.color_label = tk.Label(master=self.root, textvariable=self.color_word, font=("Arial", 100))
        # randomly select a color and a color name
        self.select_color_randomly()
        self.color_label.pack()

        # show a timer
        self.time_text = tk.StringVar(value="00:000")
        self.time_label = tk.Label(self.root, textvariable=self.time_text, fg='black', font=("Arial", 60))
        self.time_label.pack()

        # draw color button
        self.canvas = tk.Canvas(self.root, width=780, height=250)
        self.canvas.pack()
        x1, y1, x2, y2 = 40, 50, 120, 130
        for color in COLORS:
            tag_name = color + '_button'
            self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, tags=(tag_name))
            self.canvas.tag_bind(tag_name, "<Button-1>", self.on_click)
            x1 += 100
            x2 += 100

        # start flag, prevent recording when the experiment is stopped
        self.is_start = False

        self.dataset = []

        self.root.mainloop()

    def start_test(self):
        # clear dataset
        self.dataset = []
        # start flag
        self.is_start = True
        # reset start time and color label
        self.start_time = time.time()
        self.select_color_randomly()
        self.get_and_set_time()

    def stop_test_and_save_data(self):
        if self.is_start is False:
            return
        # start flag
        self.is_start = False
        # stop to refresh time
        self.root.after_cancel(self.refresh_time)
        # set time label
        self.time_text.set("00:000")

        self.write_to_excel()

    def write_to_excel(self):
        # if the dataset is empty
        if len(self.dataset) == 0:
            return
        df = pd.DataFrame(self.dataset)
        localtime = time.strftime("%Y%m%d%H%M%S", time.localtime())
        df.to_excel(localtime + '.xlsx', index=False)

    def data_statistics(self):
        # if the dataset is empty
        if len(self.dataset) == 0:
            return

        df = pd.DataFrame(self.dataset)

        # color word is word color
        df_match = df.loc[df['presented_color_word'] == df['presented_word_color']]
        # color word is not word color
        df_mismatch = df.loc[df['presented_color_word'] != df['presented_word_color']]

        # y data
        # correct rate
        correct_rate_1 = 0 if df_match.shape[0] == 0 \
            else list(df_match['is_right']).count(True) / df_match.shape[0] * 100
        correct_rate_2 = 0 if df_mismatch.shape[0] == 0 \
            else list(df_mismatch['is_right']).count(True) / df_mismatch.shape[0] * 100
        y1 = [correct_rate_1, correct_rate_2]
        # average reaction time
        y2 = [df_match['reaction_time'].mean(), df_mismatch['reaction_time'].mean()]

        # x data
        x = np.arange(2)

        bar_width = 0.1

        # set two y axis
        fig, ax1 = plt.subplots()
        ax2 = ax1.twinx()
        ax1.set_ylabel('correct rate')
        ax2.set_ylabel('average reaction time')
        # set format
        format = mtick.FormatStrFormatter('%.1f%%')
        ax1.yaxis.set_major_formatter(format)

        # draw histogram
        ax1.bar(x, y1, bar_width, color='salmon', label='correct rate')
        ax2.bar(x + bar_width, y2, bar_width, color='orchid', label='average reaction time')

        # tick label
        tick_label = ['the color of the word is the color word', 'is not']
        # position of tick label
        plt.xticks(x + bar_width / 2, tick_label)

        # show label
        fig.legend(loc=1, bbox_to_anchor=(1, 1), bbox_transform=ax1.transAxes)

        # plt.savefig('histogram.png')
        plt.show()

    def get_and_set_time(self):
        # time past
        self.reaction_time = time.time() - self.start_time
        seconds = int(self.reaction_time)
        milliseconds = int((self.reaction_time - seconds) * 1000)
        self.time_text.set('%02d:%03d' % (seconds, milliseconds))
        # refresh time every 1ms
        self.refresh_time = self.root.after(1, self.get_and_set_time)

    def select_color_randomly(self):
        # todo different from the previous one
        self.color_word.set(random.choice(COLORS))
        self.word_color.set(random.choice(COLORS))
        self.color_label.config(fg=self.word_color.get())

    def on_click(self, event):
        if not self.is_start:
            return
        tag_index = event.widget.find_withtag("current")[0]
        color_clicked = COLORS[tag_index - 1]
        result = {
            "presented_color_word": self.color_word.get(),
            "presented_word_color": self.word_color.get(),
            "color_selected": color_clicked,
            "reaction_time": self.reaction_time,
            "is_right": self.color_word.get() == color_clicked
        }
        # print(result)
        # add result to dataset
        self.dataset.append(result)
        # refresh the color and the color name
        self.select_color_randomly()
        # reset start time
        self.start_time = time.time()


if __name__ == '__main__':
    window = Window()

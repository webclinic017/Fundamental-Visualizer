#!/usr/bin/env python
from tkinter import *
from PIL import Image, ImageTk
from webscraper import req_handle, killer
from tkinter import messagebox
import pandas as pd

class Window(Frame):
    def __init__(self, master=None):
        Frame.__init__(self, master)
        self.master = master
        self.master.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.init_window()
        self.plot()

    def init_window(self):
        self.master.title("Fundamentals Visualizer")
        self.pack(fill=BOTH, expand=1)
        self.canvas1 = Canvas(root, width = 805, height = 45, background="black")
        self.canvas1.pack()

        self.var_style = StringVar(root)
        self.var_style.set("BASE")
        self.var_country = StringVar(root)
        self.var_country.set("USA")

        self.symbol = Entry(root)
        self.button1 = Button(text="Update", command=self.update)
        self.w1 = OptionMenu(root, self.var_style, "PEG", "PEG85") #TODO: Implement PEGC
        self.w2 = OptionMenu(root, self.var_country, "Germany", "Hongkong", "Japan", "France", "Canada", "UK", "Switzerland", "Australia","Korea","Netherlands","Spain","Russia","Italy","Belgium","Mexiko","Sweden","Norway","Finland","Denmark") #Austria, Poland

        self.canvas1.create_window(100, 24, window=self.symbol)
        self.canvas1.create_window(200, 24, window=self.button1)
        self.canvas1.create_window(300, 24, window=self.w1)
        self.canvas1.create_window(400, 24, window=self.w2)

    def update(self):
        x = req_handle(self.symbol.get().upper(), self.var_country.get(),self.var_style.get())
        self.plot()

    def plot(self):
        load = Image.open("graphs/plot_base.png")
        render = ImageTk.PhotoImage(load)
        img = Label(self, image=render)
        img.image = render
        img.place(x=0, y=0)

    def on_closing(self):
        if messagebox.askokcancel("Quit", "Do you want to quit?"):
            killer()
            root.destroy()

root = Tk()
w = 805
h = 550
ws = root.winfo_screenwidth()
hs = root.winfo_screenheight()
x = (ws/2) - (w/2)
y = (hs/2) - (h/2) - 50
root.geometry('%dx%d+%d+%d' % (w, h, x, y))
root.configure(background='black')
root.resizable(0,0) #Disable maximize
app = Window(root)
root.mainloop()

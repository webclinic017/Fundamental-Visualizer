#!/usr/bin/env python
from tkinter import *
from tkinter.ttk import Style
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
        self.canvas1 = Canvas(root, width = 805, height = 55, background="black")
        self.canvas1.create_line(100, 0, 100, 55, fill="white")
        self.canvas1.create_line(195, 0, 195, 55, fill="white")
        self.canvas1.create_line(295, 0, 295, 55, fill="white")
        self.canvas1.create_line(403, 0, 403, 55, fill="white")
        self.canvas1.create_line(640, 0, 640, 55, fill="white")
        self.canvas1.pack()

        self.var_style = StringVar(root)
        self.var_style.set("Base")
        self.var_country = StringVar(root)
        self.var_country.set("USA")

        self.disp1 = Label(root, text = '15',background='white')
        self.disp11 = Label(root, text = 'Current  PE',background='black',foreground='white')
        self.disp2 = Label(root, text = '15',background='white')
        self.disp21 = Label(root, text = 'Normal PE',background='black',foreground='white')
        self.disp3 = Label(root, text = '15%',background='white')
        self.disp31 = Label(root, text = 'Growth Rate',background='black',foreground='white')
        self.disp4 = Label(root, text = '15%',background='white')
        self.disp41 = Label(root, text = 'exp. Growth Rate',background='black',foreground='white')
        self.symbol = Entry(root, width = 10)

        self.sdisp = Label(root, text = 'Enter Symbol',background='black',foreground='white')
        self.btn1 = Button(text="Update", command=self.update, height=1, width=6, relief=GROOVE,background='black',foreground='white',activebackground='green',activeforeground='white') #TODO: mouseover

        self.w1 = OptionMenu(root, self.var_style,"Base", "PE15", "PEG85","PE-Plot","REIT") #TODO: Implement PEGC
        self.w2 = OptionMenu(root, self.var_country,"USA", "Germany", "Hongkong", "Japan", "France", "Canada", "UK", "Switzerland", "Australia","Korea","Netherlands","Spain","Russia","Italy","Belgium","Mexiko","Sweden","Norway","Finland","Denmark") #Austria, Poland
        self.w1.config(background='black',foreground='white',relief=FLAT,activebackground='green',activeforeground='white')
        self.w2.config(background='black',foreground='white',relief=FLAT,activebackground='green',activeforeground='white')

        self.canvas1.create_window(50, 41, window=self.disp1)
        self.canvas1.create_window(50, 17, window=self.disp11)
        self.canvas1.create_window(150, 41, window=self.disp2)
        self.canvas1.create_window(150, 17, window=self.disp21)
        self.canvas1.create_window(240, 41, window=self.disp3)
        self.canvas1.create_window(240, 17, window=self.disp31)
        self.canvas1.create_window(350, 41, window=self.disp4)
        self.canvas1.create_window(350, 17, window=self.disp41)

        self.canvas1.create_window(470, 29, window=self.w1)
        self.canvas1.create_window(570, 29, window=self.w2)
        self.canvas1.create_window(690, 41, window=self.symbol)
        self.canvas1.create_window(690, 17, window=self.sdisp)
        self.canvas1.create_window(765, 29, window=self.btn1)

    def update(self):
        x,y,z,w = req_handle(self.symbol.get().upper(), self.var_country.get(),self.var_style.get())
        self.disp1["text"] = str(round(x, 2))
        self.disp2["text"] = str(round(y, 2))
        self.disp3["text"] = str(round(z, 2)) + "%"
        self.disp4["text"] = str(round(w, 2)) + "%"
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
style = Style()
w = 805
h = 550
ws = root.winfo_screenwidth()
hs = root.winfo_screenheight()
x = (ws/2) - (w/2)
y = (hs/2) - (h/2) - 60
root.geometry('%dx%d+%d+%d' % (w, h, x, y))
root.configure(background='black')
root.resizable(0,0) #Disable maximize
app = Window(root)
root.mainloop()

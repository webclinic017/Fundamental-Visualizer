#!/usr/bin/env python
from tkinter import *
from tkinter import messagebox
from PIL import Image, ImageTk
from tk_webscraper import req_handle
from tk_data_processing import data_processing, killer
import pandas as pd

class Window(Frame):
    def __init__(self, master=None):
        Frame.__init__(self, master)
        self.master = master
        self.master.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.init_window()
        self.plot()

    def init_window(self):
        self.master.title("Fundamental Visualizer")
        self.pack(fill=BOTH, expand=1)
        self.canvas = Canvas(root, width = 805, height = 55, background="black")
        self.canvas.create_line(100, 0, 100, 55, fill="white")
        self.canvas.create_line(195, 0, 195, 55, fill="white")
        self.canvas.create_line(295, 0, 295, 55, fill="white")
        self.canvas.create_line(403, 0, 403, 55, fill="white")
        self.canvas.create_line(640, 0, 640, 55, fill="white")
        self.canvas.pack()

        self.var_style = StringVar(root)
        self.var_style.set("Base")
        self.var_country = StringVar(root)
        self.var_country.set("USA")
        self.previous_request = []

        self.disp_pe = Label(root, text = '15',background='white')
        self.label_pe = Label(root, text = 'Current  PE',background='black',foreground='white')
        self.disp_pe_norm = Label(root, text = '15',background='white')
        self.label_pe_norm = Label(root, text = 'Normal PE',background='black',foreground='white')
        self.disp_grw = Label(root, text = '15%',background='white')
        self.label_grw = Label(root, text = 'Growth Rate',background='black',foreground='white')
        self.disp_grw_exp = Label(root, text = '15%',background='white')
        self.label_grw_exp = Label(root, text = 'exp. Growth Rate',background='black',foreground='white')
        self.symbol = Entry(root, width = 10)

        self.sdisp = Label(root, text = 'Enter Symbol',background='black',foreground='white')
        self.btn_update = Button(text="Update", command=self.update, height=1, width=6, relief=GROOVE,background='black',foreground='white',activebackground='green',activeforeground='white') #TODO: mouseover

        self.stlye_selection = OptionMenu(root, self.var_style,"Base", "PE15", "PEG85","PE-Plot","REIT") #TODO: Implement PEGC
        self.country_selection = OptionMenu(root, self.var_country,"USA", "Germany", "Hongkong", "Japan", "France", "Canada", "UK", "Switzerland", "Australia","Korea","Netherlands","Spain","Russia","Italy","Belgium","Mexiko","Sweden","Norway","Finland","Denmark") #Austria, Poland
        self.stlye_selection.config(background='black',foreground='white',relief=FLAT,activebackground='green',activeforeground='white')
        self.country_selection.config(background='black',foreground='white',relief=FLAT,activebackground='green',activeforeground='white')

        self.canvas.create_window(50, 41, window=self.disp_pe)
        self.canvas.create_window(50, 17, window=self.label_pe)
        self.canvas.create_window(150, 41, window=self.disp_pe_norm)
        self.canvas.create_window(150, 17, window=self.label_pe_norm)
        self.canvas.create_window(240, 41, window=self.disp_grw)
        self.canvas.create_window(240, 17, window=self.label_grw)
        self.canvas.create_window(350, 41, window=self.disp_grw_exp)
        self.canvas.create_window(350, 17, window=self.label_grw_exp)

        self.canvas.create_window(470, 29, window=self.stlye_selection)
        self.canvas.create_window(570, 29, window=self.country_selection)
        self.canvas.create_window(690, 41, window=self.symbol)
        self.canvas.create_window(690, 17, window=self.sdisp)
        self.canvas.create_window(765, 29, window=self.btn_update)

    def update(self):
        data_request = [self.var_country.get(),self.symbol.get().upper(),self.var_style.get()]
        print("Request: ",data_request)
        #print("Previous request: ",self.previous_request)
        if data_request[:2] != self.previous_request[:2] or self.previous_request == []:
            print("Requesting data...")
            self.df_daily,self.df_yearly,self.df_est,self.currency = req_handle(*data_request[:2])
            self.previous_request = data_request
            print("Data received.")

        print("Processing data...")
        processing_request = [self.df_daily,self.df_yearly,self.df_est,*data_request[1:],self.currency]
        print(processing_request)
        pe,pe_norm,grw,grw_exp = data_processing(*processing_request)
        self.disp_pe["text"] = str(round(pe, 2))
        self.disp_pe_norm["text"] = str(round(pe_norm, 2))
        self.disp_grw["text"] = str(round(grw, 2)) + "%"
        self.disp_grw_exp["text"] = str(round(grw_exp, 2)) + "%"
        self.plot()
        print("Data processed.")

    def plot(self):
        try:
            load = Image.open("plot.png")
            render = ImageTk.PhotoImage(load)
            img = Label(self, image=render)
            img.image = render
            img.place(x=0, y=0)
        except Exception as ex:
            pass

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
y = (hs/2) - (h/2) - 60
root.geometry('%dx%d+%d+%d' % (w, h, x, y))
root.configure(background='black')
root.resizable(0,0) #Disable maximize
app = Window(root)
root.mainloop()
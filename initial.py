import tkinter as tk
from tkinter import filedialog

from screen import Screen

class Initial(Screen):
    def __init__(self, root, controller, data):
        super().__init__(root, controller, data)
        
    def on_loadfromcsv(self):
        global filePaths
        filePaths = filedialog.askopenfilenames(title='Select The CSVs')
        self.data.get_data_from_csv(filePaths)
        self.controller.show_extraction()
                    
    def gui(self):
        for child in self.root.winfo_children(): child.destroy()
    
        loadfromcsv = tk.Button(self.root,text='Load from CSV', command=self.data.on_loadfromcsv)
        loadfromcsv.pack(expand=True, fill=tk.BOTH)
        
        loadfromdatabase = tk.Button(self.root,text='Load from Database', command=self.data.on_load_from_database)
        loadfromdatabase.pack(expand=True, fill=tk.BOTH)
        
        exit = tk.Button(self.root, text='Exit', command=self.controller.exit)
        exit.pack(expand=True, fill=tk.BOTH)
        
        self.root.mainloop()
    
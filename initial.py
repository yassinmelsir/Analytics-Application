import tkinter as tk
from tkinter import filedialog

from screen import Screen

class Initial(Screen):
    def __init__(self, controller):
        super().__init__(controller)
    
        for child in self.root.winfo_children(): child.destroy()
    
        loadfromcsv = tk.Button(self.root,text='Load from CSV', command=self.on_load_from_csv)
        loadfromcsv.pack(expand=True, fill=tk.BOTH)
        
        loadfromdatabase = tk.Button(self.root,text='Load from Database', command=self.on_load_from_database)
        loadfromdatabase.pack(expand=True, fill=tk.BOTH)
        
        exit = tk.Button(self.root, text='Exit', command=self.controller.exit)
        exit.pack(expand=True, fill=tk.BOTH)
        
        self.root.mainloop()
        
    def on_load_from_csv(self):
        global filePaths
        filePaths = filedialog.askopenfilenames(title='Select The CSVs')
        if len(filePaths) == 2: self.data.get_data_from_csv(filePaths)
        if self.data_exists(): self.controller.show_extraction()
        else: self.popup_dialog('Error','Data did not load!')
                    
    
        
    
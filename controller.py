from initial import Initial
from extraction import Extraction
from cleaning import Cleaning
from analysis import Analysis
from data import Data

import tkinter as tk

class Controller():
    def __init__(self, root, data):
        self.root = root
        self.data = data
    def show_initial(self):
        Initial(self.root,self.data)
                
    def show_extraction(self):
        Extraction(self.root, self.data)
        
    def show_cleaning(self):
        Cleaning(self.root, self.data)
        
    def show_analysis(self):
        Analysis(self.root, self.data)
        
    def exit(self):
        root.destroy()
            
root = tk.Tk()
controller = Controller(root)
controller.show_extraction()
root.mainloop()



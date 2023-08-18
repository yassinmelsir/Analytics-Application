from initial import Initial
from extraction import Extraction
from cleaning import Cleaning
from analysis import Analysis
from data import Data
from _config import server_address, database_name
import tkinter as tk

class Controller():
    def __init__(self, root, data):
        self.root = root
        self.data = data
    def __destroy_root_children(self):
        for child in self.root.winfo_children(): child.destroy()
    
    def show_initial(self):
        self.__destroy_root_children()
        Initial(self)
                
    def show_extraction(self):
        self.__destroy_root_children()
        Extraction(self)
        
    def show_cleaning(self):
        self.__destroy_root_children()
        Cleaning(self)
        
    def show_analysis(self):
        self.__destroy_root_children()
        Analysis(self)
        
    def exit(self):
        self.root.destroy()
            
root = tk.Tk()
data = Data(server_address, database_name)
controller = Controller(root, data)
controller.show_initial()
root.mainloop()



import tkinter as tk
from tkinter import messagebox
import pandas as pd

class Screen():
    def __init__(self, controller):
        self.root = controller.root
        self.controller = controller
        self.data = controller.data

    def data_exists(self):
        df = self.data.get_data()
        if isinstance(df, pd.DataFrame):
            return not df.empty
        return False
    
    def popup_dialog(self,title,message):
        messagebox.showinfo(title, message)

    def destroy_children(self):
        for child in self.root.winfo_children(): child.destroy()
        
    def on_load_from_database(self):
        def on_click():
            self.data.load_from_database(listbox.get(listbox.curselection()))
            # if data exists
            if self.data_exists(): self.controller.show_analysis()
            else: 
                self.popup_dialog('Error','Did Not Load')
                dialog.destroy()
                
            
        dialog = tk.Toplevel(self.root)
        listbox = tk.Listbox(dialog)
        
        collections = self.data.get_collections()
        for collection in collections: listbox.insert(tk.END, collection)
        
        button = tk.Button(dialog, text='Load Selected File',command=on_click)
        
        listbox.pack(fill=tk.BOTH)
        button.pack(fill=tk.BOTH)

    def on_save_to_database(self):
        def on_click():
            result = self.data.save_to_database(entry.get())
            message = 'Successfully saved!'if result.acknowledged else 'Failed to save!'
            self.popup_dialog('Mongo Response', message)
            dialog.destroy() 
            
        dialog = tk.Toplevel(self.root)
        entry = tk.Entry(dialog)
        
        button = tk.Button(dialog, text='Save File As..',command=on_click)
        
        entry.pack(fill=tk.BOTH)
        button.pack(fill=tk.BOTH)  
        
    # def dialog_box(self):
    #     messagebox.showerror("Error", "File not found")
        
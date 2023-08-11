import tkinter as tk

class Screen():
    def __init__(self, root, controller, data):
        self.root = root
        self.controller = controller
        self.data = data

    def destroy_children(self):
        for child in self.root.winfo_children(): child.destroy()
        
    # def dialog_box(self):
    #     messagebox.showerror("Error", "File not found")
        
    def on_load_from_database(self):
        def on_click():
            self.data.load_from_database(listbox.get(listbox.curselection()))
            self.controller.show_cleaning()
            
        dialog = tk.Toplevel(self.root)
        listbox = tk.Listbox(dialog)
        
        collections = self.data.get_collections()
        for collection in collections: listbox.insert(tk.END, collection)
        
        button = tk.Button(dialog, text='Load Selected File',command=on_click)
        
        listbox.pack(fill=tk.BOTH)
        button.pack(fill=tk.BOTH)

    def on_save_to_database(self):
        def on_click():
            self.data.save_to_database(entry.get())
            dialog.destroy() 
            
        dialog = tk.Toplevel(self.root)
        entry = tk.Entry(dialog)
        
        button = tk.Button(dialog, text='Save File As..',command=on_click)
        
        entry.pack(fill=tk.BOTH)
        button.pack(fill=tk.BOTH)  
        
import tkinter as tk

from _config import coltoextract, columnstoextract

from screen import Screen

class Extraction(Screen):
    def __init__(self, root, controller, data):
        super().__init__(root, controller, data)
        self.groupstoextract = None
        self.data_df = self.data.get_data()

        self.controlbuttons()
        
        
        
        #extraction
        extraction = tk.Frame(root, relief='groove', borderwidth=1)
        self.extractFrame = tk.Frame(extraction, relief='groove', borderwidth=1)
        self.groupselection = tk.Entry(self.extractFrame)
        self.groupbox = tk.Listbox(self.extractFrame, selectmode=tk.MULTIPLE)
        if self.data_df: 
            for group in self.data_df[coltoextract].unique(): self.groupbox.insert(tk.END, group)
        
        self.extract_buttons()
        
        extraction.pack(fill=tk.BOTH)
        
        self.groupselection.pack(fill=tk.BOTH)
        self.extractFrame.pack(expand=True,fill=tk.BOTH, side=tk.LEFT)
        self.groupbox.pack(fill=tk.BOTH)
             
        self.root.mainloop()
        
    def controlbuttons(self):
        controlbuttons = tk.Frame(self.root, relief='groove', borderwidth=1)
        back = tk.Button(controlbuttons, text='Back To Load Screen', command=self.controller.show_initial)
        extractcontinue = tk.Button(controlbuttons, text='Extract and Continue to Cleaning', command=self.on_extract_continue)
        exit = tk.Button(controlbuttons, text='Exit', command=self.controller.exit)
        
        controlbuttons.pack(fill=tk.BOTH)
        back.pack(fill=tk.BOTH, side=tk.LEFT)
        extractcontinue.pack(fill=tk.BOTH, side=tk.LEFT)
        exit.pack(fill=tk.BOTH, side=tk.RIGHT)
        
    def extract_buttons(self):   
        extractSelected = tk.Button(self.extractFrame, text='Extract Selected Groups', command=self.extract_selected)
        extractPreselected = tk.Button(self.extractFrame, text='Extract C18A, C18F and C188', command=lambda: self.extracted_preselected(['C18A', 'C18F', 'C188']))
        extractAll = tk.Button(self.extractFrame, text='Extract All', command=lambda: self.extracted_preselected(self.data_df[coltoextract].unique()))
        clearSelected = tk.Button(self.extractFrame, text='Clear Selections', command=self.clear)
        
        extractSelected.pack(fill=tk.BOTH)
        extractPreselected.pack(fill=tk.BOTH)
        extractAll.pack(fill=tk.BOTH)
        clearSelected.pack(fill=tk.BOTH)        
    
    def extract_selected(self):
        indices = self.groupbox.curselection()
        if len(self.groupselection.get())>0: self.groupselection.delete(0,'end')
        else:
            groupstoextract = [self.groupbox.get(index) for index in indices]
            self.groupselection.insert(tk.END, ','.join(groupstoextract))
            self.data.set_groupstoextract(groupstoextract)
            
    def extracted_preselected(self,groups):
        self.groupselection.insert(tk.END,','.join(groups)); groupstoextract = groups
        self.data.set_groupstoextract(groupstoextract)
        
    def clear(self):
        self.groupselection.delete(0, 'end')
        self.data.set_groupstoextract(None)
        
    def on_extract_continue(self):
        self.data.extract_data()
        self.controller.show_cleaning()
                


        
    
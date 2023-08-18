import tkinter as tk

from _config import col_to_extract

from screen import Screen

class Extraction(Screen):
    def __init__(self, controller):
        super().__init__(controller)
        self.groups_to_extract = None
        self.data_df = self.data.get_data()
        self.control_buttons()
        
        #extraction
            
        self.extraction_frame()
        
        self.extract_buttons()
             
        self.root.mainloop()
        
    def extraction_frame(self):
        global extract_frame, group_box
        extraction = tk.Frame(self.root, relief='groove', borderwidth=1)
        extract_frame = tk.Frame(extraction, relief='groove', borderwidth=1)
        group_box = tk.Listbox(extract_frame, selectmode=tk.MULTIPLE)
        if not self.data_df.empty: 
            for group in self.data_df[col_to_extract].unique(): group_box.insert(tk.END, group)
        
        extraction.pack(fill=tk.BOTH)
        
        extract_frame.pack(expand=True,fill=tk.BOTH, side=tk.LEFT)
        group_box.pack(fill=tk.BOTH)
        
    def control_buttons(self):
        control_buttons = tk.Frame(self.root, relief='groove', borderwidth=1)
        back = tk.Button(control_buttons, text='Back To Load Screen', command=self.controller.show_initial)
        continue_ = tk.Button(control_buttons, text='Continue to Cleaning', command=self.controller.show_cleaning)
        exit = tk.Button(control_buttons, text='Exit', command=self.controller.exit)
        
        control_buttons.pack(fill=tk.BOTH)
        back.pack(fill=tk.BOTH, side=tk.LEFT)
        continue_.pack(fill=tk.BOTH, side=tk.LEFT)
        exit.pack(fill=tk.BOTH, side=tk.RIGHT)
        
    def extract_buttons(self):   
        extract_selected = tk.Button(extract_frame, text='Extract Selected Groups', command=self.extract_selected)
        extract_preselected = tk.Button(extract_frame, text='Extract C18A, C18F and C188', command=lambda: self.extracted_preselected(['C18A', 'C18F', 'C188']))
        extract_all = tk.Button(extract_frame, text='Extract All', command=lambda: self.extracted_preselected(self.data_df[col_to_extract].unique()))
                
        extract_selected.pack(fill=tk.BOTH)
        extract_preselected.pack(fill=tk.BOTH)
        extract_all.pack(fill=tk.BOTH)
    
    def extract_selected(self):
        indices = group_box.curselection()
        if len(indices) > 0:
            groups_to_extract = [group_box.get(index) for index in indices]
            self.data.set_groups_to_extract(groups_to_extract)
            self.data.extract_data()
            self.extract_continue()
        else: self.popup_dialog('Error','No group(s) selected!')
            
    def extracted_preselected(self,groups):
        groups_to_extract = groups
        self.data.set_groups_to_extract(groups_to_extract)
        self.extract_continue()
        
    def extract_continue(self):
        self.data.extract_data()
        self.controller.show_cleaning()
                


        
    
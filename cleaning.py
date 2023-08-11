import pandas as pd
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk
import seaborn as sns
import matplotlib.pyplot as plt

from matplotlib.backends.backend_tkagg import (
FigureCanvasTkAgg)
from matplotlib.figure import Figure

from _config import coltypes, filltypes

from screen import Screen


class Cleaning(Screen):
    def __init__(self, root, controller, data):
        super().__init__(root, controller, data)
        self.working_data = self.data.get_working_data()
                
        self.buttons()
    
        self.dataframe()
        
        
        tools = tk.Frame(self.root)
        tools.pack(expand=True, fill=tk.BOTH)
            
        columns = tk.Frame(tools, relief='groove', borderwidth=1)
        columns.pack(side=tk.LEFT,fill=tk.BOTH)
        columns_box_frame = tk.Frame(columns)
        columns_box_frame.pack(fill=tk.BOTH)
        colums_label = tk.Label(columns_box_frame,text='Select a Column to Clean')
        colums_label.pack(fill=tk.BOTH)
        self.columnsbox = tk.Listbox(columns)
        for column, dytype in self.self.working_data.dtypes.items(): self.columnsbox.insert(tk.END, f'{column}: {dytype}')
        self.columnsbox.pack(fill=tk.BOTH)
            
        fill_frame = tk.Frame(tools, relief='groove', borderwidth=1)
        fill_frame.pack(side=tk.LEFT, anchor='n')
        fill_label = tk.Label(fill_frame, text='Select Method to Fill Missing Values in Column')
        fill_label.pack()
        self.selected_fill = tk.StringVar()
        self.selected_fill.set(filltypes[0])
        for button_text in filltypes:
            radiobutton = tk.Radiobutton(fill_frame, text=button_text, variable=self.selected_fill, value=button_text)
            radiobutton.pack(anchor='w')
        fill_blanks = tk.Button(fill_frame,text='Fill Column Blanks', command=self.on_fill)    
        fill_blanks.pack(anchor='w')
        
        
        replacement_frame = tk.Frame(tools, relief='groove', borderwidth=1)
        replacement_frame.pack(side=tk.LEFT, anchor='n')
        replacement_label = tk.Label(replacement_frame, text='Select a Column to Parse Below')
        replacement_label.pack()
        self.to_replace_label= tk.Label(replacement_frame, text='Enter Value to Mass Replace')
        self.to_replace_label.pack(anchor='w')
        self.to_replace = tk.Entry(replacement_frame)
        self.to_replace.pack(anchor='w')
        self.replace_with_label = tk.Label(replacement_frame, text='Enter Value to Mass Replace With')
        self.replace_with_label.pack(anchor='w')
        self.replace_with = tk.Entry(replacement_frame)
        self.replace_with.pack(anchor='w')
        replace = tk.Button(replacement_frame, text='Apply Change', command=self.on_replace)
        replace.pack(anchor='w')
        
            
        coltype_frame = tk.Frame(tools, relief='groove', borderwidth=1)
        coltype_frame.pack(side=tk.LEFT, anchor='n')
        coltype_label = tk.Label(coltype_frame, text='Change Datatype of Column Below')
        coltype_label.pack()
        self.selected_coltype = tk.StringVar()
        self.selected_coltype.set(coltypes[0])
        for button_text in coltypes:
            radiobutton = tk.Radiobutton(coltype_frame, text=button_text, variable=self.selected_coltype, value=button_text)
            radiobutton.pack(anchor='w')
        set_coltype = tk.Button(coltype_frame,text='Set Column Type', command=self.on_set_type)    
        set_coltype.pack(anchor='w')
        
        rename_frame = tk.Frame(tools, relief='groove', borderwidth=1)
        rename_frame.pack(side=tk.LEFT, anchor='n')
        rename_label = tk.Label(rename_frame, text='Enter a New Name for the Column')
        rename_label.pack()
        self.new_name = tk.Entry(rename_frame)
        self.new_name.pack(anchor='w')
        apply_delimiter = tk.Button(rename_frame, text='Apply New Name', command=self.on_set_name)
        apply_delimiter.pack(anchor='w')
        
        self.root.mainloop()
    
    def update_dataframe_view(self):
        # Delete existing items
        for item in self.tree.get_children():
            self.tree.delete(item)     
        for index, row in self.working_data.iterrows():
            self.tree.insert('', index, values=list(row))

    def on_reset(self):
        self.working_data = self.data.get_working_data()
        self.update_dataframe_view()
        
    def on_apply_preset(self):
        self.data.preset_clean_data()
        self.update_dataframe_view()
        
    def on_delete_rows(self):
        selected_rows = self.tree.selection()
        for row in selected_rows: self.tree.delete(row)
        self.working_data = self.working_data[~self.working_data['NGR'].isin(selected_rows)]
    
    def on_fill(self):
        selection_index = self.columnsbox.curselection()
        if selection_index: 
            fill, column = self.selected_fill.get(), self.working_data.columns.values[self.columnsbox.curselection()[0]]
            na = 0 if fill == 'Fill With 0' else self.working_data[column].mode().iloc[0]
            self.working_data[column] = self.working_data[column].fillna(na)
        print(self.working_data)
        self.update_dataframe_view()
        
    def on_replace(self):
        selection_index = self.columnsbox.curselection()
        if selection_index:
            column = self.working_data.columns.values[selection_index[0]]
            self.working_data[column] = self.working_data[column].apply(lambda x: x.replace(f'{self.to_replace.get()}',f'{self.replace_with.get()}'))
            print(self.working_data[column])
        self.update_dataframe_view()
        
    def on_set_type(self):
        selection_index = self.columnsbox.curselection()
        if selection_index:
            column = self.working_data.columns.values[selection_index[0]]
            self.working_data[column] = self.working_data[column].astype(self.selected_coltype.get().lower())    
            print(self.working_data.dtypes())
        self.update_dataframe_view()
    
    def on_set_name(self):
        selection_index = self.columnsbox.curselection()
        if selection_index:
            column, name = self.working_data.columns.values[selection_index[0]], self.new_name.get()
            self.working_data.rename(columns={column:name}, inplace=True)
            print(self.working_data.columns)
        self.update_dataframe_view()
    
    def on_save(self):
        self.data.set_working_data(self.working_data)
        self.data.on_save_to_database()
        
    def on_continue_to(self):
        self.data.set_working_data(self.working_data)
        self.controller.show_analysis()
        
    def dataframe(self):
        dataframe = tk.Frame(self.root)
        dataframe.pack(expand=True, fill=tk.BOTH)
        self.self.tree = ttk.self.Treeview(dataframe, selectmode='extended')
        self.tree.place()
        
        vertical_scrollbar = ttk.Scrollbar(dataframe, orient='vertical', command=self.tree.yview)
        horizontal_scrollbar = ttk.Scrollbar(dataframe, orient='horizontal', command=self.tree.xview)
        
        self.tree.configure(yscrollcommand=vertical_scrollbar.set)
        self.tree.configure(xscrollcommand=horizontal_scrollbar.set)
        
        self.tree['columns'] = list(self.working_data.columns)
        self.tree['show'] = 'headings'

        for column in self.working_data.columns:
            self.tree.heading(column, text=column)
            self.tree.column(column, width=50)

        for index, row in self.working_data.iterrows():
            self.tree.insert('', index, values=list(row))

        self.tree.pack(expand=True, fill=tk.BOTH)
        vertical_scrollbar.pack(side='right', fill='y')
        horizontal_scrollbar.pack(side='bottom', fill='x')
        
        delete_rows = tk.Button(dataframe, text='Delete Selected Rows', command=self.on_delete_rows)
        delete_rows.pack(side=tk.LEFT)
    
    def buttons(self):
        buttons = tk.Frame(self.root)
        buttons.pack(fill=tk.BOTH)
        
        exit = tk.Button(buttons, text='Exit', command=self.controller.exit())
        exit.pack(side=tk.RIGHT, fill=tk.BOTH)    
        
        reset = tk.Button(buttons, text='Reset', command=self.on_reset)
        reset.pack(side=tk.LEFT, fill=tk.BOTH)
        
        apply_preset = tk.Button(buttons, text='Apply Preset Cleaning' ,command=self.on_apply_preset)
        apply_preset.pack(side=tk.LEFT, fill=tk.BOTH)
        
        save = tk.Button(buttons,text='Save to Database', command=self.on_save)
        save.pack(side=tk.LEFT, fill=tk.BOTH)
        
        continue_to = tk.Button(buttons,text='Continue to Visualization', command=self.on_continue_to)
        continue_to.pack(side=tk.LEFT, fill=tk.BOTH)
        
   
    
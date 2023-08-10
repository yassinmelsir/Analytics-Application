import pandas as pd
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk
import seaborn as sns
import matplotlib.pyplot as plt
from pymongo import MongoClient

from matplotlib.backends.backend_tkagg import (
FigureCanvasTkAgg)
from matplotlib.figure import Figure

serverAddress = 'mongodb://127.0.0.1:27017/?directConnection=true&serverSelectionTimeoutMS=2000&appName=mongosh+1.10.3' # fill with your mongo server address
databaseName = 'multiplexes' # give new database name
# collectionName  = '3names1' # give new collection name

# filePath = '/Users/yme/Code/AdvancedProgramming/SummativeAssessment/top_3_names_per_sex.csv'
# data, workingdata = pd.read_csv(filePath), pd.read_csv(filePath)

#filtering
coltofilter = 'NGR'
criteriatoremove = ['NZ02553847', 'SE213515', 'NT05399374', 'NT252665908']

#extraction
coltoextract = 'EID'
# groupstoextract =  None
groupstoextract = ['C18A', 'C18F', 'C188']
columnstoextract = [
        'EID', 'NGR', 'Site','Longitude/Latitude', 'Site Height', 'In-Use Ae Ht',
        'In-Use ERP Total', 'Freq.', 'Block','Serv Label1',
       'Serv Label2', 'Serv Label3', 'Serv Label4','Serv Label10', 'Date']

#renaming
columnstorename = {'In-Use Ae Ht': 'Aerial Height(m)', 'In-Use ERP Total': 'Power(kW)'}

#cleaning
filltypes = ['Mode Imputation', 'Fill With 0'] 
coltypes = ['Int', 'Float', 'Str']

#stats
statscolumn, groupscolumn, visualizations, statistics = 'Power(kW)', 'EID', ['Information','Correlation'], ['mean', 'std', 'min']

#graphs
graph_type = 'Information'


#initial screen
def initial_screen():
    global root
    loadfromcsv = tk.Button(root,text='Load from CSV', command=on_loadfromcsv)
    loadfromcsv.pack(expand=True, fill=tk.BOTH)
    
    loadfromdatabase = tk.Button(root,text='Load from Database', command=on_load_from_database)
    loadfromdatabase.pack(expand=True, fill=tk.BOTH)
    
    exit = tk.Button(root, text='Exit', command=on_exit)
    exit.pack(expand=True, fill=tk.BOTH)
    
    def on_loadfromcsv():
        global data, workingdata, filePaths
        filePaths = filedialog.askopenfilenames(title='Select The CSVs')
        destroy_children()
        get_data_from_csv()
        extraction_screen()  

# extraction screen    
def extraction_screen():
    global groupstoextract
    
    def extract_selected():
        global groupstoextract
        indices = groupbox.curselection()
        if len(groupselection.get())>0: groupselection.delete(0,'end')
        else:
            groupstoextract = [groupbox.get(index) for index in indices]
            groupselection.insert(tk.END, ','.join(groupstoextract))
            
    def extracted_preselected(groups):
        global groupstoextract
        groupselection.insert(tk.END,','.join(groups)); groupstoextract = groups
        
    def clear():
        groupselection.delete(0, 'end')
        
    def on_backtoloadscreen():
        destroy_children()
        initial_screen() 
        
    def on_extractcontinue():
        destroy_children()
        cleaning_screen()
        
    # control buttons
    controlbuttons = tk.Frame(root, relief='groove', borderwidth=1)
    back = tk.Button(controlbuttons, text='Back To Load Screen', command=on_backtoloadscreen)
    extractcontinue = tk.Button(controlbuttons, text='Extract and Continue to Cleaning', command=on_extractcontinue)
    exit = tk.Button(controlbuttons, text='Exit', command=on_exit)
    
    cleaningoptions = tk.Frame(root, relief='groove', borderwidth=1)
    
    #extraction
    extractFrame = tk.Frame(cleaningoptions, relief='groove', borderwidth=1)
    groupselection = tk.Entry(extractFrame)
    groupbox = tk.Listbox(extractFrame, selectmode=tk.MULTIPLE)
    for group in data[coltoextract].unique(): groupbox.insert(tk.END, group)
    
    
        
    extractSelected = tk.Button(extractFrame, text='Extract Selected Groups', command=extract_selected)
    extractPreselected = tk.Button(extractFrame, text='Extract C18A, C18F and C188', command=lambda: extracted_preselected(['C18A', 'C18F', 'C188']))
    extractAll = tk.Button(extractFrame, text='Extract All', command=lambda: extracted_preselected(data[coltoextract].unique()))
    clearSelected = tk.Button(extractFrame, text='Clear Selections', command=clear)   
    
    
    controlbuttons.pack(fill=tk.BOTH)
    back.pack(fill=tk.BOTH, side=tk.LEFT)
    extractcontinue.pack(fill=tk.BOTH, side=tk.LEFT)
    exit.pack(fill=tk.BOTH, side=tk.RIGHT)
    
    cleaningoptions.pack(fill=tk.BOTH)
    
    groupselection.pack(fill=tk.BOTH)
    extractFrame.pack(expand=True,fill=tk.BOTH, side=tk.LEFT)
    groupbox.pack(fill=tk.BOTH)
    extractSelected.pack(fill=tk.BOTH)
    extractPreselected.pack(fill=tk.BOTH)
    extractAll.pack(fill=tk.BOTH)
    clearSelected.pack(fill=tk.BOTH)
    
# cleaning screen
def cleaning_screen():
    global root, data, workingdata

    def reload():
        for child in root.winfo_children(): child.destroy()
        cleaning_screen()

    def on_reset():
        extract_data()
        reload()
        
    def on_apply_preset():
        clean_data()
        reload()
        
    def on_delete_rows():
        global workingdata
        selected_rows = tree.selection()
        for row in selected_rows: tree.delete(row)
        workingdata = workingdata[~workingdata['NGR'].isin(selected_rows)]
    
    def on_fill():
        global workingdata
        selection_index = columnsbox.curselection()
        if selection_index: 
            fill, column = selected_fill.get(), workingdata.columns.values[columnsbox.curselection()[0]]
            na = 0 if fill == 'Fill With 0' else workingdata[column].mode().iloc[0]
            workingdata[column] = workingdata[column].fillna(na)
        print(workingdata)
        reload()
        
    def on_replace():
        global workingdata
        selection_index = columnsbox.curselection()
        if selection_index:
            column = workingdata.columns.values[selection_index[0]]
            workingdata[column] = workingdata[column].apply(lambda x: x.replace(f'{to_replace.get()}',f'{replace_with.get()}'))
            print(workingdata[column])
        reload()
        
    def on_set_type():
        global workingdata
        selection_index = columnsbox.curselection()
        if selection_index:
            column = workingdata.columns.values[selection_index[0]]
            workingdata[column] = workingdata[column].astype(selected_coltype.get().lower())    
            print(workingdata.dtypes())
        reload()
    
    def on_set_name():
        global workingdata
        selection_index = columnsbox.curselection()
        if selection_index:
            column, name = workingdata.columns.values[selection_index[0]], new_name.get()
            workingdata.rename(columns={column:name}, inplace=True)
            print(workingdata.columns)
        reload()
    
    def on_save():
        on_save_to_database()
        
    def on_continue_to():
        destroy_children()
        visualization_screen()
        
    def dataframe():
        global tree, workingdata
        dataframe = tk.Frame(root)
        dataframe.pack(expand=True, fill=tk.BOTH)
        tree = ttk.Treeview(dataframe, selectmode='extended')
        tree.place()
        
        vertical_scrollbar = ttk.Scrollbar(dataframe, orient='vertical', command=tree.yview)
        horizontal_scrollbar = ttk.Scrollbar(dataframe, orient='horizontal', command=tree.xview)
        
        tree.configure(yscrollcommand=vertical_scrollbar.set)
        tree.configure(xscrollcommand=horizontal_scrollbar.set)
        
        tree['columns'] = list(workingdata.columns)
        tree['show'] = 'headings'

        for column in workingdata.columns:
            tree.heading(column, text=column)
            tree.column(column, width=50)

        for index, row in workingdata.iterrows():
            tree.insert('', index, values=list(row))

        tree.pack(expand=True, fill=tk.BOTH)
        vertical_scrollbar.pack(side='right', fill='y')
        horizontal_scrollbar.pack(side='bottom', fill='x')
        
        delete_rows = tk.Button(dataframe, text='Delete Selected Rows', command=on_delete_rows)
        delete_rows.pack(side=tk.LEFT)
    
    def buttons():
        buttons = tk.Frame(root)
        buttons.pack(fill=tk.BOTH)
        
        exit = tk.Button(buttons, text='Exit', command=on_exit)
        exit.pack(side=tk.RIGHT, fill=tk.BOTH)    
        
        reset = tk.Button(buttons, text='Reset', command=on_reset)
        reset.pack(side=tk.LEFT, fill=tk.BOTH)
        
        apply_preset = tk.Button(buttons, text='Apply Preset Cleaning' ,command=on_apply_preset)
        apply_preset.pack(side=tk.LEFT, fill=tk.BOTH)
        
        save = tk.Button(buttons,text='Save to Database', command=on_save)
        save.pack(side=tk.LEFT, fill=tk.BOTH)
        
        continue_to = tk.Button(buttons,text='Continue to Visualization', command=on_continue_to)
        continue_to.pack(side=tk.LEFT, fill=tk.BOTH)
    
    buttons()
    
    dataframe()
    
    
    tools = tk.Frame(root)
    tools.pack(expand=True, fill=tk.BOTH)
        
    columns = tk.Frame(tools, relief='groove', borderwidth=1)
    columns.pack(side=tk.LEFT,fill=tk.BOTH)
    columns_box_frame = tk.Frame(columns)
    columns_box_frame.pack(fill=tk.BOTH)
    colums_label = tk.Label(columns_box_frame,text='Select a Column to Clean')
    colums_label.pack(fill=tk.BOTH)
    columnsbox = tk.Listbox(columns)
    for column, dytype in workingdata.dtypes.items(): columnsbox.insert(tk.END, f'{column}: {dytype}')
    columnsbox.pack(fill=tk.BOTH)
        
    fill_frame = tk.Frame(tools, relief='groove', borderwidth=1)
    fill_frame.pack(side=tk.LEFT, anchor='n')
    fill_label = tk.Label(fill_frame, text='Select Method to Fill Missing Values in Column')
    fill_label.pack()
    selected_fill = tk.StringVar()
    selected_fill.set(filltypes[0])
    for button_text in filltypes:
        radiobutton = tk.Radiobutton(fill_frame, text=button_text, variable=selected_fill, value=button_text)
        radiobutton.pack(anchor='w')
    fill_blanks = tk.Button(fill_frame,text='Fill Column Blanks', command=on_fill)    
    fill_blanks.pack(anchor='w')
    
    
    replacement_frame = tk.Frame(tools, relief='groove', borderwidth=1)
    replacement_frame.pack(side=tk.LEFT, anchor='n')
    replacement_label = tk.Label(replacement_frame, text='Select a Column to Parse Below')
    replacement_label.pack()
    to_replace_label= tk.Label(replacement_frame, text='Enter Value to Mass Replace')
    to_replace_label.pack(anchor='w')
    to_replace = tk.Entry(replacement_frame)
    to_replace.pack(anchor='w')
    replace_with_label = tk.Label(replacement_frame, text='Enter Value to Mass Replace With')
    replace_with_label.pack(anchor='w')
    replace_with = tk.Entry(replacement_frame)
    replace_with.pack(anchor='w')
    replace = tk.Button(replacement_frame, text='Apply Change', command=on_replace)
    replace.pack(anchor='w')
    
        
    coltype_frame = tk.Frame(tools, relief='groove', borderwidth=1)
    coltype_frame.pack(side=tk.LEFT, anchor='n')
    coltype_label = tk.Label(coltype_frame, text='Change Datatype of Column Below')
    coltype_label.pack()
    selected_coltype = tk.StringVar()
    selected_coltype.set(coltypes[0])
    for button_text in coltypes:
        radiobutton = tk.Radiobutton(coltype_frame, text=button_text, variable=selected_coltype, value=button_text)
        radiobutton.pack(anchor='w')
    set_coltype = tk.Button(coltype_frame,text='Set Column Type', command=on_set_type)    
    set_coltype.pack(anchor='w')
    
    rename_frame = tk.Frame(tools, relief='groove', borderwidth=1)
    rename_frame.pack(side=tk.LEFT, anchor='n')
    rename_label = tk.Label(rename_frame, text='Enter a New Name for the Column')
    rename_label.pack()
    new_name = tk.Entry(rename_frame)
    new_name.pack(anchor='w')
    apply_delimiter = tk.Button(rename_frame, text='Apply New Name', command=on_set_name)
    apply_delimiter.pack(anchor='w')
    
        
def visualization_screen():
    def buttons():
        global selected_visualization, checkbox_variables, graph_type
        frame = tk.Frame(root)
        frame.pack(expand=True, fill=tk.BOTH)
        
        radiobutton_frame = tk.Frame(frame, relief='groove', borderwidth=1)
        radiobutton_frame.pack(side=tk.LEFT,fill=tk.BOTH)
        checkbox_frame = tk.Frame(frame, relief='groove', borderwidth=1)
        checkbox_frame.pack(side=tk.LEFT,fill=tk.BOTH)
        
        radiolabel = tk.Label(radiobutton_frame, text='Visualizations: ')
        radiolabel.pack(side=tk.LEFT,fill=tk.BOTH)
        selected_visualization = tk.StringVar()
        selected_visualization.set(graph_type)
        for visualization in visualizations: 
            radio_button = tk.Radiobutton(radiobutton_frame,text=visualization,variable=selected_visualization, value=visualization, command=update_visualization)
            radio_button.pack(side=tk.LEFT,fill=tk.BOTH)
        
        checkboxlabel = tk.Label(checkbox_frame, text='Groups: ')
        checkboxlabel.pack(side=tk.LEFT,fill=tk.BOTH)
        groups, checkbox_variables = groupstoextract, {}
        
        for group in groups:
            checkbox_variable = tk.BooleanVar(value=True)
            checkbox_variables[group] = checkbox_variable
            
            checkbox = tk.Checkbutton(checkbox_frame, text=group, variable=checkbox_variable, command=update_data_range)
            checkbox.pack(side=tk.LEFT,fill=tk.BOTH)
            
        exit = tk.Button(frame, text='Exit', command=on_exit)
        exit.pack(side=tk.RIGHT, fill=tk.BOTH)
        
        load = tk.Button(frame,text='Load from Database', command=on_load_from_database)
        load.pack(side=tk.RIGHT, fill=tk.BOTH)
        
        save = tk.Button(frame,text='Save to Database', command=on_save_to_database)
        save.pack(side=tk.RIGHT, fill=tk.BOTH)
        
    def update_visualization():
        global graph_type
        graph_type = selected_visualization.get()
        destroy_children()
        visualization_screen()

    def update_data_range():
        global workingdata, selected_visualization
        selected_groups = [group for group, selected in checkbox_variables.items() if selected.get()]
        workingdata = workingdata[data[groupscolumn].isin(selected_groups)]
        destroy_children()
        visualization_screen()

    def information_graph():
        sns.scatterplot(x='Longitude', y='Latitude', hue='EID', data=graph_data, ax=ax)
    
        for _, row in graph_data.iterrows(): 
            label = row['Site'] + '\n' + str(row['Freq.']) + '\n' + row['Block'] + '\n' + row['Stations']
            ax.text(row['Longitude'], row['Latitude'], label)
        ax.legend(loc='upper right')
        plt.tight_layout()
    
    def graph_information():
        global workingdata, ax, canvas, graph_data
        fig = Figure(figsize=(10,8), dpi=100)
        ax = fig.add_subplot()
        information_graph()
        canvas = FigureCanvasTkAgg(fig, master=root)
        canvas.draw()
        canvas.get_tk_widget().pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
    def regraph_information():
        global ax, canvas, graph_data
        ax.clear()
        information_graph()
        canvas.draw()
        
    def graph_correlation():
        global workingdata, ax, canvas, graph_data
        fig = Figure(figsize=(10,8), dpi=100)
        ax = fig.add_subplot()
        sns.barplot(x='NGR', y='Average Length Label', hue='Block', data=graph_data, ax=ax)
        ax.set_xticklabels(ax.get_xticklabels(), rotation=45, fontsize=10)
        plt.tight_layout()
        ax.legend(loc='upper right')
        canvas = FigureCanvasTkAgg(fig, master=root)
        canvas.draw()
        canvas.get_tk_widget().pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
    def regraph_correlation():
        global ax, canvas, workingdata
        # 
        ax.clear()
        sns.barplot(x='NGR', y='Average Length Label', hue='Block', data=graph_data, ax=ax)
        ax.set_xticklabels(ax.get_xticklabels(), rotation=45, fontsize=10)
        plt.tight_layout()
        ax.legend(loc='upper right')
        canvas.draw()
        
    def gen_graph_data():
        def convert_to_longitude(coord):
            degrees = int(coord[:3])
            minutes = float(coord[4:6])
            seconds = float(coord[7:9])
            direction = coord[3]

            # Convert to decimal
            decimal_degrees = degrees + minutes / 60 + seconds / 3600

            # Check direction
            if direction == 'W':
                decimal_degrees = -decimal_degrees

            return decimal_degrees
        
        def convert_to_latitude(coord):
            degrees = int(coord[10:12])
            minutes = float(coord[13:15])
            seconds = float(coord[16:18])
            direction = coord[12]

            # Convert to decimal
            decimal_degrees = degrees + minutes / 60 + seconds / 3600

            # Check direction
            if direction == 'S':
                decimal_degrees = -decimal_degrees

            return decimal_degrees
        global workingdata, graph_data
        graph_data = workingdata.copy()
        graph_data['Longitude'], graph_data['Latitude'] = graph_data['Longitude/Latitude'].apply(convert_to_longitude), graph_data['Longitude/Latitude'].apply(convert_to_latitude)         
        graph_data['Stations'] = graph_data['Serv Label1'] +'\n'+ graph_data['Serv Label2'] +'\n' + graph_data['Serv Label3'] +'\n' + graph_data['Serv Label4'] +'\n' + graph_data['Serv Label10']
        
        labels = ['Serv Label1','Serv Label2', 'Serv Label3', 'Serv Label4','Serv Label10']
        for col in labels:
            graph_data[col+'(ul)'] = graph_data[col].apply(len)
            
        ul_labels = [label+'(ul)' for label in labels]
        
        graph_data['Average Length Label'] = (graph_data[ul_labels].sum(axis=1))/len(ul_labels)
        

    def generate_statistics_widget():
        description_year, description_height = compute_stats()
        statistics_frame(description_year, 'Year'), statistics_frame(description_height, 'Height')
        print('Description Year', description_year)
        print('Description Height', description_height)
        
    def statistics_frame(description, constraint):
        global numericaldataframe
        numericaldataframe = tk.Frame(root)
        numericaldataframe.pack(expand=True, fill=tk.BOTH)
        
        constraint_frame = tk.Frame(numericaldataframe, relief='groove', borderwidth=1)
        constraint_label = tk.Label(constraint_frame, text=constraint+' Constraint: ')
        constraint_label.pack(side=tk.LEFT, fill=tk.BOTH), constraint_frame.pack(side=tk.LEFT, expand=True, fill=tk.BOTH)
        
        for statistic in statistics:
            statisticframe = tk.Frame(numericaldataframe, relief='groove', borderwidth=1)
            statisticlabel = tk.Label(statisticframe, text=statistic.capitalize() + ': ' + str(description[statistic]))
            
            statisticlabel.pack(side=tk.LEFT, fill=tk.BOTH), statisticframe.pack(side=tk.LEFT, expand=True, fill=tk.BOTH)
                
    def compute_stats():
        global workingdata
        year_constraint, height_constraint = 2001, 75
        workingdata['Date'] = pd.to_datetime(workingdata['Date'], format='%d/%m/%Y')
        filter_by_year, filter_by_height = workingdata[workingdata['Date'].dt.year >= year_constraint], workingdata[workingdata['Site Height'] >= height_constraint]
        return filter_by_year[statscolumn].describe(), filter_by_height[statscolumn].describe()
    
    
    gen_graph_data()
    buttons()
    generate_statistics_widget()
    graph_information() if graph_type == 'Information' else graph_correlation()
    print('Working Data:', workingdata)
    print('Graph Data:', graph_data)
    

#global functions
def on_exit():
    global root
    root.destroy()

def destroy_children():
    for child in root.winfo_children(): child.destroy()
    
def dialog_box():
    messagebox.showerror("Error", "File not found")
    
    
def on_load_from_database():
    def on_click():
        load_from_database(listbox.get(listbox.curselection()))
        destroy_children()
        cleaning_screen()
        
    dialog = tk.Toplevel(root)
    listbox = tk.Listbox(dialog)
    
    collections = get_collections()
    for collection in collections: listbox.insert(tk.END, collection)
    
    button = tk.Button(dialog, text='Load Selected File',command=on_click)
    
    listbox.pack(fill=tk.BOTH)
    button.pack(fill=tk.BOTH)

def on_save_to_database():
    def on_click():
        save_to_database(entry.get())
        dialog.destroy() 
        
    dialog = tk.Toplevel(root)
    entry = tk.Entry(dialog)
    
    button = tk.Button(dialog, text='Save File As..',command=on_click)
    
    entry.pack(fill=tk.BOTH)
    button.pack(fill=tk.BOTH)  
    
    #database functions
def get_collection(collectionName):
    client = MongoClient(serverAddress)
    database = client[databaseName]
    return database[collectionName], client
    
def get_collections():
    client = MongoClient(serverAddress)
    database = client[databaseName]
    collection = database.list_collection_names()
    client.close()
    return collection

def save_to_database(collectionName):
    global data
    mongodata = data.to_dict(orient='records')
    collection, client = get_collection(collectionName)
    collection.insert_many(mongodata)
    client.close()
    
def load_from_database(collectionName):
    global data, workingdata
    collection, client = get_collection(collectionName)
    results = collection.find()
    formatted_results = list(results)
    data, workingdata = pd.DataFrame(formatted_results), pd.DataFrame(formatted_results)
    client.close()
    
    
# non global function to move later
def clean_data():
    global workingdata
    
     # 1. remove NGRS NZ02553847, SE213515, NT05399374 and NT252665908 from possible outputs
    cleaned = workingdata[~workingdata[coltofilter].isin(criteriatoremove)] # filter out the NGRS: NZ02553847, SE213515, NT05399374 and NT252665908
    
    # 2. c.Please note that: In-Use Ae Ht, In-Use ERP Total  will need the following new header after extraction: 
    # Aerial height(m), Power(kW) respectively.
    cleaned.rename(columns=columnstorename, inplace=True)    

    # remove anomalies, and reclassify
    column_to_parse = 'Power(kW)'
    cleaned[column_to_parse] = cleaned[column_to_parse].apply(lambda x: x.replace(',',''))
    cleaned[column_to_parse] = cleaned[column_to_parse].apply(lambda x: x.replace('.',''))
    cleaned[column_to_parse] = cleaned[column_to_parse].astype(int)
    
    # fill blanks with mode imputation
    for col in cleaned.columns[cleaned.isnull().any()]: cleaned[col].fillna(cleaned[col].mode().iloc[0])
    
    workingdata = cleaned
    
def get_data_from_csv():
    global data
    # global data, workingdata, filePaths
    # dataframes = [pd.read_csv(filePath, encoding='latin1') for filePath in filePaths]
    # for dataframe in dataframes:
    #     if 'NGR' in dataframe.columns: antennas = dataframe
    #     if 'EID' in dataframe.columns: params = dataframe
    antenna, params = pd.read_csv('/Users/yme/Code/AdvancedProgramming/SummativeAssessment/TxAntennaDAB.csv', encoding='latin1'), pd.read_csv('/Users/yme/Code/AdvancedProgramming/SummativeAssessment/TxParamsDAB.csv', encoding='latin1')
    df = pd.merge(params, antenna, on='id', how='left') # join the two dataframes on antenna/params id to make data easier to work with
    df.columns = [col.strip() for col in df.columns] # format columns names
    data = df
    
def extract_data():
    global data, workingdata
    
    #Client Requests
    # 1. remove NGRS NZ02553847, SE213515, NT05399374 and NT252675908 from possible outputs
    # Done in Cleaning Screen Logic
    
    # 2. The ‘EID’ column contains information of the DAB multiplex block E.g C19A. 
    # Extract this out into a new column, one for each of the following DAB multiplexes:
    # a.all DAB multiplexes, that are , C18A, C18F, C188
    # Can be done by selecting extract C18A, C18F, C188 in the extract screen
    extracted = data[data[coltoextract].isin(groupstoextract)] # extract multiplexes
    # extracted.set_index(coltoextract, inplace=True) # groupd data by multiplex
    
    # b.join each category, C18A, C18F, C188 to the ‘ NGR’ that signifies the DAB stations location to the following: 
    #  ‘Site’, ‘Site Height, In-Use Ae Ht, In-Use ERP Total
    extracted = extracted[columnstoextract] # reduce to desired columns
    #c.Please note that: In-Use Ae Ht, In-Use ERP Total  will need the following new header after extraction: 
    # Aerial height(m), Power(kW) respectively.
    #Done in Cleaning Screen Logic
    workingdata = extracted

# run
    
root = tk.Tk()

# initial_screen()
get_data_from_csv()
# extraction_screen()
extract_data()
# cleaning_screen()
clean_data()
visualization_screen()

root.mainloop()





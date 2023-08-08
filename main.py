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
databaseName = '3names' # give new database name
collectionName  = '3names1' # give new collection name

statscolumn, groupscolumn, visualizations, statistics = 'Births', 'Sex', ['Information','Correlation'], ['mean', 'std', 'min']

filePath = '/Users/yme/Code/AdvancedProgramming/SummativeAssessment/top_3_names_per_sex.csv'
data, workingdata = pd.read_csv(filePath), pd.read_csv(filePath)

#filtering
coltofilter = 'NGR'
criteriatoremove = ['NZ02553847', 'SE213515', 'NT05399374', 'NT252665908']

#extraction
coltoextract = 'EID'
# groupstoextract =  None
groupstoextract = ['C18A', 'C18F', 'C188']
columnstoextract = ['EID', 'NGR', 'Site', 'Site Height', 'In-Use Ae Ht', 'In-Use ERP Total']

#renaming
columnstorename = {'In-Use Ae Ht': 'Aerial Height(m)', 'In-Use ERP Total': 'Power(kW)'}

#screens
def initial_screen():
    loadfromcsv = tk.Button(root,text='Load from CSV', command=on_loadfromcsv)
    loadfromcsv.pack(expand=True, fill=tk.BOTH)
    
    loadfromdatabase = tk.Button(root,text='Load from Database', command=on_load_from_database)
    loadfromdatabase.pack(expand=True, fill=tk.BOTH)
    
    exit = tk.Button(root, text='Exit', command=on_exit)
    exit.pack(expand=True, fill=tk.BOTH)
    
def extraction_screen():
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
    
def cleaning_screen():

    def on_reset():
        global root
        for child in root.winfo_children(): child.destroy()
        extract_data()
        cleaning_screen()
        
    def on_apply_preset():
        global root
        clean_data()
        for child in root.winfo_children(): child.destroy()
        visualization_screen()

    def on_fill():
        print('')
        
    def on_apply_delimiter():
        print('')
        
    global data, workingdata
    
    buttons = tk.Frame(root)
    buttons.pack(expand=True, fill=tk.BOTH)
    
    exit = tk.Button(buttons, text='Exit', command=on_exit)
    exit.pack(side=tk.RIGHT, fill=tk.BOTH)
    
    continue_w_save = tk.Button(buttons,text='Continue and Save', command=on_continue_and_save)
    continue_w_save.pack(side=tk.RIGHT, fill=tk.BOTH)
    
    continue_wo_save = tk.Button(buttons,text='Continue', command=on_continue_to_analysis)
    continue_wo_save.pack(side=tk.RIGHT, fill=tk.BOTH)
    
    reset = tk.Button(buttons, text='Reset', command=on_reset)
    reset.pack(side=tk.LEFT, fill=tk.BOTH)
    
    apply_preset = tk.Button(buttons, text='Apply Preset Cleaning' ,command=on_apply_preset)
    apply_preset.pack(side=tk.LEFT, fill=tk.BOTH)
    
    def on_delete_rows():
        global workingdata, root
        selected_rows = tree.selection()
        for row in selected_rows: tree.delete(row)
        workingdata = workingdata[~workingdata['NGR'].isin(selected_rows)]
    
    delete_rows = tk.Button(buttons, text='Delete Selected Rows', command=on_delete_rows)
    delete_rows.pack(side=tk.LEFT)
    
    dataframe = tk.Frame(root)
    dataframe.pack(expand=True, fill=tk.BOTH)
    dataframe_view(dataframe, workingdata)
    
    tools = tk.Frame(root)
    tools.pack(expand=True, fill=tk.BOTH)
    
    
    columns = tk.Frame(tools, padx=5)
    columns.pack(side=tk.LEFT,fill=tk.BOTH)
    columns_box_frame = tk.Frame(columns)
    columns_box_frame.pack(fill=tk.BOTH)
    
    columnsbox = tk.Listbox(columns, selectmode=tk.MULTIPLE)
    for column in workingdata.columns: columnsbox.insert(tk.END, column)
    columnsbox.pack(fill=tk.BOTH)
    
    fill = tk.Frame(columns)
    fill.pack(side=tk.LEFT)
    selected_fill = tk.IntVar()
    for index, button_text in enumerate(['Mode Imputation', 'Fill With 0']):
        radiobutton = tk.Radiobutton(fill, text=button_text, variable=selected_fill, value=index)
        radiobutton.pack()
    fill_blanks = tk.Button(fill,text='Fill Column Blanks', command=on_fill)    
    fill_blanks.pack()
    
    delimiter_frame = tk.Frame(columns)
    delimiter_frame.pack(side=tk.LEFT)
    delimiter_label = tk.Label(delimiter_frame, text='Enter Delimiter to Parse Columns Values')
    delimiter_label.pack()
    delimiter = tk.Entry(delimiter_frame)
    delimiter.pack()
    apply_delimiter = tk.Button(delimiter_frame, text='Apply Delimiter', command=on_apply_delimiter)
    apply_delimiter.pack()
    
    # text entries for delimiter
            
    
def on_continue_and_save():
    def on_click():
        save_to_database(entry.get())
        destroy_children()
        visualization_screen()
        
    dialog = tk.Toplevel(root)
    entry = tk.Entry(dialog)
    
    button = tk.Button(dialog, text='Save Selected File As..',command=on_click)
    
    entry.pack(fill=tk.BOTH)
    button.pack(fill=tk.BOTH)
    

def on_continue_to_analysis():
    destroy_children()
    visualization_screen()
    
    
def on_reset():
    extract_data()

def visualization_screen():
    buttons()
    generate_statistics_widget()
    graph_information()

#widgets
def buttons():
    global selected_visualization, checkbox_variables
    frame = tk.Frame(root)
    frame.pack(expand=True, fill=tk.BOTH)
    
    radiobutton_frame = tk.Frame(frame, relief='groove', borderwidth=1)
    radiobutton_frame.pack(side=tk.LEFT,fill=tk.BOTH)
    checkbox_frame = tk.Frame(frame, relief='groove', borderwidth=1)
    checkbox_frame.pack(side=tk.LEFT,fill=tk.BOTH)
    
    radiolabel = tk.Label(radiobutton_frame, text='Visualizations: ')
    radiolabel.pack(side=tk.LEFT,fill=tk.BOTH)
    selected_visualization = tk.StringVar()
    selected_visualization.set(visualizations[0])
    for visualization in visualizations: 
        radio_button = tk.Radiobutton(radiobutton_frame,text=visualization,variable=selected_visualization, value=visualization, command=update_visualization)
        radio_button.pack(side=tk.LEFT,fill=tk.BOTH)
    
    checkboxlabel = tk.Label(checkbox_frame, text='Groups: ')
    checkboxlabel.pack(side=tk.LEFT,fill=tk.BOTH)
    groups, checkbox_variables = data[groupscolumn].unique(), {}
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


def dialog_box():
    messagebox.showerror("Error", "File not found")
    
def graph_information():
    global ax, canvas
    fig = Figure(figsize=(10,8), dpi=100)
    ax = fig.add_subplot()
    sns.lineplot(x='Year', y='Births', hue='Name', data=workingdata, ax=ax)
    ax.set_xticklabels(ax.get_xticklabels(),rotation=45, fontsize=10)  
    plt.tight_layout()
    canvas = FigureCanvasTkAgg(fig, master=root)
    canvas.draw()
    canvas.get_tk_widget().pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    
def regraph_information():
    global ax, canvas
    ax.clear()
    sns.lineplot(x='Year', y='Births', hue='Name', data=workingdata, ax=ax)
    ax.set_xticklabels(ax.get_xticklabels(), rotation=45, fontsize=10)
    plt.tight_layout()
    canvas.draw()
    
def regraph_correlation():
    global ax, canvas
    ax.clear()
    sns.barplot(x='Name', y='Births', data=workingdata, ax=ax)
    ax.set_xticklabels(ax.get_xticklabels(), rotation=45, fontsize=10)
    plt.tight_layout()
    canvas.draw()

def generate_statistics_widget():
    global numericaldataframe
    numericaldataframe = tk.Frame(root)
    numericaldataframe.pack(expand=True, fill=tk.BOTH)
    
    description = workingdata[statscolumn].describe() 
    for statistic in statistics:
        statisticframe = tk.Frame(numericaldataframe, relief='groove', borderwidth=1)
        statisticlabel = tk.Label(statisticframe, text=statistic.capitalize() + ': ' + str(description[statistic]))
        
        statisticlabel.pack(side=tk.LEFT, fill=tk.BOTH), statisticframe.pack(side=tk.LEFT, expand=True, fill=tk.BOTH)
    
def repopulate_statistics_widget():
    global numericaldataframe
    for child in numericaldataframe.winfo_children(): child.destroy()
    description = workingdata[statscolumn].describe() 
    for statistic in statistics:
        statisticframe = tk.Frame(numericaldataframe, relief='groove', borderwidth=1)
        statisticlabel = tk.Label(statisticframe, text=statistic.capitalize() + ': ' + str(description[statistic]))
        
        statisticlabel.pack(side=tk.LEFT, fill=tk.BOTH), statisticframe.pack(side=tk.LEFT, expand=True, fill=tk.BOTH)
        
def dataframe_view(frame, dataframe):
    global tree
    tree = ttk.Treeview(frame,selectmode='extended')
    vertical_scrollbar = ttk.Scrollbar(frame, orient='vertical', command=tree.yview)
    horizontal_scrollbar = ttk.Scrollbar(frame, orient='horizontal', command=tree.xview)
    
    tree.configure(yscrollcommand=vertical_scrollbar.set)
    tree.configure(xscrollcommand=horizontal_scrollbar.set)
    
    tree['columns'] = list(dataframe.columns)
    tree['show'] = 'headings'

    for column in dataframe.columns:
        tree.heading(column, text=column)
        tree.column(column)

    for index, row in dataframe.iterrows():
        tree.insert('', index, values=list(row))

    tree.pack(expand=True, fill=tk.BOTH)
    vertical_scrollbar.pack(side='right', fill='y')
    horizontal_scrollbar.pack(side='bottom', fill='x')

    
    
#event functions
def destroy_children():
    for child in root.winfo_children(): child.destroy()
    
def on_exit():
    global root
    root.destroy()
    
def on_loadfromcsv():
    global data, workingdata, filePaths
    filePaths = filedialog.askopenfilenames(title='Select The CSVs')
    destroy_children()
    get_data_from_csv()
    extraction_screen()
    
def on_extractcontinue():
    destroy_children()
    cleaning_screen()
    
def on_backtoloadscreen():
    destroy_children()
    initial_screen()
    
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
        destroy_children() 
        visualization_screen()
        
    dialog = tk.Toplevel(root)
    entry = tk.Entry(dialog)
    
    button = tk.Button(dialog, text='Save Selected File As..',command=on_click)
    
    entry.pack(fill=tk.BOTH)
    button.pack(fill=tk.BOTH)
    
    
#backend functions
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
    
    # c.Please note that: In-Use Ae Ht, In-Use ERP Total  will need the following new header after extraction: 
    # Aerial height(m), Power(kW) respectively.
    extracted.rename(columnstorename, inplace=True)    
    workingdata = extracted

def clean_data():
     # 1. remove NGRS NZ02553847, SE213515, NT05399374 and NT252675908 from possible outputs
    cleaned = cleaned[~data[coltofilter].isin(criteriatoremove)] # filter out the NGRS: NZ02553847, SE213515, NT05399374 and NT252675908
    # fill blanks
    # parse columns
    # assign integer values 
    workingdata = cleaned
    

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
    
def update_visualization():
    regraph_information() if selected_visualization.get() == 'Information' else regraph_correlation()

def update_data_range():
    global workingdata, selected_visualization
    selected_groups = [group for group, selected in checkbox_variables.items() if selected.get()]
    workingdata = data[data[groupscolumn].isin(selected_groups)]
    repopulate_statistics_widget()
    regraph_information() if selected_visualization.get() == 'Information' else regraph_correlation()    

# run
    
root = tk.Tk()

# initial_screen()
get_data_from_csv()
# extraction_screen()
extract_data()
cleaning_screen()

# visualization_screen()

root.mainloop()





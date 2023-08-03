import pandas as pd
import tkinter as tk
from tkinter import filedialog, messagebox
import seaborn as sns
import matplotlib.pyplot as plt
from pymongo import MongoClient

from matplotlib.backends.backend_tkagg import (
FigureCanvasTkAgg)
from matplotlib.figure import Figure

serverAddress = 'mongodb://127.0.0.1:27017/?directConnection=true&serverSelectionTimeoutMS=2000&appName=mongosh+1.10.1' # fill with your mongo server address
databaseName = 'blank' # give new database name
collectionName  = 'blank' # give new collection name

statscolumn, groupscolumn, visualizations, statistics = 'Births', 'Sex', ['Information','Correlation'], ['mean', 'std', 'min']

filePath = '/Users/yme/Code/AdvancedProgramming/SummativeAssessment/top_3_names_per_sex.csv'
data, workingdata = pd.read_csv(filePath), pd.read_csv(filePath)

def on_exit():
    root.destroy()
    
def on_loadfromcsv():
    global data, workingdata, filePaths
    
    filePaths = filedialog.askopenfilenames(title='Select The CSVs')
    
    cleandata()
    save_to_mongo()
    workingscreen()
    
def save_to_mongo():
    global data
    mongodata = data.to_dict(orient='records')
    client, collection = connect_to_server()
    collection.insert_many(mongodata)
    client.close()

def cleandata():
    # global data, workingdata, filePaths
    # dataframes = [pd.read_csv(filePath, encoding='latin1') for filePath in filePaths]
    # for dataframe in dataframes:
    #     if 'NGR' in dataframe.columns: antennas = dataframe
    #     if 'EID' in dataframe.columns: params = dataframe
    antenna, params = pd.read_csv('/Users/yme/Code/AdvancedProgramming/SummativeAssessment/TxAntennaDAB.csv', encoding='latin1'), pd.read_csv('/Users/yme/Code/AdvancedProgramming/SummativeAssessment/TxParamsDAB.csv', encoding='latin1')
    breakpoint()
    
    
def connect_to_server():
    client = MongoClient(serverAddress)
    database = client[databaseName]
    collection = database[collectionName]
    return client, collection
    
def on_loadfromdatabase():
    global data, workingdata
    client, collection = connect_to_server()
    results = collection.find()
    formatted_results = list(results)
    data, workingdata = pd.DataFrame(formatted_results), pd.DataFrame(formatted_results)
    client.close()
    
    for child in root.winfo_children(): child.destroy()
    workingscreen()

def initialscreen():
    loadfromcsv = tk.Button(root,text='Load from CSV', command=on_loadfromcsv)
    loadfromcsv.pack(expand=True, fill=tk.BOTH)
    
    loadfromdatabase = tk.Button(root,text='Load from Database', command=on_loadfromdatabase)
    loadfromdatabase.pack(expand=True, fill=tk.BOTH)
    
    exit = tk.Button(root, text='Exit', command=on_exit)
    exit.pack(expand=True, fill=tk.BOTH)
    
def dialog_box():
    messagebox.showerror("Error", "File not found")
    
def workingscreen():
    for child in root.winfo_children(): child.destroy()
    buttons()
    numericaldata()
    graph_information()
        
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

def numericaldata():
    global numericaldataframe
    numericaldataframe = tk.Frame(root)
    numericaldataframe.pack(expand=True, fill=tk.BOTH)
    populate_numerical_frame()
    
def populate_numerical_frame():
    description = workingdata[statscolumn].describe() 
    for statistic in statistics:
        statisticframe = tk.Frame(numericaldataframe, relief='groove', borderwidth=1)
        statisticlabel = tk.Label(statisticframe, text=statistic.capitalize() + ': ' + str(description[statistic]))
        
        statisticlabel.pack(side=tk.LEFT, fill=tk.BOTH), statisticframe.pack(side=tk.LEFT, expand=True, fill=tk.BOTH)
        
def repopulate_statistics():
    for child in numericaldataframe.winfo_children(): child.destroy()
    populate_numerical_frame()

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
    
def update_visualization():
    regraph_information() if selected_visualization.get() == 'Information' else regraph_correlation()

def update_data_range():
    global workingdata, selected_visualization
    selected_groups = [group for group, selected in checkbox_variables.items() if selected.get()]
    workingdata = data[data[groupscolumn].isin(selected_groups)]
    repopulate_statistics()
    regraph_information() if selected_visualization.get() == 'Information' else regraph_correlation()    
    
    
root = tk.Tk()

cleandata()

root.mainloop()





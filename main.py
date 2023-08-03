import pandas as pd
import tkinter as tk
import seaborn as sns
import matplotlib.pyplot as plt

from matplotlib.backends.backend_tkagg import (
FigureCanvasTkAgg)
from matplotlib.figure import Figure

serverAddress = 'mongodb://127.0.0.1:27017/?directConnection=true&serverSelectionTimeoutMS=2000&appName=mongosh+1.10.1' # fill with your mongo server address
databaseName = 'blank' # give new database name
collectionName  = 'blank' # give new collection name

filePath = '/Users/yme/Code/AdvancedProgramming/SummativeAssessment/top_3_names_per_sex.csv'
data, workingdata, statscolumn, groupscolumn, visualizations, statistics = pd.read_csv(filePath), pd.read_csv(filePath), 'Births', 'Sex', ['Information','Correlation'], ['mean', 'std', 'min']

def on_exit():
    root.destroy()
    
def on_loadfromcsv():
    global data
    data = pd.read_csv(filePath)
    for child in root.winfo_children(): child.destroy()
    workingscreen()
    
def on_loadfromdatabase():
    global data
    data = pd.read_csv(filePath)
    for child in root.winfo_children(): child.destroy()
    workingscreen()

def initialscreen():
    loadfromcsv = tk.Button(root,text='Load from CSV', command=on_loadfromcsv)
    loadfromcsv.pack(expand=True, fill=tk.BOTH)
    
    loadfromdatabase = tk.Button(root,text='Load from Database', command=on_loadfromdatabase)
    loadfromdatabase.pack(expand=True, fill=tk.BOTH)
    
    exit = tk.Button(root, text='Exit', command=on_exit)
    exit.pack(expand=True, fill=tk.BOTH)
    
def workingscreen():
    buttons()
    numericaldata()
    graph()
    
    
def graph():
    global ax, canvas
    fig = Figure(figsize=(10,8), dpi=100)
    ax = fig.add_subplot()
    sns.lineplot(x='Year', y='Births', hue='Name', data=workingdata, ax=ax)
    ax.set_xticklabels(ax.get_xticklabels(),rotation=45, fontsize=10)  
    plt.tight_layout()
    plt.savefig('activity_two.png', dpi=100)
    canvas = FigureCanvasTkAgg(fig, master=root)
    canvas.draw()
    canvas.get_tk_widget().pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    
def regraph():
    global ax, canvas
    ax.clear()
    sns.lineplot(x='Year', y='Births', hue='Name', data=workingdata, ax=ax)
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
        statisticlabel = tk.Label(statisticframe, text=statistic.capitalize()+':')
        statisticdata = tk.Label(statisticframe, text=description[statistic])
        
        statisticframe.pack(side=tk.LEFT, expand=True, fill=tk.BOTH)
        statisticlabel.pack(side=tk.LEFT, fill=tk.BOTH)
        statisticdata.pack(side=tk.LEFT, fill=tk.BOTH)
        
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
    print('Visualization Updated')

def update_data_range():
    global workingdata
    selected_groups = [group for group, selected in checkbox_variables.items() if selected.get()]
    workingdata = data[data[groupscolumn].isin(selected_groups)]
    repopulate_statistics()
    regraph()
    
    
root = tk.Tk()

workingscreen()

root.mainloop()





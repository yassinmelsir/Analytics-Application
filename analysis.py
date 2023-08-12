import pandas as pd
import tkinter as tk
import seaborn as sns
import matplotlib.pyplot as plt

from matplotlib.backends.backend_tkagg import (
FigureCanvasTkAgg)
from matplotlib.figure import Figure

from screen import Screen

from _config import visualizations, statistics, statscolumn

class Analysis(Screen):
    def __init__(self, root, controller, data):
        super().__init__(root, controller, data)
        self.gen_graph_data()
        self.buttons()
        self.generate_statistics_widget()
        self.graph_information() if graph_type == 'Information' else self.graph_correlation()
        print('Working Data:', workingdata)
        print('Graph Data:', graph_data)
        
        self.root.mainloop()

    def buttons(self):
        global selected_visualization, checkbox_variables, graph_type
        frame = tk.Frame(self.root)
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
            radio_button = tk.Radiobutton(radiobutton_frame,text=visualization,variable=selected_visualization, value=visualization, command=self.update_visualization)
            radio_button.pack(side=tk.LEFT,fill=tk.BOTH)
        
        checkboxlabel = tk.Label(checkbox_frame, text='Groups: ')
        checkboxlabel.pack(side=tk.LEFT,fill=tk.BOTH)
        groups, checkbox_variables = self.data.get_groupstoextract(), {}
        
        for group in groups:
            checkbox_variable = tk.BooleanVar(value=True)
            checkbox_variables[group] = checkbox_variable
            
            checkbox = tk.Checkbutton(checkbox_frame, text=group, variable=checkbox_variable, command=self.update_data_range)
            checkbox.pack(side=tk.LEFT,fill=tk.BOTH)
            
        exit = tk.Button(frame, text='Exit', command=self.on_exit)
        exit.pack(side=tk.RIGHT, fill=tk.BOTH)
        
        load = tk.Button(frame,text='Load from Database', command=self.on_load_from_database)
        load.pack(side=tk.RIGHT, fill=tk.BOTH)
        
        save = tk.Button(frame,text='Save to Database', command=self.on_save_to_database)
        save.pack(side=tk.RIGHT, fill=tk.BOTH)
        
    def update_visualization(self):
        global graph_type
        graph_type = selected_visualization.get()
        self.controller.show_visualization()

    def update_data_range(self):
        global workingdata, selected_visualization
        selected_groups = [group for group, selected in checkbox_variables.items() if selected.get()]
        self.workingdata = self.workingdata[self.data.get_data()['EID'].isin(selected_groups)]
        self.controller.show_analysis()

    def information_graph(self):
        sns.scatterplot(x='Longitude', y='Latitude', hue='EID', data=graph_data, ax=ax)
        for _, row in graph_data.iterrows(): 
            label = row['Site'] + '\n' + str(row['Freq.']) + '\n' + row['Block'] + '\n' + row['Stations']
            ax.text(row['Longitude'], row['Latitude'], label)
        ax.legend(loc='upper right')
        plt.tight_layout()
    
    def graph_information(self):
        global workingdata, ax, canvas, graph_data
        fig = Figure(figsize=(10,8), dpi=100)
        ax = fig.add_subplot()
        self.information_graph()
        canvas = FigureCanvasTkAgg(fig, master=self.root)
        canvas.draw()
        canvas.get_tk_widget().pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
    def regraph_information(self):
        global ax, canvas, graph_data
        ax.clear()
        self.information_graph()
        canvas.draw()
        
    def graph_correlation(self):
        global workingdata, ax, canvas, graph_data
        fig = Figure(figsize=(10,8), dpi=100)
        ax = fig.add_subplot()
        sns.barplot(x='NGR', y='Average Length Label', hue='Block', data=graph_data, ax=ax)
        ax.set_xticklabels(ax.get_xticklabels(), rotation=45, fontsize=10)
        plt.tight_layout()
        ax.legend(loc='upper right')
        canvas = FigureCanvasTkAgg(fig, master=self.root)
        canvas.draw()
        canvas.get_tk_widget().pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
    def regraph_correlation(self):
        global ax, canvas, workingdata
        # 
        ax.clear()
        sns.barplot(x='NGR', y='Average Length Label', hue='Block', data=graph_data, ax=ax)
        ax.set_xticklabels(ax.get_xticklabels(), rotation=45, fontsize=10)
        plt.tight_layout()
        ax.legend(loc='upper right')
        canvas.draw()
        
    def gen_graph_data(self):
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
        

    def generate_statistics_widget(self):
        description_year, description_height = self.compute_stats()
        self.statistics_frame(description_year, 'Year'), self.statistics_frame(description_height, 'Height')
        print('Description Year', description_year)
        print('Description Height', description_height)
        
    def statistics_frame(self,description, constraint):
        global numericaldataframe
        numericaldataframe = tk.Frame(self.root)
        numericaldataframe.pack(expand=True, fill=tk.BOTH)
        
        constraint_frame = tk.Frame(numericaldataframe, relief='groove', borderwidth=1)
        constraint_label = tk.Label(constraint_frame, text=constraint+' Constraint: ')
        constraint_label.pack(side=tk.LEFT, fill=tk.BOTH), constraint_frame.pack(side=tk.LEFT, expand=True, fill=tk.BOTH)
        
        for statistic in statistics:
            statisticframe = tk.Frame(numericaldataframe, relief='groove', borderwidth=1)
            statisticlabel = tk.Label(statisticframe, text=statistic.capitalize() + ': ' + str(description[statistic]))
            
            statisticlabel.pack(side=tk.LEFT, fill=tk.BOTH), statisticframe.pack(side=tk.LEFT, expand=True, fill=tk.BOTH)
                
    def compute_stats(self):
        global workingdata
        year_constraint, height_constraint = 2001, 75
        workingdata['Date'] = pd.to_datetime(workingdata['Date'], format='%d/%m/%Y')
        filter_by_year, filter_by_height = workingdata[workingdata['Date'].dt.year >= year_constraint], workingdata[workingdata['Site Height'] >= height_constraint]
        return filter_by_year[statscolumn].describe(), filter_by_height[statscolumn].describe()
    
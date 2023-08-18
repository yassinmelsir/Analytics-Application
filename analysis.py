import pandas as pd
import tkinter as tk
import seaborn as sns
import matplotlib.pyplot as plt

from matplotlib.backends.backend_tkagg import (
FigureCanvasTkAgg)
from matplotlib.figure import Figure

from screen import Screen

from _config import visualizations, statistics, year_constraint, height_constraint, stats_column, graph_type, label_columns

class Analysis(Screen):
    def __init__(self, controller):
        super().__init__(controller)
        self.working_data = self.data.get_working_data()
        self.get_graph_data()
        self.buttons()
        self.generate_statistics_widget()
        self.graph_information() if graph_type == 'Information' else self.graph_correlation()
        print('Working Data:', self.working_data)
        print('Graph Data:', eid_df)
        
        self.root.mainloop()
        
    def buttons(self):
        global selected_visualization, checkbox_variables, graph_type
        frame = tk.Frame(self.root)
        frame.pack(expand=True, fill=tk.BOTH)
        
        radiobutton_frame = tk.Frame(frame, relief='groove', borderwidth=1)
        radiobutton_frame.pack(side=tk.LEFT,fill=tk.BOTH)
        checkbox_frame = tk.Frame(frame, relief='groove', borderwidth=1)
        checkbox_frame.pack(side=tk.LEFT,fill=tk.BOTH)
        
        radio_label = tk.Label(radiobutton_frame, text='Visualizations: ')
        radio_label.pack(side=tk.LEFT,fill=tk.BOTH)
        selected_visualization = tk.StringVar()
        selected_visualization.set(graph_type)
        for visualization in visualizations: 
            radio_button = tk.Radiobutton(radiobutton_frame,text=visualization,variable=selected_visualization, value=visualization, command=self.update_visualization)
            radio_button.pack(side=tk.LEFT,fill=tk.BOTH)
        
        checkbox_label = tk.Label(checkbox_frame, text='Groups: ')
        checkbox_label.pack(side=tk.LEFT,fill=tk.BOTH)
        groups, checkbox_variables = self.data.get_groups_to_extract(), {}
        
        for group in groups:
            checkbox_variable = tk.BooleanVar(value=True)
            checkbox_variables[group] = checkbox_variable
            
            checkbox = tk.Checkbutton(checkbox_frame, text=group, variable=checkbox_variable, command=self.update_data_range)
            checkbox.pack(side=tk.LEFT,fill=tk.BOTH)
            
        exit = tk.Button(frame, text='Exit', command=self.controller.exit)
        exit.pack(side=tk.RIGHT, fill=tk.BOTH)
        
        load = tk.Button(frame,text='Load from Database', command=self.on_load_from_database)
        load.pack(side=tk.RIGHT, fill=tk.BOTH)
        
        save = tk.Button(frame,text='Save to Database', command=self.on_save_to_database)
        save.pack(side=tk.RIGHT, fill=tk.BOTH)
        
    def get_graph_data(self):
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
        
        global eid_df
        eid_df = self.working_data.copy()
        eid_df['Longitude'], eid_df['Latitude'] = eid_df['Longitude/Latitude'].apply(convert_to_longitude), eid_df['Longitude/Latitude'].apply(convert_to_latitude)         
        eid_df['Stations'] = eid_df['Serv Label1'] +', '+ eid_df['Serv Label2'] +'\n ' + eid_df['Serv Label3'] + ', ' + eid_df['Serv Label4'] + '\n' + eid_df['Serv Label10']
        
        labels = ['Serv Label1','Serv Label2', 'Serv Label3', 'Serv Label4','Serv Label10']
        for col in labels:
            eid_df[col+'(ul)'] = eid_df[col].apply(len)
            
        ul_labels = [label+'(ul)' for label in labels]
        
        eid_df['Average Length Label'] = (eid_df[ul_labels].sum(axis=1))/len(ul_labels)
        
        global label_df
        label_df = pd.DataFrame(columns=label_columns+['Label'])
        for i in [1,2,3,4,10]:
            s_label = [f'Serv Label{i}']
            df = self.working_data[label_columns+s_label].copy()
            df.rename(columns={s_label[0]:'Label'},inplace=True)
            label_df = pd.concat([label_df, df])
        label_df['Label Recurrences'] = label_df['Label'].map(label_df['Label'].value_counts())
        label_df['EID Recurrences'] = label_df['EID'].map(label_df['EID'].value_counts())
        label_df['Recurrences/Size of Multiplex (Antennas)'] = label_df['Label Recurrences'] / label_df['EID Recurrences']
        return eid_df, label_df
        
    def regraph(self):
        self.regraph_information() if graph_type == 'Information' else self.regraph_correlation()
        
    def update_visualization(self):
        global graph_type
        graph_type = selected_visualization.get()
        self.regraph()

    def update_data_range(self):
        global eid_df, label_df
        selected_groups = [group for group, selected in checkbox_variables.items() if selected.get()]
        self.working_data = self.data.get_working_data()
        if len(selected_groups) > 0:
            self.working_data = self.working_data[self.working_data['EID'].isin(selected_groups)]
        else: self.working_data = pd.DataFrame(columns=self.working_data.columns)
        self.get_graph_data()
        self.regraph()
        for child in height_frame.winfo_children(): child.destroy()
        for child in year_frame.winfo_children(): child.destroy()
        description_year, description_height= self.compute_stats()
        self.fill_statistics(year_frame,description_year,'Year')
        self.fill_statistics(height_frame,description_height,'Height')

    def information_graph(self):
        # plot x:longitude-y:latitude-l:site-c:multiplex 
        sns.scatterplot(x='Longitude', y='Latitude', hue='EID', data=eid_df, ax=ax1)
        for _, row in eid_df.iterrows(): 
            # label = row['Site'] + '\n' + str(row['Freq.']) + '\n' + row['Block'] + '\n' + row['Stations']
            label = row['Site']
            ax1.text(row['Longitude'], row['Latitude'], label)
        ax1.legend(loc='upper right')
        
        #plot x:Freq-y:Label-l:Block-c:multiplex
        sns.scatterplot(x='Freq.',y='Label',hue='EID',data=label_df, ax=ax2)
        for _, row in label_df.iterrows(): 
            label = row['Block']
            ax2.text(row['Freq.'], row['Label'], label)
        ax2.legend(loc='upper right')
        plt.tight_layout()
        
    
    def graph_information(self):
        global ax1, ax2, canvas
        fig, (ax1, ax2) = plt.subplots(1,2,figsize=(20,8), dpi=100)
        self.information_graph()
        canvas = FigureCanvasTkAgg(fig, master=self.root)
        canvas.draw()
        canvas.get_tk_widget().pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
    def regraph_information(self):
        ax1.clear(), ax2.clear()
        self.information_graph()
        canvas.draw()
        
    def correlation_graph(self):
        sns.scatterplot(x='EID', y='Freq.', hue='Block', data=eid_df, ax=ax1)
        for _, row in eid_df.iterrows(): 
            label = row['Stations']
            ax1.text(row['EID'], row['Freq.'], label)
        ax1.legend(loc='upper right')
        
        sns.scatterplot(x='Recurrences/Size of Multiplex (Antennas)',y='Label',hue='EID',data=label_df, ax=ax2)
        for _, row in label_df.iterrows(): 
            label = str(row['Freq.']) + '/' + row['Block']
            ax2.text(row['Recurrences/Size of Multiplex (Antennas)'], row['Label'], label)
        ax2.legend(loc='upper right')
        plt.tight_layout()
        
    def graph_correlation(self):
        global ax1, ax2, canvas
        fig, (ax1, ax2) = plt.subplots(1,2,figsize=(20,8), dpi=100)
        self.correlation_graph()
        canvas = FigureCanvasTkAgg(fig, master=self.root)
        canvas.draw()
        canvas.get_tk_widget().pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
    def regraph_correlation(self):
        ax1.clear(), ax2.clear()
        self.correlation_graph()
        canvas.draw()
        
    def generate_statistics_widget(self):
        description_year, description_height = self.compute_stats()
        self.statistics_frame(description_year, description_height)
        
    def statistics_frame(self,description_year, description_height):
        

        global statistics_frame,year_frame,height_frame
        statistics_frame = tk.Frame(self.root)
        statistics_frame.pack(expand=True, fill=tk.BOTH)
        
        year_frame = tk.Frame(statistics_frame)
        year_frame.pack(expand=True, fill=tk.BOTH)
        
        
        global height_frame
        height_frame = tk.Frame(statistics_frame)
        height_frame.pack(expand=True, fill=tk.BOTH)
        
        self.fill_statistics(year_frame,description_year,'Year')
        
        self.fill_statistics(height_frame,description_height,'Height')
        
    def fill_statistics(self,frame,description,constraint):
            constraint_frame = tk.Frame(frame, relief='groove', borderwidth=1)
            constraint_label = tk.Label(constraint_frame, text=f'{constraint} Constraint: ')
            constraint_label.pack(side=tk.LEFT, fill=tk.BOTH), constraint_frame.pack(side=tk.LEFT, expand=True, fill=tk.BOTH)
            
            for statistic in statistics:
                statisticframe = tk.Frame(frame, relief='groove', borderwidth=1)
                statisticlabel = tk.Label(statisticframe, text=statistic.capitalize() + ': ' + str(description[statistic]))
                statisticlabel.pack(side=tk.LEFT, fill=tk.BOTH), statisticframe.pack(side=tk.LEFT, expand=True, fill=tk.BOTH)
                
    def compute_stats(self):
        self.working_data['Date'] = pd.to_datetime(self.working_data['Date'].copy(), format='%d/%m/%Y').copy()
        filter_by_year, filter_by_height = self.working_data[self.working_data['Date'].dt.year >= year_constraint], self.working_data[self.working_data['Site Height'] >= height_constraint]
        print(filter_by_year[stats_column].describe(), filter_by_height[stats_column].describe())
        return filter_by_year[stats_column].describe(), filter_by_height[stats_column].describe()
    
    
    
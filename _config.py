import tkinter as tk

server_address = 'mongodb://127.0.0.1:27017/?directConnection=true&serverSelectionTimeoutMS=2000&appName=mongosh+1.10.3' # fill with your mongo server address
database_name = 'multiplexes' # give new database name
# collectionName  = '3names1' # give new collection name

# filePath = '/Users/yme/Code/AdvancedProgramming/SummativeAssessment/top_3_names_per_sex.csv'
# data, workingdata = pd.read_csv(filePath), pd.read_csv(filePath)
data, working_data = None, None

#filtering
col_to_filter = 'NGR'
criteria_to_remove = ['NZ02553847', 'SE213515', 'NT05399374', 'NT252665908']

#extraction
col_to_extract = 'EID'
groups_to_extract = ['C18A', 'C18F', 'C188']
columns_to_extract = [
        'EID', 'NGR', 'Site','Longitude/Latitude', 'Site Height', 'In-Use Ae Ht',
        'In-Use ERP Total', 'Freq.', 'Block','Serv Label1',
       'Serv Label2', 'Serv Label3', 'Serv Label4','Serv Label10', 'Date']

#renaming
columns_to_rename = {'In-Use Ae Ht': 'Aerial Height(m)', 'In-Use ERP Total': 'Power(kW)'}

#cleaning
fill_types = ['Mode Imputation', 'Fill With 0'] 
col_types = ['Int', 'Float', 'Str']

#stats
stats_column, groups_column, visualizations, statistics = 'Power(kW)', 'EID', ['Information','Correlation'], ['mean', 'std', 'min']
year_constraint, height_constraint = None, None

#graphs
graph_type = 'Information'

#initialization
next_screen = 'initial'

#analysis
label_columns = [
        'EID', 'NGR', 'Site','Longitude/Latitude', 'Site Height', 'Aerial Height(m)',
        'Power(kW)', 'Freq.', 'Block']
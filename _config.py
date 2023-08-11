import tkinter as tk

serverAddress = 'mongodb://127.0.0.1:27017/?directConnection=true&serverSelectionTimeoutMS=2000&appName=mongosh+1.10.3' # fill with your mongo server address
databaseName = 'multiplexes' # give new database name
# collectionName  = '3names1' # give new collection name

# filePath = '/Users/yme/Code/AdvancedProgramming/SummativeAssessment/top_3_names_per_sex.csv'
# data, workingdata = pd.read_csv(filePath), pd.read_csv(filePath)
data, working_data = None, None

#filtering
coltofilter = 'NGR'
criteriatoremove = ['NZ02553847', 'SE213515', 'NT05399374', 'NT252665908']

#extraction
coltoextract = 'EID'
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

#initialization
next_screen = 'initial'
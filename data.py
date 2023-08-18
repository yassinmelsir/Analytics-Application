import pandas as pd
from pymongo import MongoClient
from _config import columns_to_extract, col_to_filter, criteria_to_remove, columns_to_rename

class Data():
    def __init__(self, server_address, database_name):
        self.server_address = server_address
        self.database_name = database_name
        self.data = None
        self.working_data = None
        
        self.groups_to_extract = None
        
    def get_data(self):
        return self.data
    
    def get_working_data(self):
        return self.working_data
    
    def set_working_data(self, working_data):
        self.working_data = working_data
        
    def get_groups_to_extract(self):
        return self.groups_to_extract
    
    def set_groups_to_extract(self, groups_to_extract):
        self.groups_to_extract = groups_to_extract
    
    def get_collection(self,collection_name):
        client = MongoClient(self.server_address)
        database = client[self.database_name]
        return database[collection_name], client
        
    def get_collections(self):
        client = MongoClient(self.server_address)
        database = client[self.database_name]
        collection = database.list_collection_names()
        client.close()
        return collection

    def save_to_database(self,collection_name):
        mongodata = self.working_data.to_dict(orient='records')
        collection, client = self.get_collection(collection_name)
        result = collection.insert_many(mongodata)
        client.close()
        return result
        
    def load_from_database(self,collection_name):
        collection, client = self.get_collection(collection_name)
        results = collection.find()
        formatted_results = list(results)
        self.data, self.working_data = pd.DataFrame(formatted_results), pd.DataFrame(formatted_results)
        self.groups_to_extract = self.working_data['EID'].unique()
        client.close() 
        
    def get_data_from_csv(self, filePaths):
        # global data, _, filePaths
        dataframes = [pd.read_csv(filePath, encoding='latin1') for filePath in filePaths]
        for dataframe in dataframes:
            if 'NGR' in dataframe.columns: antennas = dataframe
            if 'EID' in dataframe.columns: params = dataframe
        # antenna, params = pd.read_csv('/Users/yme/Code/AdvancedProgramming/SummativeAssessment/TxAntennaDAB.csv', encoding='latin1'), pd.read_csv('/Users/yme/Code/AdvancedProgramming/SummativeAssessment/TxParamsDAB.csv', encoding='latin1')
        df = pd.merge(params, antennas, on='id', how='left') # join the two dataframes on antenna/params id to make data easier to work with
        df.columns = [col.strip() for col in df.columns] # format columns names
        self.data = df
        
    def extract_data(self):
        #Client Requests
        # 1. remove NGRS NZ02553847, SE213515, NT05399374 and NT252675908 from possible outputs
        # Done in Cleaning Screen Logic
        
        # 2. The ‘EID’ column contains information of the DAB multiplex block E.g C19A. 
        # Extract this out into a new column, one for each of the following DAB multiplexes:
        # a.all DAB multiplexes, that are , C18A, C18F, C188
        # Can be done by selecting extract C18A, C18F, C188 in the extract screen
        extracted = self.data[self.data['EID'].isin(self.groups_to_extract)] # extract multiplexes
        # extracted.set_index(coltoextract, inplace=True) # groupd self.data by multiplex
        
        # b.join each category, C18A, C18F, C188 to the ‘ NGR’ that signifies the DAB stations location to the following: 
        #  ‘Site’, ‘Site Height, In-Use Ae Ht, In-Use ERP Total
        extracted = extracted[columns_to_extract] # reduce to desired columns
        #c.Please note that: In-Use Ae Ht, In-Use ERP Total  will need the following new header after extraction: 
        # Aerial height(m), Power(kW) respectively.
        #Done in Cleaning Screen Logic
        self.working_data = extracted
    
    def delete_rows(self,selected_rows):
        self.working_data = self.working_data[~self.working_data['NGR'].isin(selected_rows)]
        
    def fill(self, fill, column):
        na = 0 if fill == 'Fill With 0' else self.working_data[column].mode().iloc[0]
        self.working_data[column] = self.working_data[column].fillna(na)
        
    def replace(self, column, to_replace, replace_with):
        self.working_data[column] = self.working_data[column].apply(lambda x: x.replace(f'{to_replace}',f'{replace_with}'))
        
    def set_type(self, column, selected_coltype):
        self.working_data[column] = self.working_data[column].astype(selected_coltype.get().lower())    
    
    def set_name(self, name, column):
        self.working_data.rename(columns={column:name}, inplace=True)

    def preset_clean_data(self):
        
        # 1. remove NGRS NZ02553847, SE213515, NT05399374 and NT252665908 from possible outputs
        cleaned = self.working_data[~self.working_data[col_to_filter].isin(criteria_to_remove)] # filter out the NGRS: NZ02553847, SE213515, NT05399374 and NT252665908
        
        # 2. c.Please note that: In-Use Ae Ht, In-Use ERP Total  will need the following new header after extraction: 
        # Aerial height(m), Power(kW) respectively.
        cleaned.rename(columns=columns_to_rename, inplace=True)    

        # remove anomalies, and reclassify
        column_to_parse = 'Power(kW)'
        cleaned[column_to_parse] = cleaned[column_to_parse].apply(lambda x: x.replace(',',''))
        cleaned[column_to_parse] = cleaned[column_to_parse].apply(lambda x: x.replace('.',''))
        cleaned[column_to_parse] = cleaned[column_to_parse].astype(int)
        
        # fill blanks with mode imputation
        for col in cleaned.columns[cleaned.isnull().any()]: cleaned[col].fillna(cleaned[col].mode().iloc[0])
        
        return cleaned
import pandas as pd
import numpy as np
from geopy.geocoders import Nominatim
from datetime import date

#consists of raw data german air pollutant assessment methods
file_input = "DEAir_Assessment_raw.csv"

#stores the pre-processed data of the raw file as staging
file_pre_processed = "Pre-Processed_DEAir_Assessment.csv"

#stores the respective dimension tables of a star scheme into csvs
file_station_dim = "Station_details.csv"
file_methods_dim = "MeasurementMethod_details.csv"
file_pollutants_dim = "Pollutants_details.csv"

#stores the fact table of a star scheme into csv
file_pollutant_method_fact = "Pollutants_assessed_facts.csv"

#stores the data required for classification
file_classify_pollutant = "classify_pollutant.csv"

df_input = pd.read_csv(file_input, encoding = "utf-8", header = 0)

#currency_check
df_input['OperationYear'] = df_input['OperationalActivityBegin'].str.slice(stop=4).astype(int)
df_input=df_input.loc[(df_input['OperationYear'] >= 1900) & (df_input['OperationYear'] <= date.today().year)]

if date.today().year-df_input['OperationYear'].max() > 1:
    df_input = pd.read_csv(file_input, header = 0)

#completeness_check
df_input['OperationalActivityEnd'] = df_input.OperationalActivityEnd.replace(np.nan,'Not Specified')

#Obtain a dataframe of count of values for a specific column
stationType_counts_df = df_input['StationType'].value_counts(normalize=True).rename_axis('StationType').reset_index(name='count')
stationArea_counts_df = df_input['StationArea'].value_counts(normalize=True).rename_axis('StationArea').reset_index(name='count')
MeasurementRegime_counts_df = df_input['MeasurementRegime'].value_counts(normalize=True).rename_axis('MeasurementRegime').reset_index(name='count')

#check if any column is empty
nan_rows = df_input.isnull().values.any()
# print(nan_rows)
if nan_rows:

    #Drop rows where pollutant and the measurement method is NaN.
    df_input = df_input[df_input.Pollutant != np.nan]
    df_input = df_input[df_input.MeasurementMethod != np.nan]

    #Replaces NaN values with Germany
    df_input['CountryOrTerritory'] = df_input.CountryOrTerritory.replace(np.nan,'Germany')
    
    #Replaces NaN values with the most occuring value of Station type
    df_input['StationType'] = df_input.StationType.replace(np.nan,stationType_counts_df.iloc[0,0])    
    
    #Replaces NaN values with the most occuring value of Station area
    df_input['StationArea'] = df_input.StationArea.replace(np.nan,stationArea_counts_df.iloc[0,0])

    #Replaces NaN values with the most occuring value of Measurement Regime    
    df_input['MeasurementRegime'] = df_input.MeasurementRegime.replace(np.nan,MeasurementRegime_counts_df.iloc[0,0])


#Accuracy Check
#Check if the values present belongs to mentioned categories,if not drop them.
df_input=df_input.loc[(df_input['StationType'] == 'Traffic') | (df_input['StationType'] == 'Background') | (df_input['StationType'] == 'Industrial')]
df_input=df_input.loc[(df_input['StationArea'] == 'Urban') | (df_input['StationArea'] == 'Suburban') | (df_input['StationArea'] == 'Rural-Regional') | (df_input['StationArea'] == 'Rural-Near_city') | (df_input['StationArea'] == 'Rural') | (df_input['StationArea'] == 'Rural-Remote')]
df_input=df_input.loc[(df_input['MeasurementRegime'] == 'Continuous data collection') | (df_input['MeasurementRegime'] == 'Periodic data collection')]

#Validity Check

# checks if the given float numbers actually follow the syntax of geo coordinate.
if not np.array_equal(df_input.Latitude, df_input.Latitude.astype(float)):
    df=df_input[df_input.Latitude.str.contains("(\\-?|\\+?)?\d+(\\.\d+)?")]

if not np.array_equal(df_input.Longitude, df_input.Longitude.astype(float)):
    df=df_input[df_input.Longitude.str.contains("(\\-?|\\+?)?\d+(\\.\d+)?")]

######### This piece of code works, commenting it because my system cannot support tedious tasks
#### fetches the city and country based on the given geo coordinates, if the country fetched isnt in Deutschland, we drop it. 
#
# city = []
# country_check = []
# geolocator = Nominatim(user_agent="uni_project")
# for i in range(len(df_input)):
#     cords = str(df_input.iloc[i,7])+", "+str(df_input.iloc[i,8])
#     location = geolocator.reverse(cords)
#     location = location.address.split(',')
#     # print(location[3]+" | "+location[-1])
#     city.append(location[3])
#     country_check.append(location[-1])

# df_input['City'] =  city
# df_input['CountryCheck'] = country_check
# #drop the row if country is not Deutschland
# df_input=df_input.loc[(df_input['CountryCheck'].str.strip() == 'Deutschland')]
####
##########

#checks if the altitude is within german's highest and lowest altitude
df_input=df_input.loc[(df_input['Altitude'] >= -3.54) & (df_input['Altitude'] <= 2963)]

#Transformations

# Split the pollutant on the first occurance of '(' into a different column and trim ')' to obtain the pollutant type being assessed
df_input[['Pollutant','PollutantType']] = df_input['Pollutant'].str.split('(',expand=True)
df_input['PollutantType'] = df_input['PollutantType'].str.replace(")","")

# convert the value of 'air' and 'aerosol' to 1 and 0 and store it in a new column 
df_input['isAir'] = df_input['PollutantType']
df_input['isAir'].replace(to_replace='air', value=1, inplace=True)
df_input['isAir'].replace(to_replace='aerosol',  value=0, inplace=True)


# pd.set_option('display.max_columns', None)
# print(df_input.head(5))

# write the pre processed dataframe to a CSV
df_input.to_csv(file_pre_processed, encoding='utf-8', index=False)

df_pre_processed = pd.read_csv(file_pre_processed, encoding = "utf-8", header = 0)

# fetching the relevant columns for the respective dimension and factual tables
df_stations = df_pre_processed.loc[ : , ['StationCode', 'StationName', 'StationType', 'StationArea', 'CountryOrTerritory', 'Latitude', 'Longitude'] ]
df_methods = df_pre_processed.loc[ : , ['MeasurementMethodCode', 'MeasurementMethod', 'MeasurementRegime']]
df_pollutants = df_pre_processed.loc[ : , ['PollutantCode', 'Pollutant', 'PollutantType', 'isAir']]
df_pollutant_assess_fact = df_pre_processed.loc[ : , ['StationCode', 'PollutantCode', 'MeasurementMethodCode', 'Altitude', 'OperationalActivityBegin','OperationalActivityEnd']]

# sorts the dataframes and drops any duplicates for the dimesion table
df_stations = df_stations.sort_values(by = ['StationName'], ascending = True, na_position = 'last').drop_duplicates(['StationCode'],keep = 'first')
df_methods = df_methods.sort_values(by = ['MeasurementMethod'], ascending = True, na_position = 'last').drop_duplicates(['MeasurementMethodCode'],keep = 'first')
df_pollutants = df_pollutants.sort_values(by = ['Pollutant'], ascending = True, na_position = 'last').drop_duplicates(['PollutantCode'],keep = 'first')

# write the dimensions and facts into a csv. Voila Star SCheme is ready!
df_stations.to_csv(file_station_dim, encoding='utf-8', index=False)
df_methods.to_csv(file_methods_dim, encoding='utf-8', index=False)
df_pollutants.to_csv(file_pollutants_dim, encoding='utf-8', index=False)
df_pollutant_assess_fact.to_csv(file_pollutant_method_fact, encoding='utf-8', index=False)

# Fetch the columns required for classification.
# Generally a feature selection is employed using corelation matrix, but since most of our data is consists of either high or low cardinality.
# we pick the ones with categorical data types
predict_df = df_pre_processed.loc[ : , ["StationType","StationArea","MeasurementMethod",'Altitude','isAir']]

# convert the categorical varibales to numerical
stationType = predict_df.StationType.unique()
i=1
for x in stationType:
    predict_df['StationType'].replace(to_replace=stationType[i-1], value=i, inplace=True)
    i = i+1

stationArea = predict_df.StationArea.unique()
i=1
for x in stationArea:
    predict_df['StationArea'].replace(to_replace=stationArea[i-1], value=i, inplace=True)
    i=i+1

measurementMethod = predict_df.MeasurementMethod.unique()
i=1
for x in measurementMethod:
    predict_df['MeasurementMethod'].replace(to_replace=measurementMethod[i-1], value=i, inplace=True)
    i=i+1

# write it to a csv for the usuage in classification
predict_df.to_csv(file_classify_pollutant, encoding='utf-8', index=False)

print("Done")


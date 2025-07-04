import warnings
warnings.filterwarnings('ignore')

import pandas as pd
import numpy as np
from sklearn.preprocessing import OrdinalEncoder, OneHotEncoder



def cleaning_columns(self):
    # Clean column names: remove whitespace, lower case, replace space by underscore
    self.df.columns = self.df.columns.str.strip().str.lower().str.replace(" ", "_")

    # Drop unused columns
    self.df.drop(columns=['unnamed:_0', 'url', 'id', 'monthlycost', 'hasbalcony', 'accessibledisabledpeople',
                    'bathroomcount','roomcount','hasattic','hasbasement','hasdressingroom',
                    'diningroomsurface','hasdiningroom','floorcount','streetfacadewidgth',
                    'floodzonetype','heatingtype','hasheatpump','hasvoltaicpanels',
                    'hasthermicpanels','kitchensurface','kitchentype','haslivingroom',
                    'livingroomsurface','gardenorientation','hasairconditioning',
                    'hasarmoreddoor','hasvisiophone','hasoffice',
                    'hasfireplace','terracesurface','terraceorientation',
                    'gardensurface', 'toiletcount',
                    'hasphotovoltaicpanels', 'streetfacadewidth','buildingconstructionyear',
                    'facedecount', 'landsurface'], inplace=True, errors='ignore') 



# Maybe reuse some of this logic to make sure the data passed is reasonable?
def eliminate_outliers(self):
    cols = ['bedroomcount', 'habitablesurface', 'price']

    for col in cols:
        # 75th percentile
        seventy_fifth = self.df[col].quantile(0.75)
        # 25th percentile
        twenty_fifth = self.df[col].quantile(0.25)
        # Interquartile range
        surface_iqr = seventy_fifth - twenty_fifth

        # Upper threshold
        upper = seventy_fifth + (1.5 * surface_iqr)
        # Lower threshold
        lower = twenty_fifth - (1.5 * surface_iqr)

        outliers = self.df[(self.df[col] < lower) | (self.df[col] > upper)]

    self.df=self.df[~self.df.index.isin(outliers.index)]

    self.df = self.df[~self.df['habitablesurface'].isna()]
    self.df['habitablesurface'] = self.df['habitablesurface'].astype(float)
    self.df = self.df.drop(self.df[self.df['habitablesurface'] > 1500].index)
    self.df = self.df.drop(self.df[self.df['bedroomcount'] > 20].index)   


def oe_ohe_processing(df):
    oe2 = OrdinalEncoder(categories=[['AS_NEW','JUST_RENOVATED','GOOD','TO_BE_DONE_UP','TO_RENOVATE','TO_RESTORE']])
    df['buildingcondition_encoded'] = oe2.fit_transform(df[['buildingcondition']])

    # Preprocessing Type
    df['type_encoded'] = (df['type'] == 'HOUSE').astype(int)
    return df

def drop_remaining_columns(df):
    # Drop columns 
    df.drop(columns=['buildingcondition','region'], inplace=True)

    
#  TODO: fix this function
def latitude_longitude_columns(df):
    df_geo = pd.read_csv('preprocessing/georef-belgium-postal-codes@public.csv', sep=';')
    pc_geo_dict = {}
    for pc in df['postcode'].unique():
        print('POSTCODE', pc)
        geo_point = df_geo.loc[df_geo['Post code'] == pc, 'Geo Point'].values
        print('GEO POINT', geo_point)
        if len(geo_point) > 0:
            pc_geo_dict[pc] = geo_point[0]
        else:
            pc_geo_dict[pc] = None
    df['geocode'] = df['postcode'].map(pc_geo_dict)

    df[['latitude', 'longitude']] = df['geocode'].str.split(',', expand=True)

    df['latitude'] = df['latitude'].astype(float)
    df['longitude'] = df['longitude'].astype(float)

    df.drop(columns=['geocode'], inplace=True)
    df.drop(columns=['postcode'], inplace=True)
        

def check_required_columns_data(df):
    print('df', df)
    postal_codes_df = pd.read_csv('preprocessing/georef-belgium-postal-codes@public.csv', sep=';')

    area = int(df['area'].iloc[0])
    property_type = df['property-type'].iloc[0]
    zip_code = df['zip-code'].iloc[0]

    print("Area:", area, "Property Type:", property_type, "Zip Code:", zip_code)
    if area <= 0 or area >= 1500:
        raise ValueError("Area must be a positive number and less than 1500.")
    if property_type == 'OTHER':
        return "HOUSE" if df['area'] > 200 else "APARTMENT"
    if zip_code not in postal_codes_df['Post code'].values:
        raise ValueError("Invalid zip code. Please provide a valid Belgian postal code.")
    
def transform_fields(df):
    df['habitablesurface'] = df['area'].astype(float)
    df['type'] = df['property-type']
    df['postcode'] = df['zip-code'].astype(str)
    df['bedroomcount'] = df['rooms-number'].astype(int)
    df['hasgarden'] = df['garden'].fillna(False).astype(bool)
    df['hasswimmingpool'] = df['swimming-pool'].fillna(False).astype(bool)
    df['hasterrace'] = df['terrace'].fillna(False).astype(bool)
    df['buildingcondition'] = df['building-state'].astype(str).replace({
        'NEW': 'AS_NEW',
        'JUST RENOVATED': 'JUST_RENOVATED',
        'TO REBUILD': 'TO_RENOVATE'
    })
    df['hasswimmingpool'] = df['swimming-pool'].fillna(False).astype(bool)
    return df


def convert_boolean_values(df):
    df[['hasgarden','hasswimmingpool', 'hasterrace']] = df[['hasgarden','hasswimmingpool', 'hasterrace']].astype(int)
    return df

            
def data_pre_processing(json):
    df = pd.DataFrame([json])  # Convert JSON to DataFrame
    # we're only expecting one row
    df = df.loc[0:1] 
    print(df.info())
    check_required_columns_data(df)
    df = transform_fields(df)
    print('transformed fields', df)
    df = convert_boolean_values(df)
    df = oe_ohe_processing(df)
    df = latitude_longitude_columns(df)
    # df = drop_remaining_columns(df)


    # df = cleaning_columns()
    # df = add_parking_col()
    # df = add_region_column()
    # df = eliminate_outliers()
    # df = eliminate_postcode_small_number()
    # df = drop_remaining_rows()
    # df = oe_ohe_processing()
    # df = drop_duplicates()
    # df = df.info()

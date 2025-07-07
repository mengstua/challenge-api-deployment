import pandas as pd
import numpy as np
from sklearn.preprocessing import OrdinalEncoder, OneHotEncoder

pd.set_option('display.max_columns', None)  # Show all columns

def encode_fields(df):
    oe2 = OrdinalEncoder(
        categories=[
            [
                "AS_NEW",
                "JUST_RENOVATED",
                "GOOD",
                "TO_BE_DONE_UP",
                "TO_RENOVATE",
                "TO_RESTORE",
            ]
        ]
    )
    df["buildingcondition_encoded"] = oe2.fit_transform(df[["buildingcondition"]])

    # One-Hot Encoding Region
    ohe = OneHotEncoder(
        categories=[["Brussels", "Flanders", "Wallonia"]],
        sparse_output=False,
        handle_unknown="ignore"
    )
    encoded = ohe.fit_transform(df[['region']])
    df_one_hot = pd.DataFrame(encoded, columns=ohe.get_feature_names_out(['region']), index=df.index)
    df = pd.concat([df, df_one_hot], axis=1)


    # Preprocessing Type
    df["type_encoded"] = (df["type"] == "HOUSE").astype(int)
    return df


def drop_remaining_columns(df):
    # Drop columns
    df.drop(
        columns=[
            "buildingcondition",
            "area",
            "property-type",
            "rooms-number",
            "zip-code",
            "land-area",
            "garden",
            "garden-area",
            "equipped-kitchen",
            "full-address",
            "swimming-pool",
            "furnished",
            "open-fire",
            "terrace",
            "terrace-area",
            "facades-number",
            "building-state",
            "type",
            'region',
        ],
        inplace=True,
    )
    return df


def latitude_longitude_columns(df):
    df_geo = pd.read_csv(
        "preprocessing/georef-belgium-postal-codes@public.csv", sep=";"
    )
    df_geo_unique = df_geo.drop_duplicates(subset=["Post code"])

    # Create a mapping from postcode to geo point
    postcode_to_geo = df_geo_unique.set_index("Post code")["Geo Point"]
    # Map the geo point to your df
    df["geocode"] = df["postcode"].astype(int).map(postcode_to_geo).fillna("0,0")
    # Split geocode into latitude and longitude
    df[["latitude", "longitude"]] = df["geocode"].str.split(",", expand=True)
    df["latitude"] = df["latitude"].astype(float)
    df["longitude"] = df["longitude"].astype(float)
    df.drop(columns=["geocode", "postcode"], inplace=True)
    return df

def add_region_column(df):
    df_geo = pd.read_csv(
        "preprocessing/georef-belgium-postal-codes@public.csv", sep=";"
    )
    df_geo_unique = df_geo.drop_duplicates(subset=["Post code"])
    df["region"] = df["zip-code"].astype(int).map(
        df_geo_unique.set_index("Post code")["Région code"]
    ).astype(int)
    # map region code to region name
    region_mapping = {
        1000: "Brussels",
        2000: "Flanders",
        3000: "Wallonia",
    }
    df["region"] = df["region"].map(region_mapping)


def check_required_columns_data(df):
    print("df", df)
    postal_codes_df = pd.read_csv(
        "preprocessing/georef-belgium-postal-codes@public.csv", sep=";"
    )

    area = int(df["area"].iloc[0])
    property_type = df["property-type"].iloc[0]
    zip_code = df["zip-code"].iloc[0]

    print("Area:", area, "Property Type:", property_type, "Zip Code:", zip_code)
    if area <= 0 or area >= 1500:
        raise ValueError("Area must be a positive number and less than 1500.")
    if property_type == "OTHER":
        return "HOUSE" if df["area"] > 200 else "APARTMENT"
    if zip_code not in postal_codes_df["Post code"].values:
        raise ValueError(
            "Invalid zip code. Please provide a valid Belgian postal code."
        )


def transform_fields(df):
    df["habitablesurface"] = df["area"].astype(float)
    df["type"] = df["property-type"]
    df["postcode"] = df["zip-code"].astype(str)
    df["bedroomcount"] = df["rooms-number"].astype(int)
    df["hasgarden"] = df["garden"].fillna(False).astype(bool)
    df["hasswimmingpool"] = df["swimming-pool"].fillna(False).astype(bool)
    df["hasterrace"] = df["terrace"].fillna(False).astype(bool)
    df["buildingcondition"] = (
        df["building-state"]
        .fillna("TO_RENOVATE")
        .astype(str)
        .replace(
            {
                "NEW": "AS_NEW",
                "JUST RENOVATED": "JUST_RENOVATED",
                "TO REBUILD": "TO_RENOVATE",
            }
        )
    )
    df["hasswimmingpool"] = df["swimming-pool"].fillna(False).astype(bool)
    # If we don't get these information from the user, we set them to False
    df["haslift"] = False
    df['hasparking'] = False

    df['epcscore_encoded'] = 3  # Default value for EPC score if we don't get it from the payload
    return df


def convert_boolean_values(df):
    df[["hasgarden", "hasswimmingpool", "hasterrace"]] = df[
        ["hasgarden", "hasswimmingpool", "hasterrace"]
    ].astype(int)
    return df



def sort_columns(df):
    model_columns = ["bedroomcount","habitablesurface","haslift","hasgarden","hasswimmingpool","hasterrace","hasparking","epcscore_encoded","buildingcondition_encoded","region_Brussels","region_Flanders","region_Wallonia","type_encoded","latitude","longitude"
]
    # sort the DataFrame columns based on the model_columns list
    df = df[model_columns]
    return df

def pre_process_data(json):
    df = pd.DataFrame([json])
    # we're only expecting one row
    df = df.loc[0:1]
    check_required_columns_data(df)
    add_region_column(df)
    df = transform_fields(df)
    df = convert_boolean_values(df)
    df = encode_fields(df)
    df = latitude_longitude_columns(df)
    df = drop_remaining_columns(df)
    df = sort_columns(df)
    return df

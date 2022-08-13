import pandas as pd
import base64
"""
Functions to clean up and reset data from initial webscraping of NAMI Website
"""


def remove_messy_data(nami_df):
    """
    remove all counties/NAMI Chapters that have no email information

    Parameters
    ----------
    :param nami_df: Pandas Dataframe
        all NAMI Chapter data before clean up
    """
    for key, val in nami_df.iterrows():
        if val['Email'] == "N/A":
            nami_df = nami_df.drop(key, inplace=True)
    nami_df.to_pickle("pickles/NAMI_DATA.pkl")
    print("Removed Messy Data")


def addPopulations(nami_df, county_population_df):
    """
    add population information to NAMI CHAPTER data from population estimates from US GOV


    :param nami_df: Pandas Dataframe
        Cleaned up NAMI Chapter data
    :param county_population_df: Pandas Dataframe
        Populations of all counties in the United States
    :return: None
    """
    # print(nami_df.to_string())
    for nami_key, nami_val in nami_df.iterrows():
        for county_key, county_val in county_population_df.iterrows():
            county = county_val["CTYNAME"]
            if "County" in county:
                county = county_val["CTYNAME"][:-6].strip()
            if county in nami_val["Serving"] and (
                    nami_val['Population_2021'] is None or county_val["POPESTIMATE2021"] > nami_val["Population_2021"]):
                print(f"Nami Serving: {nami_val['Serving']}")
                print(f"Nami Pop: {nami_val['Population_2021']}\nCounty Pop: {county_val['POPESTIMATE2021']}\n")
                # print(county_val["POPESTIMATE2021"])
                nami_val["Population_2021"] = county_val["POPESTIMATE2021"]
    nami_df = nami_df.sort_values(["Population_2021"], ascending=False)
    nami_df.to_pickle("pickles/NAMI_DATA.pkl")



def reset_data(nami_df):
    """
    reset population dataframes and clear all contacted counties

    :param nami_df: Pandas Dataframe
        Current NAMI Chapter Data
    :return: None
    """
    high_df = pd.DataFrame()
    mid_df = pd.DataFrame()
    low_df = pd.DataFrame()
    none_df = pd.DataFrame()
    contacted_df = pd.DataFrame()
    all_contacted_df = pd.DataFrame()

    for key, val in nami_df.iterrows():
        if val['Population_2021'] is None:
            none_df = none_df.append(val, ignore_index=True)
        elif val['Population_2021'] > 10000000:
            high_df = high_df.append(val, ignore_index=True)
        elif val['Population_2021'] > 1000000:
            mid_df = mid_df.append(val, ignore_index=True)
        elif val['Population_2021'] > 1000:
            low_df = low_df.append(val, ignore_index=True)

    high_df.to_pickle("pickles/HighPopulationCounties.pkl")
    mid_df.to_pickle("pickles/MiddlePopulationCounties.pkl")
    low_df.to_pickle("pickles/LowPopulationCounties.pkl")
    none_df.to_pickle("pickles/NonePopulationCounties.pkl")

    high_df.to_pickle("pickles/HighPopulationCounties_notContacted.pkl")
    mid_df.to_pickle("pickles/MiddlePopulationCounties_notContacted.pkl")
    low_df.to_pickle("pickles/LowPopulationCounties_notContacted.pkl")
    none_df.to_pickle("pickles/NonePopulationCounties_notContacted.pkl")

    contacted_df.to_pickle("pickles/CountiesJustContacted.pkl")
    all_contacted_df.to_pickle("pickles/AllContactedCounties.pkl")
    print("~~~~~~~~~~~~DATA IS RESET~~~~~~~~~~~~")


def flyer_upload():
    """
    Function to encode pdf file with byte data for attachment to email
    :return: None
    """
    with open("flyer.pdf", "rb") as pdf_file:
        flyer_bytes = base64.b64encode(pdf_file.read())
    with open("flyer_bytes.txt", "wb") as binary_file:
        # Write bytes to file
        binary_file.write(flyer_bytes)

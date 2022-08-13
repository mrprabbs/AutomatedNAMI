""" NAMI Automatic Email Sender
This script scrapes contact information from the NAMI (National Alliance of Mental Illness) and cleans the data into
separate categories grouped by population. It then allows the user to send a specific study recruitment email to the
chapters of their choice (based on population)
"""
# !/usr/bin/env python3
import configparser
import pandas as pd
import utils
from graph import Graph
import EmailSender


def main():
    """
    Front end for user to interact with the program.
    """
    # Load settings for setting up Graph API
    config = configparser.ConfigParser()
    config.read(['config.cfg', 'config.dev.cfg'])
    azure_settings = config['azure']

    graph: Graph = Graph(azure_settings)
    EmailSender.greet_user(graph)

    choice = -1

    # front end dashboard
    while choice != 0:
        print('\n\nPlease choose one of the following options:')
        print('0. Exit')
        print('1. Display access token')
        print('2. Send mail')
        print('3. Display chapters just contacted during this session')
        print('4. Display ALL contacted chapters')

        try:
            choice = int(input())
        except ValueError:
            choice = -1

        # exit program
        if choice == 0:
            print('Goodbye...')

            # clear data for Counties Contacted during this session
            contacted_df = pd.DataFrame()
            contacted_df.to_pickle('pickles/CountiesJustContacted.pkl')
        elif choice == 1:
            EmailSender.display_access_token(graph)
        # send emails to NAMI Chapters
        elif choice == 2:
            pd.set_option('display.max_columns', None)
            pd.set_option('display.max_rows', None)

            # load dataframes with counties that have not been contacted
            high_df = pd.read_pickle("pickles/HighPopulationCounties_notContacted.pkl")
            mid_df = pd.read_pickle("pickles/MiddlePopulationCounties_notContacted.pkl")
            low_df = pd.read_pickle("pickles/LowPopulationCounties_notContacted.pkl")
            none_df = pd.read_pickle("pickles/NonePopulationCounties_notContacted.pkl")

            print(f"Top 10 High Population Counties that have NOT been contacted yet\n{high_df.head(10)}\n")
            print(f"Top 10 Mid Population Counties that have NOT been contacted yet\n{mid_df.head(10)}\n")
            print(f"Top 10 low Population Counties that have NOT been contacted yet\n{low_df.head(10)}\n")
            print(f"Top 10 Counties with NO POPULATION DATA that have NOT been contacted yet\n{low_df.head(10)}\n")

            # allow user to input how many counties they would like to contact of each population level
            high = int(input("Number of HIGH (>10000000) population counties you would like to contact: "))
            mid = int(input("Number of MEDIUM (>1000000) population counties you would like to contact: "))
            low = int(input("Number of LOW (>1000) population counties you would like to contact: "))
            none = int(
                input("Number of (None) population counties with NO POPULATION DATA you would like to contact:"))

            EmailSender.send_emails(graph, high_df, mid_df, low_df, none_df, high, mid, low, none)
        # display to user counties that have been contacted during this session
        elif choice == 3:
            df = pd.read_pickle('pickles/CountiesJustContacted.pkl')
            if df.empty:
                print("\nNo NAMI Chapters have been contacted during this session yet\n")
            else:
                print(f"\n~~~~~~~~~~~NAMI CHAPTERS CONTACTED DURING THIS SESSION~~~~~~~~~~~\n")
                print(df.to_string())
        # display to user ALL counties that have been contacted
        elif choice == 4:
            df = pd.read_pickle('pickles/AllContactedCounties.pkl')
            if df.empty:
                print("\n\nNo NAMI Chapters have been contacted yet.")
            else:
                print(f"\n~~~~~~~~~~~ALL CONTACTED NAMI CHAPTERS~~~~~~~~~~~\n")
                print(df.to_string())
        # elif choice == 5:
        #     utils.flyer_upload()
        # hidden option from user dashboard, reset all data including all counties that have been contacted
        elif choice == 9:
            if input("\nARE YOU SURE YOU WANT TO RESET ALL DATA!?!?!?!!? (y/n)\n") == "y":
                df = pd.read_pickle("pickles/NAMI_DATA.pkl")
                utils.reset_data(df)
        else:
            print('Invalid choice!\n')


if __name__ == "__main__":
    main()

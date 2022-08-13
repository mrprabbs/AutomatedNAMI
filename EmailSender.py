import pandas as pd
from graph import Graph
import config


def greet_user(graph: Graph):
    """
    A  simple function that calls the graph object and displays username

    Parameters
    ----------
    :param graph: Graph object
         Allows interaction with Graph REST API
    """
    user = graph.get_user()
    print('Hello,', user['displayName'])
    # For Work/school accounts, email is in mail property
    # Personal accounts, email is in userPrincipalName
    print('Email:', user['mail'] or user['userPrincipalName'], '\n')


def display_access_token(graph: Graph):
    """
    A function that displays the user's token key from the graph object

    Parameters
    ----------
    :param graph: Graph object
         Allows interaction with Graph REST API
    """
    token = graph.get_user_token()
    print('User token:', token, '\n')


def send_mail(graph: Graph, recipient):
    """
    Function that sends an email to a specific recipient using the post request from the graph method send_mail

    Parameters
    ----------
    :param graph: Graph object
         Allows interaction with Graph REST API
    :param recipient: str
        Customizable receiver of email


    """
    # Send mail to the recipient
    # graph.send_mail(config.subject, config.message, 'pskukreja@wisc.edu')
    graph.send_mail(config.subject, config.message, recipient)
    print(f'\nMail sent to {recipient}.\n')


def send_emails(graph: Graph, high_df, mid_df, low_df, none_df, high, mid, low, none):
    """
    Sends emails to users in different population categories based on user input of how many emails they would like to
    send to each category

    :param graph: Graph Object
         Allows interaction with Graph REST API
    :param high_df: Pandas Dataframe
        all NAMI Chapters that serve counties with high populations (>10000000)
    :param mid_df: Pandas Dataframe
        all NAMI Chapters that serve counties with medium populations (>1000000)
    :param low_df: Pandas Dataframe
        all NAMI Chapters that serve counties with low populations (>1000)
    :param none_df:Pandas Dataframe
        all NAMI Chapters that do not have a population listed for the counties that they serve
    :param high: int
        number of high population NAMI Chapters that the user wants to send emails to
    :param mid: int
        number of medium population NAMI Chapters that the user wants to send emails to
    :param low: int
        number of low population NAMI Chapters that the user wants to send emails to
    :param none: int
        number of none population NAMI Chapters that the user wants to send emails to
    :return:
    """
    # iterate through all population dataframes as many times as user chooses
    contacted_list = list()
    for high_key, high_val in high_df.iterrows():
        if high_key < high:
            # send_mail(graph, 'pskukreja@wisc.edu')
            send_mail(graph, high_val['Email'])  # send email to recipient using graph API
            high_df = high_df.drop(high_key)  # remove NAMI Chapter from dataframe
            high_df = high_df.reset_index(drop=True)  # reset index of dataframe
            contacted_list.append(high_val['Email'])  # add NAMI Chapter to list of contacted chapters
    # This basic logic is repeated because pandas dataframe cannot be edited through reference
    for mid_key, mid_val in mid_df.iterrows():
        if mid_key < mid:
            send_mail(graph, mid_val['Email'])
            mid_df = mid_df.drop(mid_key)
            mid_df = mid_df.reset_index(drop=True)
            contacted_list.append(mid_val['Email'])

    for low_key, low_val in low_df.iterrows():
        if low_key < low:
            send_mail(graph, low_val['Email'])
            low_df = low_df.drop(low_key)
            low_df = low_df.reset_index(drop=True)
            contacted_list.append(low_val['Email'])

    for none_key, none_val in none_df.iterrows():
        if none_key < none:
            send_mail(graph, none_val['Email'])
            none_df = none_df.drop(none_key)
            none_df = none_df.reset_index(drop=True)
            contacted_list.append(none_val['Email'])
    # print(f"Contacted Emails: {contacted_list}")
    contacted_df = pd.DataFrame(contacted_list, columns=["Contacted Emails"])
    contacted_df.to_pickle("pickles/CountiesJustContacted.pkl")
    try:
        prev_contacted_df = pd.read_pickle("pickles/AllContactedCounties.pkl")
        all_contacted_df = pd.concat([prev_contacted_df, contacted_df])
        all_contacted_df = all_contacted_df.drop_duplicates()
        all_contacted_df = all_contacted_df.reset_index(drop=True)
        all_contacted_df.to_pickle("pickles/AllContactedCounties.pkl")
    except EOFError: # error if no counties have been contacted yet
        # First time emailing counties
        prev_contacted_df = contacted_df
        prev_contacted_df = prev_contacted_df.drop_duplicates()
        prev_contacted_df = prev_contacted_df.reset_index()
        prev_contacted_df.to_pickle("pickles/AllContactedCounties.pkl")

    # load updated list of counties that have not been contacted yet to pickles for later
    high_df.to_pickle("pickles/HighPopulationCounties_notContacted.pkl")
    mid_df.to_pickle("pickles/MiddlePopulationCounties_notContacted.pkl")
    low_df.to_pickle("pickles/LowPopulationCounties_notContacted.pkl")
    none_df.to_pickle("pickles/NonePopulationCounties_notContacted.pkl")

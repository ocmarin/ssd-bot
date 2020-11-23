import Levenshtein as lev
import pandas as pd
import praw
import pickle
import os
import time
import string
import requests
import io
import re

def simplifytitle(title: str) -> str:
    title = title.lower()
    # Deletes anything in [] (inclusive)
    title = re.sub("\[(.*?)\] ", "", title)
    title = title.replace("portable", "port.").replace("\n", "")
    return title

def simplelev (title: str, data : {}) -> {}:
    cur = 0
    comparison = {}
    title = simplifytitle(title)
    while cur < len(data):
        brand = str(data.iloc[cur, 0]).lower()
        model = str(data.iloc[cur, 1]).lower()
        # If the brand is in the title
        if brand in title or (
                "adata" == brand and "xpg" in title) or (
                "wd" == brand and "western digital" in title):
            # Brand in title
            comparison[cur] = lev.distance(brand + model, title)
            #print("Comparison added!")
        cur += 1
    return comparison

def weightedlev(title: str, data:{}) ->{}:
    cur = 0
    comparison = {}
    title = simplifytitle(title)
    while cur < len(data):
        brand = str(data.iloc[cur, 0]).lower()
        model = str(data.iloc[cur, 1]).lower()
        # If the brand is in the title
        if brand in title or (
                "adata" == brand and "xpg" in title) or (
                "wd" == brand and "western digital" in title):
            # Brand in title
            comparison[cur] = lev.distance(brand + model, title)
            #print("Comparison added!")
            for word in model.split("/"):
                if word != "nan" and word in title:
                    print(f"{word} is in {title}")
                    comparison[cur] -= 5 * len(word)
            for word in model.split():
                if word != "nan" and word in title:
                    print(f"{word} is in {title}")
                    comparison[cur] -= 5 * len(word)
        cur += 1
    return comparison

def selectivelev (title: str, data: {}) -> {}:
    cur = 0
    comparison = {}
    title = simplifytitle(title)
    while cur < len(data):
        brand = str(data.iloc[cur, 0]).lower()
        model = str(data.iloc[cur, 1]).lower()
        # If the brand is in the title
        if brand in title or (
                "adata" == brand and "xpg" in title) or (
                "wd" == brand and "western digital" in title):
            # Brand in title
            # for word in model.split():
            #     if word != "nan" and word in title:
            #         modelfound = True
            #         comparison[cur] = lev.distance(brand + model, title) \
            #             - 5*len(word)
            #         break
            for words in model.split("/"):
                for word in words.split():
                    if word != "nan" and word in title and ("gen4" in title if "gen4" in word else True):
                        # print(f"Found {word} in {title}\n")
                        comparison[cur] = (lev.distance(brand + " "+ model, title) \
                            - 5*len(word)) if cur not in comparison else (comparison[cur]-5*len(word))
                    elif cur in comparison:
                        print(f"Couldn't find {word} in {title}")
                        comparison[cur] += len(word)
        cur += 1
    return comparison

def word_match(title: str, data: {}) ->{}:
    """Gets the best match for the given SSD. This algorithm
       bases itself mostly on how many of the model words are in
       the title itself.

       Ex: "Samusung word 970 Evo" contains 970 and Evo, so when "970 Evo"
       is compared to the title, it does well unlike "860 QVO" or other models.

        The title is the text to try to find an appropriate match for.
        The data is a dictionary of SSDs in which the 0th and 1st index
        of each entry are the brand and model, respectively.

    Returns:
        dict: A dictionary of all the comparisons made. The key
        signifies the row that the SSD was found in within the
        provided data.
    """
    # Keeps track of which SSD is being parsed through.
    cur = 0
    # Keeps track of all comparisons being made.
    # The key being the SSD number,
    # and the value is how similar to the model the title is.
    comparison = {}
    # Simplify the title to make easier to parse.
    title = simplifytitle(title)
    # Continue to loop through until we are out of data.
    while cur < len(data):
        # Get the brand and model from the data.
        brand = str(data.iloc[cur, 0]).lower()
        model = str(data.iloc[cur, 1]).lower()
        # If the brand is in the title
        if brand in title or (
                "adata" == brand and "xpg" in title) or (
                "wd" == brand and "western digital" in title):
            # For the occassional SSDs that have a slash
            for words in model.split("/"):
                # For every word (whitespace in between) within each split.
                for word in words.split():
                    if word != "nan" and word in title:
                        print(f"Found {word} in {title}")
                        comparison[cur] = -len(word) if cur not in comparison else comparison[cur]-len(word)
                    elif word not in title and cur in comparison:
                        # print(f"Couldn't find {word} in {title}")
                        comparison[cur] += len(word)
            #print(comparison)
        cur += 1
    return comparison

def best_match(comparisons: {}, getlowest: bool=True) -> {}:
    """Gets the best match from the given set of comparisons.

    Returns:
        dict: A dictionary containing the information that best matches.
        None: When there is no good match, such as comparisons containg no info.
    """
    if len(comparisons) == 0:
        return None
    return min(comparisons, key=comparisons.get) if getlowest  else max(comparisons, key=comparisons.get)

def get_sheet_values(url):
    """Simply returns the values within the spreadsheet at the URL given.

    Args:
        url (string): The url to look for the data at.

    Returns:
        dict: The information at the URL.
    """
    r_csv = requests.get(url).content
    df = pd.read_csv(io.StringIO(r_csv.decode("utf-8")))

    return df


def main():
    data = get_sheet_values(
        url="https://docs.google.com/spreadsheets/d/1B27_j9NDPU3cNlj2HKcrfpJKHkOf-Oi1DbuuQva2gT4/export?format=csv")
    with open("posts.txt", "r") as posts:
        lines = posts.readlines()
        # print(f"Lines extracted: {lines}")
        for line in lines:
            comp = word_match(line, data)
            # for key in comp:
            #     print(f"Simplelev of {data.iloc[key, 0]} {data.iloc[key, 1]}: {comp[key]}")
            with open("priority.log", "a") as sl:
                if len(comp) == 0:
                    sl.write(f"NULL\n")
                    continue
                guess = min(comp, key=comp.get)
                gbrand = data.iloc[guess, 0]
                gmodel = data.iloc[guess, 1]
                if gbrand == "nan":
                    sl.write(f"NULL\n")
                    continue
                sl.write(f"{gbrand} {gmodel}\n")


if __name__ == "__main__":
    main()
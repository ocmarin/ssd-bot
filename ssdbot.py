import pandas as pd
import praw
import os
import time
from praw.models.reddit.subreddit import ContributorRelationship
from praw.reddit import Reddit
import requests
import io
import re

DEBUG = False


def main():
    # Credentials to logon to a Reddit account.
    client_id = os.environ["CLIENT_ID"]
    client_secret = os.environ["CLIENT_SECRET"]
    password = os.environ["SSDBOT_PASSWORD"]

    # Instantiate the Reddit object w/ account. using praw.
    reddit = praw.Reddit(
        client_id=client_id,
        client_secret=client_secret,
        user_agent="windows:in.ocielmar.ssdbot:v0.2 (by u/TheEpicPie & u/cambriancatalyst)",
        username="SSDBot",
        password=password,
    )

    # Get this subreddit.
    bapcs = reddit.subreddit("BuildAPCSales")
    # Get the data stored in a pretty dictionary.
    data = get_sheet_values(
        url="https://docs.google.com/spreadsheets/d/1B27_j9NDPU3cNlj2HKcrfpJKHkOf-Oi1DbuuQva2gT4/export?format=csv")
    # This loop will continue until the end of time.
    while True:
        print("[INFO] Checking recent posts...")
        # Keep track of time to know how long to sleep.
        start_time = time.time()
        # Go through the last 10 new submissions in bapcs.
        for sub in bapcs.new(limit=10):
            # If the submission is not flaired at all, ignore it.
            if not sub.link_flair_text:
                continue
            # If the submission is flaired as an SSD.
            if "SSD" in sub.link_flair_text:
                print(f"[INFO] Found SSD Post: {sub.title}")
                # Keep track of whether or not this bot has commented.
                found = False
                # Check every comment to see if this bot has commented.
                for comment in sub.comments:
                    if comment.author and comment.author.name == "SSDBot":
                        found = True
                        if DEBUG:
                            # Print SSD object info when debugging.
                            print(find_ssd(sub.title, data))
                        print("[INFO] Already commented on this.")
                        break
                # If the bot hadn't commented on this submission before.
                if not found:
                    # Use the func to find an SSD matching this data.
                    ssd = find_ssd(sub.title, data)
                    # If the func returned None, pack it up.
                    if not ssd:
                        break
                    # Constructing the string that will makeup the comment.
                    # Looks messy but trust it looks fine in Reddit's markdown.
                    # See: https://www.reddit.com/wiki/markdown
                    print(ssd[10])
                    reply = f"The {ssd[0]} {ssd[1]} is a " + (f"*{ssd[10]}* " if
                                                              type(ssd[10]) is not float else "") + f"**{ssd[14]}** SSD.\n\n" + \
                        f"* Interface: **{ssd[2]}**\n\n* Form Factor: **{ssd[3]}**\n\n* Controller: **{ssd[5]}**\n\n* Configuration: **{ssd[6]}**\n\n" + \
                        f"* DRAM: **{ssd[7]}**\n\n* HMB: **{ssd[8]}**\n\n* NAND Brand: **{ssd[9]}**\n\n* NAND Type: **{ssd[10]}**\n\n* 2D/3D NAND: **{ssd[11]}**\n\n" + \
                        f"* Layers: **{ssd[12]}**\n\n* R/W: **{ssd[13]}**\n\n[Click here to view this SSD in the tier list](https://docs.google.com/spreadsheets/d/1B27_j9NDPU3cNlj2HKcrfpJKHkOf-Oi1DbuuQva2gT4/edit#gid=0&range=A{ssd[15]}:V{ssd[15]})\n\n" + \
                        f"[Click here to view camelcamelcamel product search page]({ssd[16]})."
                    # Continue adding more to the reply,
                    # specifically the feedback request.
                    reply += f"\n\n---\n^(Suggestions, concerns, errors? Message us directly or submit an issue on) [^(Github!)](https://github.com/ocmarin/ssd-bot)"
                    print("[COMMENT]\n" + reply)
                    # Makes the bot post the comment/reply.
                    if not DEBUG:  # Only submit a comment when not debugging.
                        sub.reply(reply)
                        print(
                            f"[INFO] Posted at https://reddit.com{sub.permalink}")

        check_mismatches(reddit, "SSDBot", 10)
        # Comparisons function to be implemented.
        # check_for_comparisons(reddit, 20, data)
        time.sleep(60.0 - ((time.time() - start_time) % 90))  # Sleepy time


def chart_ssd(*args) -> str:
    """Formats the given SSD into a nice chart.

    Args:
        ssd (str): Data containing the SSD's information. Should be in the following order:
        Model, Brand, Interface, Form Factor, NONE, Controller, Configuration, DRAM, HMB,
        NAND Brand, Nand Type, 2/3D NAND, Layers, R/W Speed, NONE, tier-index, Camel Search Page

    Returns:
        str: The nicely formatted string that is human friendly when combined into a chart.
    """
    print("IN PAIN")

    # This method is not efficient at all.
    pain = f"|SSD"
    for ssd in args:
        pain = pain + f"|{ssd[0]} {ssd[1]}"
    pain = pain+f"|\n|:-:"
    for ssd in args:
        pain = pain + "|:-:"
    pain = pain+"|\n|Tier"
    for ssd in args:
        pain = pain+f"|{ssd[10]}"
    pain = pain+"|\n|Interface"
    for ssd in args:
        pain = pain + f"|{ssd[2]}"
    pain = pain + "|\n|Form Factor"
    for ssd in args:
        pain = pain+f"|{ssd[3]}"
    pain = pain+"|\n|Controller"
    for ssd in args:
        pain = pain+f"|{ssd[5]}"
    pain = pain+"|\n|Configuration"
    for ssd in args:
        pain = pain+f"|{ssd[6]}"
    pain = pain+"|\n|DRAM"
    for ssd in args:
        pain = pain+f"|{ssd[7]}"
    pain = pain+"|\n|HMB"
    for ssd in args:
        pain = pain+f"|{ssd[8]}"
    pain = pain+"|\n|NAND Brand"
    for ssd in args:
        pain = pain+f"|{ssd[9]}"
    pain = pain+"|\n|NAND Type"
    for ssd in args:
        pain = pain+f"|{ssd[10]}"
    pain = pain+"|\n|2D/3D NAND"
    for ssd in args:
        pain = pain+f"|{ssd[11]}"
    pain = pain+"|\n|Layers"
    for ssd in args:
        pain = pain+f"|{ssd[12]}"
    pain = pain+"|\n|R/W"
    for ssd in args:
        pain = pain+f"|{ssd[13]}"
    pain = pain+"|\n|Tier Link"
    for ssd in args:
        pain = pain + \
            f"|[Link](https://docs.google.com/spreadsheets/d/1B27_j9NDPU3cNlj2HKcrfpJKHkOf-Oi1DbuuQva2gT4/edit#gid=0&range=A{ssd[15]}:V{ssd[15]})"
    pain = pain+"|"
    return pain


def check_for_comparisons(reddit: Reddit, posts: int, data: dict):
    # TODO: Not familar with what data types these return.
    # I just wanted to cycle through the comments of recent comments from the bot.

    for comment in reddit.redditor("SSDBot").comments.new(limit=posts):
        # Cycle through all the last x comments by the bot.
        for reply in comment.replies:
            if "vs" in str.lower(reply.body):
                first = comment[comment.body.index(
                    " "+1):comment.body.index("is")-1]
                second = reply.body[reply.body.index("vs") + 3:]
                print(
                    f"[INFO] Found an attempted comparison on {first} against {second}!")
                contender = find_ssd(first, data)
                challenger = find_ssd(second, data)
                comp = chart_ssd(contender, challenger) + \
                    f"\n\n---\n^(Suggestions, concerns, errors? Message us directly or submit an issue on [Github!](https://github.com/ocmarin/ssd-bot))"
                if not DEBUG:
                    reply.reply(comp)
                    print(
                        f"[COMPARISON] Made a comparison post at: https://reddit.com{reply.permalink}")


def check_mismatches(reddit: Reddit, user: str, posts: int):
    for comment in reddit.redditor(user).comments.new(limit=posts):
        # Cycle through all the last x comments for the given redditor.
        if comment.score <= -3:
            # If the bot receives enough downvotes, edit the comment.
            body = comment.body
            sub = comment.submission
            print(
                f"[INFO] Negative score on comment: https://reddit.com{comment.permalink}")
            if " is a " not in body:
                # If this phrase isn't in the comment, it has been edited.
                print("[INFO] Incorrect guess already edited.")
                break
            # If the comment with SSD info was downvoted, get the guessed SSD.
            guessed = body[4:body.index(" is")]
            # Write to log saying what the mismatch was.
            with open("mismatches.txt", "a") as mlog:
                mlog.write(
                    f"{simplifytitle(sub.title)} =/= {guessed}\n")
            # Edit the comment to prevent any further confusion.
            edit = f"My guess ({guessed}) was **incorrect**. This incident has been recorded." + \
                "\n\n*Sorry for any confusion, humans!*" + \
                "\n\n---\n^(Suggestions, concerns, errors? Message us directly or " + \
                "submit an issue on) [^(Github!)](https://github.com/ocmarin/ssd-bot)"
            print(f"[EDIT] {edit}")
            if not DEBUG:
                comment.edit(edit)


def simplifytitle(title: str) -> str:
    """Simplifies the titles down to make easier to parse.

    Specifically, makes the titles lowercase and removes anything within square brackets([]).

    Args:
        title (str): The title to dumb down for easier navigation through.

    Returns:
        str: The given title in lowercase with unneccessary data removed.
    """
    title = title.lower()
    # Deletes anything in [] (inclusive)
    title = re.sub("\[(.*?)\] ", "", title)
    title = title[:40].replace("portable", "port.").replace("\n", "")
    return title


def word_match(title: str, data: dict) -> dict:
    """Gets the best match for the given SSD.
        This algorithm bases itself mostly on how many of the model words are in the title itself. Ex: "Samusung word 970 Evo" contains 970 and Evo, so when "970 Evo" is compared to the title, it does well unlike "860 QVO" or other models.

        The title is the text to try to find an appropriate match for. The data is a dictionary of SSDs in which the 0th and 1st index of each entry are the brand and model, respectively.

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
                    # If the data didn't return "nan"
                    # and a word within the model is in the title.
                    if word != "nan" and word in title:
                        # print(f"Found {word} in {title}")
                        # Add this to our comparison, if already
                        # within the comparison, further subtract its value.
                        comparison[cur] = - \
                            len(word) if cur not in comparison else comparison[cur]-len(
                                word)
                    # If a word within the model is not in the title but has had other matches.
                    elif word not in title and cur in comparison:
                        # Add more to the number, signifying
                        # that there is a larger difference.
                        comparison[cur] += len(word)
            # print(comparison)
        # Since Python doesn't have traditional for loops, we make our own.
        cur += 1
    # Returns each comparison made, higher number = higher differnce.
    return comparison


def best_match(comparisons: dict, getlowest: bool = True) -> dict:
    """Gets the key of the best match from the given set of comparisons.

    Returns:
        dict: A dictionary containing the information that best matches.
        None: When there is no good match, such as comparisons containg no info.
    """
    # If there is nothing within the given comparisons dictionary, just return None.
    if len(comparisons) == 0:
        return None
    match = min(comparisons, key=comparisons.get) if getlowest else max(
        comparisons, key=comparisons.get)
    if comparisons[match] >= -1 if getlowest else comparisons[match] <= 1:
        match = None
    # Otherwise, return either the highest or lowest in the comparisons; depending on what bool getlowest is.
    return match


def find_ssd(title: str, data: dict):
    """Finds an SSD within the title string using the given data.

    Args:
        title (str): The string to look for an SSD model in.
        data (dict): A set of data in which, for the sake of this function,
        assumes the format is equivalent to that of the NewMaxx SSD spreadsheet.

    Returns:
        dict: A dictionarty containing the SSD's information. The indices of which give the same info as the aforementioned spreadsheet.
    """
    # If there is no data submitted. :(
    if data.empty:
        print("[ERROR] Couldn't retrieve SSD information!")

    ind = best_match(word_match(title, data))

    if not ind:
        return None

    # The match is the best SSD with the least lev distance from the title
    brand = data.iloc[ind, 0]
    model = data.iloc[ind, 1]
    interface = data.iloc[ind, 2]
    ffactor = data.iloc[ind, 3]
    capacity = data.iloc[ind, 4]
    controller = data.iloc[ind, 5]
    ssd_config = data.iloc[ind, 6]
    dram = data.iloc[ind, 7]
    hmb = data.iloc[ind, 8]
    nand_brand = data.iloc[ind, 9]
    nand_type = data.iloc[ind, 10]
    nand_2d_3d = data.iloc[ind, 11]
    layers = data.iloc[ind, 12]
    r_w = data.iloc[ind, 13]
    category = data.iloc[ind, 14]
    index = ind + 2
    storage_match = re.search("(\d+)TB|(\d+)GB|(\d+)tb|(\d+)gb", title)
    clean_value_dict = {" ": "+", "(": "+", ")": ""}
    camel_url = "https://camelcamelcamel.com/search?sq="

    match = [brand, model, interface, ffactor, capacity, controller, ssd_config, dram,
             hmb, nand_brand, nand_type, nand_2d_3d, layers, r_w, category, index, camel_url]
    # print("[MATCH] Comparison Info: " + str(comparison))
    print("[MATCH] " + str(match[0]) + " " +
          str(match[1]) + " is the best fit!")
    return match


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


if __name__ == "__main__":
    main()

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


# Used for non-public spreadsheets

# from google.auth.transport.requests import Request
# from google_auth_oauthlib.flow import InstalledAppFlow
# from googleapiclient.discovery import build

def main():
    client_id = os.environ["CLIENT_ID"]
    client_secret = os.environ["CLIENT_SECRET"]
    password = os.environ["SSDBOT_PASSWORD"]

    reddit = praw.Reddit(
        client_id=client_id,
        client_secret=client_secret,
        user_agent="windows:in.ocielmar.ssdbot:v0.1 (by u/TheEpicPie & u/cambriancatalyst)",
        username="SSDBot",
        password=password,
    )

    bapcs = reddit.subreddit("BuildAPCSales")
    data = get_sheet_values(
        url="https://docs.google.com/spreadsheets/d/1B27_j9NDPU3cNlj2HKcrfpJKHkOf-Oi1DbuuQva2gT4/export?format=csv")
    while True:
        print("[INFO] Checking recent posts...")
        start_time = time.time()
        for sub in bapcs.new(limit=20):
            if not sub.link_flair_text:
                continue
            if "SSD" in sub.link_flair_text:
                print(f"[INFO] Found SSD Post: {sub.title}")
                found = False
                for comment in sub.comments:
                    if comment.author and comment.author.name == "SSDBot":
                        found = True
                        print(find_ssd(sub.title, data))
                        print("[INFO] Already commented on this.")
                        break
                if not found:
                    ssd = find_ssd(sub.title, data)
                    if not ssd:
                        break
                    reply = f"The {ssd[0]} {ssd[1]} is a " + (f"*{ssd[10]}* " if len(
                        ssd[10]) > 0 else "") + f"**{ssd[14]}** SSD.\n\nHere is some more data from " + \
                        f"[NewMaxx's SSD Spreadsheet](https://docs.google.com/spreadsheets/d/1B27_j9NDPU3cNlj2HKcrfpJKHkOf-Oi1DbuuQva2gT4/):\n\n" + \
                        f"* Interface: **{ssd[2]}**\n\n* Form Factor: **{ssd[3]}**\n\n* Controller: **{ssd[5]}**\n\n* Configuration: **{ssd[6]}**\n\n" + \
                        f"* DRAM: **{ssd[7]}**\n\n* HMB: **{ssd[8]}**\n\n* NAND Brand: **{ssd[9]}**\n\n* NAND Type: **{ssd[10]}**\n\n* 2D/3D NAND: **{ssd[11]}**\n\n" + \
                        f"* Layers: **{ssd[12]}**\n\n* R/W: **{ssd[13]}**\n\n[Click here to view this SSD in the tier list](https://docs.google.com/spreadsheets/d/1B27_j9NDPU3cNlj2HKcrfpJKHkOf-Oi1DbuuQva2gT4/edit#gid=0&range=A{ssd[15]}:V{ssd[15]})\n\n" + \
                        f"[Click here to view camelcamelcamel product search page]({ssd[16]})."

                    reply += f"\n\n---\n^(Suggestions, concerns, errors? Message us directly or submit an issue on [^Github!](https://github.com/ocmarin/ssd-bot))"
                    print("[COMMENT BEING SUBMITTED]\n" + reply)
                    sub.reply(reply)
                    print(f"[INFO] Posted at reddit.com{sub.permalink}")
        time.sleep(60.0 - ((time.time() - start_time) % 60))  # Sleep


def find_ssd(title: str, data):
    if data.empty:
        print("[ERROR] There was an error getting SSD information!")

    cur = 0
    comparison = {}
    # Equalizes lev distance for title length variance
    title = title[:50]
    while cur < len(data):
        # If the brand is in the title
        if str(data.iloc[cur, 0]).lower() in title.lower() or (
                "adata" == str(data.iloc[cur, 0]).lower() and "xpg" in title.lower()) or (
                "wd" == str(data.iloc[cur, 0]).lower() and "western digital" in title.lower()):
            # Get one model if many are in the model cel
            # After checking if brand is in title
            # add the index and its corresponding dist to comparison
            comparison[cur] = lev.distance(
                title.lower(), str(data.iloc[cur, 1]).lower().replace('ssd (new)', ''))
            if str(data.iloc[cur, 1]).lower() in title.lower():
                comparison[cur] -= (2 * len(str(data.iloc[cur, 1]).lower()))
        cur += 1
    if len(comparison) <= 0:
        print("[ERROR] SSD could not be found.")
        return None
    # The match is the best SSD with the least lev distance from the title
    brand = data.iloc[min(comparison, key=comparison.get), 0]
    model = data.iloc[min(comparison, key=comparison.get), 1]
    interface = data.iloc[min(comparison, key=comparison.get), 2]
    ffactor = data.iloc[min(comparison, key=comparison.get), 3]
    capacity = data.iloc[min(comparison, key=comparison.get), 4]
    controller = data.iloc[min(comparison, key=comparison.get), 5]
    ssd_config = data.iloc[min(comparison, key=comparison.get), 6]
    dram = data.iloc[min(comparison, key=comparison.get), 7]
    hmb = data.iloc[min(comparison, key=comparison.get), 8]
    nand_brand = data.iloc[min(comparison, key=comparison.get), 9]
    nand_type = data.iloc[min(comparison, key=comparison.get), 10]
    nand_2d_3d = data.iloc[min(comparison, key=comparison.get), 11]
    layers = data.iloc[min(comparison, key=comparison.get), 12]
    r_w = data.iloc[min(comparison, key=comparison.get), 13]
    category = data.iloc[min(comparison, key=comparison.get), 14]
    index = min(comparison, key=comparison.get) + 2
    storage_match = re.search("(\d+)TB|(\d+)GB|(\d+)tb|(\d+)gb", title)
    clean_value_dict = {" ": "+", "(": "+", ")": ""}
    camel_url = "https://camelcamelcamel.com/search?sq="
    if storage_match:
        storage = storage_match.group(0)
        camel_values = [brand, model, storage]
        for value in camel_values:
            for i, j in clean_value_dict.items():
                value = value.replace(i, j)
            camel_url += value + "+"
        camel_url = camel_url[:-1]
        match = [brand, model, interface, ffactor, capacity, controller, ssd_config, dram,
                 hmb, nand_brand, nand_type, nand_2d_3d, layers, r_w, category, index, camel_url]
    else:
        camel_values = [brand, model]
        for value in camel_values:
            for i, j in clean_value_dict.items():
                value = value.replace(i, j)
            camel_url += value + "+"
        camel_url = camel_url[:-1]
        match = [brand, model, interface, ffactor, capacity, controller, ssd_config, dram,
                 hmb, nand_brand, nand_type, nand_2d_3d, layers, r_w, category, index, camel_url]
    print("[MATCH] Comparison Info: " + str(comparison))
    print("[MATCH] " + str(match[0]) + " " +
          str(match[1]) + " is the best fit!")
    return match


def get_sheet_values(url):
    r_csv = requests.get(url).content
    df = pd.read_csv(io.StringIO(r_csv.decode("utf-8")))

    # # Used for non-public spreadsheets

    # SCOPES = ["https://www.googleapis.com/auth/spreadsheets.readonly"]

    # creds = None
    # # The file token.pickle stores the user's access and refresh tokens, and is
    # # created automatically when the authorization flow completes for the first
    # # time.
    # if os.path.exists("token.pickle"):
    #     with open("token.pickle", "rb") as token:
    #         creds = pickle.load(token)
    # # If there are no (valid) credentials available, let the user log in.
    # if not creds or not creds.valid:
    #     if creds and creds.expired and creds.refresh_token:
    #         creds.refresh(Request())
    #     else:
    #         flow = InstalledAppFlow.from_client_secrets_file(
    #             "credentials.json", SCOPES)
    #         creds = flow.run_local_server(port=0)
    #     # Save the credentials for the next run
    #     with open("token.pickle", "wb") as token:
    #         pickle.dump(creds, token)

    # service = build("sheets", "v4", credentials=creds)

    # info = service.spreadsheets().values().get(
    #     spreadsheetId=sheetId, range=sheetRange).execute()

    # # Info holds the cells, this will get our values
    # return info.get("values", [])

    return df


if __name__ == "__main__":
    main()

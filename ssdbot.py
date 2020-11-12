from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import Levenshtein as lev
import praw
import pickle
import os.path
import time
import string


def main():
    reddit = praw.Reddit(
        client_id="5ri9KO7cP9Hniw",
        client_secret="uEm4hKsKjH-VPyO00t6AgRaDQshRNA",
        user_agent="windows:in.ocielmar.ssdbot:v0.1 (by u/TheEpicPie)",
        username="SSDBot",
        password="gF6tjY7taSi8kVq",
    )
    bapcs = reddit.subreddit("BuildAPCSales")
    data = get_sheet_values(
        sheetId="1B27_j9NDPU3cNlj2HKcrfpJKHkOf-Oi1DbuuQva2gT4", sheetRange="A1:Q270")
    while True:
        #print("[INFO] Checking recent posts...")
        start_time = time.time()
        for sub in bapcs.new(limit=5):
            if not sub.link_flair_text:
                continue
            if "SSD" in sub.link_flair_text:
                print(f"[INFO] Found SSD Post: {sub.title}")
                found = False
                for comment in sub.comments:
                    if comment.author and comment.author.name == "SSDBot":
                        found = True
                        # print(find_ssd(sub.title, data))
                        print("[INFO] Already commented on this.")
                        break
                if not found:
                    ssd = find_ssd(sub.title, data)
                    if not ssd:
                        break
                    reply = f"The {ssd[0]} {ssd[1]} is a " + (f"*{ssd[10]}* " if len(ssd[10]) > 0 else "") + f"**{ssd[14]}** SSD.\n\nHere is some more data from " + \
                        f"[NewMaxx's SSD Spreadsheet](https://docs.google.com/spreadsheets/d/1B27_j9NDPU3cNlj2HKcrfpJKHkOf-Oi1DbuuQva2gT4/):" + \
                        f"\n\n| Interface | Controller | Configuration | DRAM? | Layers | R/W (MB/s) |\n|---------|-----------|----------|----|---------|---|--------|\n" + \
                            f"| {ssd[2]} | {ssd[5]} | {ssd[6]} | {ssd[7]} | {ssd[12]} | {ssd[13]} |"
                    if(len(ssd) > 15 and len(ssd[15]) > 0):
                        reply += f"\n\nAdditional notes: {ssd[15]}."
                    reply += f"\n\n---\n^(Suggestions, concerns, errors? Message me directly!)"
                    print("[COMMENT BEING SUBMITTED]\n" + reply)
                    sub.reply(reply)
                    print(f"[INFO] Posted at reddit.com{sub.permalink}")
        time.sleep(60.0 - ((time.time() - start_time) % 60))  # Sleep


def find_ssd(title: str, data: []) -> []:
    if not data:
        print("[ERROR] There was an error getting SSD information!")

    cur = 0
    comparison = {}
    # Equalizes lev distance for title length variance
    title = title[:50]
    while cur < len(data):
        # If the brand is in the title
        if data[cur][0] in title or ("ADATA" in data[cur][0] and "XPG" in title) or ("WD" in data[cur][0] and "Western Digital" in title):
            # Get one model if many are in the model cel
            # After checking if brand is in title
            # add the index and its corresponding dist to comparison
            comparison[cur] = lev.distance(title, data[cur][1])
            if data[cur][1] in title:
                comparison[cur] -= (2 * len(data[cur][1]))
        cur += 1
    if len(comparison) <= 0:
        print("[ERROR] SSD could not be found.")
        return None
    # The match is the best SSD with the least lev distance from the title
    match = data[min(comparison, key=comparison.get)]
    #print("[MATCH] Comparison Info: " + str(comparison))
    print("[MATCH] " + str(match[0]) + " " +
          str(match[1]) + " is the best fit!")
    print(f"[DEBUG] Length of data: {len(match)}")
    return match


def get_sheet_values(sheetId: str, sheetRange: str) -> []:
    SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']

    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('sheets', 'v4', credentials=creds)

    info = service.spreadsheets().values().get(
        spreadsheetId=sheetId, range=sheetRange).execute()

    # Info holds the cells, this will get our values
    return info.get('values', [])


if __name__ == "__main__":
    main()

import os
import tweepy as tpy
import json
import csv
from datetime import datetime
from typing import Tuple, Dict
from dotenv import load_dotenv


def extract_msg(msg_dict: Dict, ulimit: int=151) -> Tuple[str, Dict]:
    msg = ''
    delkeys = []
    for cname, cinfo in msg_dict.items():
        if cinfo['days'] == 0:
            msg += f"{cname}: Today! Good Luck!\n"
        elif cinfo['days'] > 0 and cinfo['days'] < ulimit:
            msg += f"{cname}: {cinfo['days']} days\n"
        elif cinfo['days'] < 0:
            delkeys.append(cname)

    for k in delkeys:
        del msg_dict[k]

    return msg, msg_dict

def get_deadlines_msg(csvfile: str) -> str:
    with open(csvfile, newline='') as f:
        reader = csv.reader(f)
        deadlines = list(reader)

    date_frmt = '%d-%m-%Y'
    msg_dict = {}
    for dl in deadlines:
        cname = dl[0].strip()
        date = dl[1].strip()
        today = datetime.now().strftime(date_frmt)
        days_left = datetime.strptime(date, date_frmt) - datetime.strptime(today, date_frmt)
        msg_dict[cname] = {'date': date, 'days':days_left.days}

    msg_dict = {k: v for k, v in sorted(msg_dict.items(), key=lambda item: item[1]['days'])}
    msg, msg_dict = extract_msg(msg_dict)

    # Remove the passed deadline from the csv file
    with open(csvfile, 'w', newline='') as f:
        writer = csv.writer(f)
        for cname, days_left in msg_dict.items():
            date = days_left['date']
            writer.writerow([cname, date])

    return msg


if __name__ == '__main__':
    root_path = './'
    load_dotenv(os.path.join(root_path, '.env'))
    # json_file = os.path.join(root_path, 'keys.json')
    # with open(json_file) as f:
    #     acnts = json.load(f)
    #     dev = acnts['dev']
    #     bot1 = acnts['bot1']

    consumer_key = os.getenv("DEV_CONSUMER_KEY")
    consumer_secret = os.getenv("DEV_CONSUMER_SECRET")
    bot1_access_token = os.getenv("BOT_ACCESS_TOKEN")
    bot1_access_token_secret = os.getenv("BOT_ACCESS_TOKEN_SECRET")

    # Authenticate to Twitter with the bot account
    client = tpy.Client(consumer_key=consumer_key,
                        consumer_secret=consumer_secret,
                        access_token=bot1_access_token,
                        access_token_secret=bot1_access_token_secret)


    csvfile = os.path.join(root_path, 'dl.csv')
    msg = get_deadlines_msg(csvfile)
    msg = '\n'.join(msg.split('\n'))
    print(f'Tweeting:\n{msg}')

    # Tweet the message
    cres = client.create_tweet(text=msg)
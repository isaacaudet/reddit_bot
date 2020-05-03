import time
import matplotlib.pyplot as plt
import pandas as pd
import praw
from fuzzywuzzy import fuzz
from fuzzywuzzy import process
from collections import defaultdict

reddit = praw.Reddit(client_id='lFJMpcqjHFSn-g', client_secret='Rlm0bZ1wf7smLFAzJJB5uguTqBk',
                     user_agent='Reddit Scrape')


# Uses fuzzywuzzy to get match ratio between comment strings and index k in the dictionary

def get_ratio(row, k):
    name = row['comments']
    return fuzz.token_sort_ratio(name, k)


# Uses PRAW to append N reddit post titles/comments from a specified subreddit.
# Converts lists to a Panda DataFrame, which is converted to a CSV file.
# Prints num of comments scraped + time elapsed.

def comment2csv(posts, subreddit, sort):
    start = time.time()
    comment_count = 0
    comm_list = []
    header_list = []
    if sort == 'top':
        sorting = reddit.subreddit(subreddit).top(limit=posts)
    elif sort == 'new':
        sorting = reddit.subreddit(subreddit).new(limit=posts)
    else:
        sorting = reddit.subreddit(subreddit).hot(limit=posts)

    for submission in sorting:
        submission.comments.replace_more(limit=None)
        comment_queue = submission.comments[:]
        while comment_queue:
            header_list.append(submission.title)
            comment = comment_queue.pop(0)
            comm_list.append(comment.body)
            comment_count += 1
            t = []
            t.extend(comment.replies)
            while t:
                header_list.append(submission.title)
                reply = t.pop(0)
                comm_list.append(reply.body)
                comment_count += 1

    df = pd.DataFrame(header_list)
    df['comm_list'] = comm_list
    df.columns = ['header', 'comments']
    df['comments'] = df['comments'].apply(lambda x: x.replace('\n', ''))
    df.to_csv(subreddit + '.csv', index=False)

    end = time.time()
    print(str(comment_count) + ' comments scraped in: ' + str("{:.2f}".format(end - start)))


# Opens CSV file and reads it using Panda. Checks substring match ratio using fuzzywuzzy.
# Increments dictionary value by the ammount of matches above 70%.

def csv_counter(subreddit, dictionary):
    start = time.time()
    with open(subreddit + '.csv', 'r', encoding='utf-8') as data_csv:
        data = pd.read_csv(data_csv, index_col=False)
        for j in data['comments']:
            for k in dictionary.keys():
                choices = j.split()
                possibilities = process.extract(k, choices, scorer=fuzz.token_sort_ratio)
                dictionary[k] += len([possible for possible in possibilities if possible[1] > 70])
    end = time.time()
    print('Dictionary scraped in: ' + str("{:.2f}".format(end - start)))


# Plots dictionary data using bar graph.

def plot_data(dictionary):
    plt.bar(range(len(dictionary)), dictionary.values(), align='center')
    plt.xticks(range(len(dictionary)), list(dictionary.keys()))
    plt.show()


if __name__ == '__main__':
    sub = input('Enter subreddit to scrape: ')
    lim = int(input('Enter number of posts to scrape: '))
    sort = input('Enter the sorting mode[default=hot]: ')
    custom_dict = input('Custom Dictionary?[Y/N]')
    if custom_dict == 'Y':
        d = defaultdict(int)
        keys = input('Enter keys seperated by a space: ').split()
        for i in keys:
            d[i]
    else:
        d = {'brimstone': 0, 'sage': 0, 'breach': 0, 'sova': 0, 'jet': 0, 'cypher': 0, 'viper': 0, 'raze': 0,
             'phoenix': 0,
             'omen': 0}

    comment2csv(lim, sub, sort)
    csv_counter(sub, d)
    plot_data(d)

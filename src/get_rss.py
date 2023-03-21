# coding=utf-8
import feedparser
import pandas as pd
from sentence_transformers import SentenceTransformer
import umap

# This is AP News at the moment, but can add multiple RSS feeds
# TODO make this a feed list
ap = feedparser.parse('https://news.google.com/rss/search?q=when:24h+allinurl:apnews.com&hl=en-US&gl=US&ceid=US:en')
bb = feedparser.parse('https://news.google.com/rss/search?q=when:24h+allinurl:bloomberg.com&hl=en-US&gl=US&ceid=US:en')
hn = feedparser.parse('https://hnrss.org/best')
lw = feedparser.parse('https://www.lesswrong.com/feed.xml')
 
# Make a function out of this
def rss_to_df(feed, source):
    '''
    Description: Takes a feedparser object and converts it to a Pandas DataFrame
    Args:
        feed: A feedparser object
    Returns: A Pandas DataFrame
    '''
    df = pd.DataFrame({'title': feed.entries[0].title, 'link': feed.entries[0].link, 'published': feed.entries[0].published}, index=[0])
    for i in range(len(feed.entries)):
        entry = feed.entries[i]
        curr = pd.DataFrame({'title': entry.title, 'link': entry.link, 'published': entry.published}, index=[i])
        df = df.append(curr)
    df = df.reset_index(drop=True)
    df['source'] = source

    # Convert the published column to a datetime object
    df['published'] = pd.to_datetime(df['published'])

    # Fix the "- AP news - en español" at the end of the title
    df['title'] = df['title'].str.replace(' - The Associated Press - en Español', '')
    return df

# Transform the sentences
def transform_sentence(df, colname='title'):
    '''
    Description: Takes a data frame as input and produces a data frame of sentence embeddings of the column of interest in proper order.
    Args:
        tweet_df: Data frame that contains at least a column called Tweet, which is the sentence to be transformed.
    Returns: A data frame of sentence embeddings
    '''
    model_name = 'all-mpnet-base-v2'
    model = SentenceTransformer(model_name)
    se = model.encode(df[colname].tolist(), show_progress_bar = True)
    se = pd.DataFrame(se)
    se.columns = se.columns.astype(str)
    return se

# Make a UMAP from the embeddings
def make_umap(se):
    '''
    Description: Takes in a data frame of sentence embeddings and performs dimension reduction on it. 
    This reduces the dimensionality to 2. 
    Args:
        se: Data frame of sentence embeddings
    Returns: A data frame of the 2-dimensional UMAP
    '''
    dimr = umap.UMAP(densmap=True, random_state=42).fit_transform(se)
    dimr = pd.DataFrame(dimr, columns = ['umap1', 'umap2'])
    return dimr


def main():
    # Convert the RSS feeds to a single data frame
    ap_df = rss_to_df(ap, 'AP News')
    bb_df = rss_to_df(bb, 'Bloomberg')
    hn_df = rss_to_df(hn, 'Hacker News')
    lw_df = rss_to_df(lw, 'Less Wrong')
    df = ap_df.append(bb_df)
    df = df.append(hn_df)
    df = df.append(lw_df)
    df = df.reset_index(drop=True)

    # Process the data
    se = transform_sentence(df)
    dimr = make_umap(se)
    df = pd.concat([df, dimr], axis=1) # We might add back in the embeddings later
    df.to_csv('data/rss.csv', index=False)
    print(df['published'])

if __name__ == '__main__':
    main()




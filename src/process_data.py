
import pandas as pd
from sentence_transformers import SentenceTransformer
import umap
from transformers import pipeline

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

# Get sentiment analysis from the titles
def get_sentiment(df, colname='title'):
    '''
    Description: Takes in a data frame and performs sentiment analysis on the column of interest. 
    Args:
        df: Data frame
        colname: Column name of interest
    Returns: A data frame of the sentiment analysis
    '''
    # Sentiment analysis
    #tokenizer = AutoTokenizer.from_pretrained("cardiffnlp/twitter-roberta-base-sentiment-latest")
    #model_path = AutoModelForSequenceClassification.from_pretrained("cardiffnlp/twitter-roberta-base-sentiment-latest")
    model_path = "cardiffnlp/twitter-roberta-base-sentiment-latest"
    sentiment_task = pipeline("sentiment-analysis", model=model_path, tokenizer=model_path)

    # Same but for the tweets in the df
    # Sentiment is time consuming.
    count = 0
    sentiment_label = []
    # sentiment_score = []

    for i in df[colname]:
        count += 1
        if count % 1000 == 0:
            print(str(count) + ' tweets processed for senteiment')
        sentiment_label.append(sentiment_task(i)[0]['label'])
        # sentiment_score.append(sentiment_task(i)[0]['score'])

    # df['sentiment_label'] = sentiment_label
    # df['sentiment_score'] = sentiment_score
    return sentiment_label


def main():
    # Convert the RSS feeds to a single data frame
    # Import data
    df = pd.read_csv('output/opml_output.csv')
    print(df)

    # Process the data
    df['sentiment'] = get_sentiment(df)
    se = transform_sentence(df)
    dimr = make_umap(se)
    df = pd.concat([df, dimr], axis=1) # We might add back in the embeddings later
    df.to_csv('data/rss.csv', index=False)
    print(df['published'])

if __name__ == '__main__':
    main()

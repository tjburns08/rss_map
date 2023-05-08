import feedparser
import pandas as pd
import xml.etree.ElementTree as ET

def parse_opml(file_path):
    tree = ET.parse(file_path)
    root = tree.getroot()
    feeds = []
    for elem in root.iter('outline'):
        url = elem.get('xmlUrl')
        elem_type = elem.get('type')
        text = elem.get('text')
        if url and elem_type == "rss":
            feeds.append((url, text))
    return feeds

def rss_reader(feed_url, feed_text):
    feed = feedparser.parse(feed_url)
    feed_entries = []

    for entry in feed.entries:
        feed_entries.append({
            'source': feed_text,
            'title': entry.title,
            'summary': entry.summary,
            'link': entry.link,
            'published': entry.published
        })

    return feed_entries

if __name__ == "__main__":
    opml_file = "data/rss-subscriptions.opml"
    output_csv = "output/opml_output.csv"
    
    feeds = parse_opml(opml_file)

    all_feed_entries = []

    for feed_url, feed_text in feeds:
        try:
            all_feed_entries.extend(rss_reader(feed_url, feed_text))
        except Exception as e:
            print(f"Error processing feed URL: {feed_url}. Error: {e}")

    df = pd.DataFrame(all_feed_entries)
    df.to_csv(output_csv, index=False)

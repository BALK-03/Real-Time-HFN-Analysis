import json
import os
import sys
from typing import List

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__),'..', '..')))
from src.reddit.reddit_scraper import RedditScraper
from src.utils.get_config import get_config


def fetch_and_append_reddit_data(filename: str, num_rows: int, subreddits: List[str]):
    scraper = RedditScraper()
    
    count = 0
    last_posts = {subreddit: None for subreddit in subreddits}
    
    with open(filename, mode='a', encoding='utf-8') as file:
        while count < num_rows:
            for subreddit_name in subreddits:
                if count >= num_rows:
                    break
                
                subreddit = scraper.reddit_client.subreddit(subreddit_name)
                result = scraper.fetch_posts(subreddit, num_posts=1, last_post=last_posts[subreddit_name])
                
                if result is None:
                    continue
                
                post_data, last_posts[subreddit_name] = result

                if len(post_data["post_body"]) == 0:
                    continue
                
                post_record = {
                    "text": post_data["post_body"],
                    "subreddit": subreddit_name,
                    "is_post": 1    # 1 because its a post
                }
                file.write(json.dumps(post_record, ensure_ascii=False) + "\n")
                count += 1
                
                post = scraper.reddit_client.submission(id=post_data["post_id"])
                comments = scraper.fetch_comments(post, num_comments=4)
                for comment in comments:
                    comment_record = {
                        "text": comment,
                        "subreddit": subreddit_name,
                        "is_post": 0    # 0 because its not a post, its a comment
                    }
                    file.write(json.dumps(comment_record, ensure_ascii=False) + "\n")
                    count += 1


if __name__ == "__main__":
    filename = "./src/storage/bert_unlabeled_data.jsonl"
    config_file = "./config/reddit_config.yml"
    subreddits = get_config(config_file=config_file, target_config="subreddits")
    fetch_and_append_reddit_data(filename=filename, num_rows=100, subreddits=subreddits)

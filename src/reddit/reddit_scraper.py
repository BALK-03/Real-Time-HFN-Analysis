import os, sys
import praw
from typing import Optional, Dict
from dotenv import load_dotenv


sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from src.utils.logger import get_logger
from src.utils.get_config import get_config


class RedditScraper:
    CONFIG_FILE = "./config/reddit_config.yml"
    ENV_FILE = "./config/.env"

    def __init__(self):
        self.logger = get_logger(__name__)
        self.reddit_client = self.reddit_authentication()
        self.logger.info(f"Authenticated succefully!")
        self.subreddits = get_config(config_file=RedditScraper.CONFIG_FILE, target_config='subreddits')

    def reddit_authentication(self) -> praw.Reddit:
        try:
            load_dotenv(RedditScraper.ENV_FILE)
            return praw.Reddit(
                username=os.getenv('REDDIT_USERNAME'),
                password=os.getenv('REDDIT_PASSWORD'),
                client_id=os.getenv('REDDIT_CLIENT_ID'),
                client_secret=os.getenv('REDDIT_CLIENT_SECRET'),
                user_agent=os.getenv('REDDIT_USER_AGENT')
            )
        except KeyError as e:
            self.logger.error(f"Missing configuration key: {e}")
            raise
        except Exception as e:
            self.logger.error(f"Reddit authentication failed: {e}")
            raise

    def fetch_posts(self, subreddit, num_posts=1, last_post=None) -> Optional[tuple[Dict[str, str], str]]:
        try:
            posts = list(subreddit.hot(limit=num_posts, params={'after': last_post}))
            # If no more available posts to fetch
            if not posts:
                return
            for post in posts:
                post_data = {
                    "post_id": post.id,
                    "post_title": post.title,
                    "post_url": post.url,
                    "created_utc": post.created_utc,
                    "post_body": post.selftext
                }
                self.logger.info(f"post {post} fetched!")

                last_post = post.name
            return post_data, last_post
        except Exception as e:
            self.logger.error(f"Problem occured while fetching posts: {e}")
            return

    def fetch_comments(self, post, num_comments = 30) -> Optional[list[str]]:
        try:
            post.comment_sort = "top"
            post.comments.replace_more(limit=0)

            # A set to ensure no duplicates
            comments_set = {comment.body for comment in post.comments[:num_comments]}
            return list(comments_set)
        except Exception as e:
            self.logger.error(f"Problem occured while fetching comments: {e}")
            return
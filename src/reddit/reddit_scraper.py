import os, sys
import praw
import yaml
from typing import Optional, Dict, List
from dotenv import DotEnv

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from src.utils.logger import get_logger


class RedditScraper:
    CONFIG_FILE = "./config/reddit_config.yml"

    def __init__(self):
        self.logger = get_logger(__name__)
        self.reddit_client = self.reddit_authentication()
        self.logger.info(f"Authenticated succefully!")
        self.subreddits = self.get_subreddits(reddit_config=RedditScraper.CONFIG_FILE)

    def get_subreddits(self, reddit_config) -> List[str]:
        try:
            with open(reddit_config, 'r')  as file:
                config = yaml.safe_load(file)
            subreddits = config.get('subreddits')
            return subreddits
        except Exception as e:
            self.logger.error(f"Probelm occured while reading from {reddit_config} file: {e}")
            raise

    def reddit_authentication(self) -> praw.Reddit:
        try:
            DotEnv('.env')
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
            # No more available posts to fetch
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

    def fetch_comments(self, post, num_comments = 30) -> Optional[list[str]]:   # -> tuple[dict[str, str], str]
        try:
            post.comment_sort = "top"
            post.comments.replace_more(limit=0)

            # A set to ensure no duplicates
            comments_set = {comment.body for comment in post.comments[:num_comments]}
            return list(comments_set)
        except Exception as e:
            self.logger.error(f"Problem occured while fetching comments: {e}")
            return
from collections import defaultdict

from src.utils.logger import get_logger
from src.reddit.reddit_scraper import RedditScraper
from src.kafka.producer import Producer


def main():
    logger = get_logger(__name__)

    scraper = RedditScraper()

    subreddits = scraper.subreddits
    reddit_client = scraper.reddit_client

    producer = Producer(bootstrap_servers='localhost:9092')
    
    last_post_info = defaultdict(lambda: None)
    idx = 0
    while True:
        try:
            subreddit = subreddits[idx]
            subreddit = reddit_client.subreddit(subreddit)

            post_data, after_post = scraper.fetch_posts(
                subreddit = subreddit,
                num_posts = 1,
                last_post = last_post_info[subreddit]
            )

            if not post_data:
                idx = (idx +1) % len(subreddits)
                continue
            else:                
                post = reddit_client.submission(post_data["post_id"])

                comments_data = scraper.fetch_comments(
                    post = post,
                    num_comments = 20
                )
                
                post_data["comments"] = comments_data

                is_produced = producer.publish_to_kafka(data=post_data, topic="RedditData")
                if not is_produced:
                    logger.warning(f"Unpublished data, post: {post}. Check kafka setup!")

                last_post_info[subreddit] = after_post
                idx = (idx +1) % len(subreddits)
        except Exception as e:
            logger.error(f"Problem occured while fetching or publishing data from subreddit {subreddit}: {e}")
            idx = (idx +1) % len(subreddits)
            continue


if __name__ == "__main__":
    main()
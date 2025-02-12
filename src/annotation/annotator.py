def append_to_csv(filename, data_dict):
    """
    Append a row of data to a CSV file. If the file does not exist, create it and write the header first.

    Parameters:
        filename (str): The name of the CSV file.
        data_dict (dict): A dictionary where keys are column names and values are their respective data.
    """
    file_exists = os.path.isfile(filename)
    header = list(data_dict.keys())
    data = list(data_dict.values())

    with open(filename, 'a', newline='') as csvfile:
        writer = csv.writer(csvfile)

        if not file_exists:
            writer.writerow(header)

        writer.writerow(data)
    # print("Data appended to CSV file.")



if __name__ == "__main__":
    import os, sys
    import csv
    from collections import defaultdict

    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
    from src.reddit.reddit_scraper import RedditScraper
    from src.utils.logger import get_logger
    from src.annotation.prompt_llm import PromptLLM

    logger = get_logger(__name__)
    FILE_PATH = "./src/annotation/storage/bert_finetune_sentiment.csv"

    scraper = RedditScraper()
    annotator = PromptLLM()

    subreddits = scraper.subreddits
    reddit_client = scraper.reddit_client
    
    last_post_info = defaultdict(lambda: None)
    idx = 0
    for i in range(1, 101):
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
                annotated_post = annotator.annotate_post(
                    post_text=post_data["post_body"]
                )
                append_to_csv(
                    filename=FILE_PATH,
                    data_dict={**annotated_post, "subreddit": subreddit}
                )

                post = reddit_client.submission(post_data["post_id"])

                comments_data = scraper.fetch_comments(
                    post = post,
                    num_comments = 29
                )
                for comment in comments_data:
                    if not comment:
                        continue

                    annotated_comment = annotator.annotate_comment(
                        post_text=post_data["post_body"],
                        comment_text=comment
                    )
                    append_to_csv(
                        filename=FILE_PATH,
                        data_dict={**annotated_comment, "subreddit": subreddit}
                    )
                last_post_info[subreddit] = after_post
                idx = (idx +1) % len(subreddits)
        except Exception as e:
            logger.warning(f"Problem occured while storing data from subreddit {subreddit}: {e}")
            idx = (idx +1) % len(subreddits)
            continue
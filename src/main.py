import os
import logging

import praw


logging.basicConfig(format='%(asctime)s %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)


def main():
    """Main"""
    reddit = praw.Reddit(
        client_id=os.getenv('CLIENT_ID'),
        client_secret=os.getenv('CLIENT_SECRET'),
        user_agent='linux:SanDiegoLibreBot:v1.0 (by u/mitch_feaster)',
        username=os.getenv('REDDIT_USERNAME'),
        password=os.getenv('REDDIT_PASSWORD'),
    )

    subs = ["SanDiegoLibreTest"]
    logger.info(f"Listening for new posts to {', '.join(subs)}")
    for submission in reddit.subreddit('+'.join(subs)).stream.submissions():
        msg = f"[Crosspost] {submission.subreddit_name_prefixed} u/{submission.author.name} - {submission.title}"
        logger.info(msg)
        submission.crosspost(subreddit="SanDiegoLibre")


if __name__ == "__main__":
    main()

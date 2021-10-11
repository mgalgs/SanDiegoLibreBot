import os
import time
import logging
import pathlib

import praw


logging.basicConfig(format='%(asctime)s %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

IS_PROD = os.getenv("PROD") == "yes"


class SeenDB:
    def __init__(self, db_path):
        self._db_path = db_path
        if not os.path.exists(self._db_path):
            pathlib.Path(self._db_path).touch()
        with open(self._db_path, 'r') as f:
            self._seen = set([l.strip() for l in f.readlines()])

    def add(self, fullname):
        self._seen.add(fullname)
        with open(self._db_path, 'a') as f:
            f.write(f"{fullname}\n")

    def have(self, fullname):
        return fullname in self._seen


def main():
    """Main - duh!"""
    reddit = praw.Reddit(
        client_id=os.getenv('CLIENT_ID'),
        client_secret=os.getenv('CLIENT_SECRET'),
        user_agent='linux:SanDiegoLibreBot:v1.0 (by u/mitch_feaster)',
        username=os.getenv('REDDIT_USERNAME'),
        password=os.getenv('REDDIT_PASSWORD'),
    )

    subs = ["SanDiego", "SanDiegan"]
    target_sub = "SanDiegoLibre" if IS_PROD else "SanDiegoLibreTest"
    dbpath = pathlib.Path(__file__).parent.resolve() / 'seen.txt'
    seendb = SeenDB(dbpath)
    fifteen_minutes = 60 * 15

    # Grab the .hot() posts each hour and cross-post them at 15 minute
    # intervals. The 15 minute interval crap is due to rate-limiting and
    # can hopefully be tuned more aggressively in the future.
    while True:
        nposted = 0
        # grabbing 20 (instead of 4, which is the most we can post each
        # hour) since we'll be skipping posts that have already been seen.
        hot_posts = reddit.subreddit('+'.join(subs)).hot(limit=20)
        for post in hot_posts:
            if not IS_PROD:
                # test sub can't accept video uploads
                if reddit.submission(post.fullname.split('_')[1]).is_video:
                    logger.warning(f"Skipping {post.fullname} since our test sub can't take vids")
                    continue
            already_seen = seendb.have(post.fullname)
            action = "SKIP" if already_seen else "X-POST"
            msg = f"[{action}] {post.subreddit_name_prefixed} u/{post.author.name} - {post.permalink}"
            logger.info(msg)
            if not already_seen:
                try:
                    post.crosspost(subreddit=target_sub)
                except praw.exceptions.RedditAPIException as e:
                    logger.error(f"Failed to post {post.fullname}: {e}")
                    continue
                finally:
                    seendb.add(post.fullname)
                nposted += 1
                time.sleep(fifteen_minutes)
            if nposted == 4:
                break
        # Make sure we sleep through all 4 fifteen minute post slots if we
        # didn't use all 4 slots above.
        moresleep = (4 - nposted) * fifteen_minutes
        if moresleep > 0:
            logger.info(f"Need to sleep for {moresleep} more seconds because we cruised through everything")
            time.sleep(moresleep)


if __name__ == "__main__":
    main()

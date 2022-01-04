import os
import sys
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


def get_db_path():
    storage_dir = os.getenv('STORAGE_DIR')
    if storage_dir is not None:
        dbdir = pathlib.Path(storage_dir)
        if not dbdir.exists():
            logger.error("Storage directory does not exist: %s", storage_dir)
            sys.exit(1)
    else:
        dbdir = pathlib.Path(__file__).parent.resolve()
    return dbdir / 'seen.txt'


class Poster:
    def __init__(self):
        self.reddit = praw.Reddit(
            client_id=os.getenv('CLIENT_ID'),
            client_secret=os.getenv('CLIENT_SECRET'),
            user_agent='linux:SanDiegoLibreBot:v1.0 (by u/mitch_feaster)',
            username=os.getenv('REDDIT_USERNAME'),
            password=os.getenv('REDDIT_PASSWORD'),
        )

        self.subs = ["SanDiego", "SanDiegan"]
        self.target_sub = "SanDiegoLibre" if IS_PROD else "SanDiegoLibreTest"
        dbpath = get_db_path()
        logger.info("Using database at %s", dbpath)
        self.seendb = SeenDB(dbpath)

    def post_some(self, num_to_post):
        logger.info(f"Num to post: {num_to_post}")
        if num_to_post < 1:
            return
        hot_posts = self.reddit.subreddit('+'.join(self.subs)).hot(limit=20)
        nposted = 0
        for post in hot_posts:
            if not IS_PROD:
                # test sub can't accept video uploads
                if self.reddit.submission(post.fullname.split('_')[1]).is_video:
                    logger.warning(f"Skipping {post.fullname} since our test sub can't take vids")
                    continue
            already_seen = self.seendb.have(post.fullname)
            action = "SKIP" if already_seen else "X-POST"
            msg = f"[{action}] {post.subreddit_name_prefixed} u/{post.author.name} - {post.permalink}"
            logger.info(msg)
            if not already_seen:
                try:
                    post.crosspost(subreddit=self.target_sub)
                    nposted += 1
                    if nposted == num_to_post:
                        break
                except praw.exceptions.RedditAPIException as e:
                    logger.error(f"Failed to post {post.fullname}: {e}")
                    continue
                finally:
                    self.seendb.add(post.fullname)


def usage():
    print(f"Usage: {os.path.basename(sys.argv[0])} num-to-post")


def main():
    if len(sys.argv) != 2:
        usage()
        sys.exit(1)

    try:
        num_to_post = int(sys.argv[1])
    except ValueError:
        usage()
        sys.exit(1)
    Poster().post_some(num_to_post)


if __name__ == "__main__":
    main()

import time
import json
import os
import praw
from psaw import PushshiftAPI

CFG_FILENAME = "config.json"


def main():
	cwd = os.getcwd()
	cfg_file = open(cwd + "/" + CFG_FILENAME)
	cfg_settings = json.loads(cfg_file.read())
	cfg_file.close()

	reddit = praw.Reddit(user_agent=cfg_settings["user_agent"],
						 client_id=cfg_settings["client_id"],
						 client_secret=cfg_settings["client_secret"],
						 username=cfg_settings["username"],
						 password=cfg_settings["password"])
	api = PushshiftAPI(reddit)

	while True:
		gen = api.search_comments(q="oh no", limit=10_000)
		try:
			for comment in gen:
				try:
					if comment.body.lower() != "oh no":
						continue

					if comment.submission.locked:
						continue

					comment.refresh()
					if comment.parent().author == reddit.config.username:
						continue

					skip = False
					for reply in comment.replies:
						if reply.author == reddit.config.username:
							skip = True
							break

					if skip:
						continue

					comment.reply("# **OH YEAH!**")

					print_header('-', get_formatted_gmt_time() + '\nUser:\n' + comment.author.name)
				# time.sleep(1)
				except Exception as e:
					handle_error(e)

			print_header('*', "Reached end of iterable, retrying shortly.")

		except Exception as e:
			handle_error(e)


# time.sleep(3)

def handle_error(e):
	print_error(e)
	if type(e) == praw.exceptions.RedditAPIException:
		for subexception in e.items:
			if "RATELIMIT" in subexception.error_message:
				print_header('*', "Sleeping for 15 minutes to comply with rate limit")
				time.sleep(900)
				break


def print_error(error):
	print('#' * 80)
	print('#' * 80)
	print(get_formatted_gmt_time())
	print(f"An error of type {type(error)} was raised:")
	print(vars(error))
	print('-' * 80)


def print_header(char, text):
	print(char * 80)
	print(text)
	print(char * 80)


def get_formatted_gmt_time():
	return time.strftime("%Y-%m-%d %H:%M:%S GMT", time.gmtime())


if __name__ == "__main__":
	main()

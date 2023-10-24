import collections
import calendar
import requests
import json

API_TOKEN = "XXXXXXX"

REPO = "kiteco/kiteco"


def get(url):
	r = requests.get(
		f"https://api.github.com{url}",
		headers={"Authorization": f"token {API_TOKEN}"},
	)
	msg = r.json()
	if r.status_code != 200:
		raise Exception(f"""Failed to get {url}: github said '{msg["message"]}'""")
	return msg


def patch(url, payload):
	r = requests.patch(
		f"https://api.github.com{url}",
		headers={"Authorization": f"token {API_TOKEN}"},
		data=json.dumps(payload),
	)
	msg = r.json()
	if r.status_code != 200:
		raise Exception(f"""Failed to patch {url}: github said '{msg["message"]}'""")
	return msg


def put(url, payload):
	r = requests.put(
		f"https://api.github.com{url}",
		headers={"Authorization": f"token {API_TOKEN}"},
		data=json.dumps(payload),
	)
	msg = r.json()
	if r.status_code != 200:
		raise Exception(f"""Failed to put {url}: github said '{msg["message"]}'""")
	return msg


def fetch_prs():
	return get(f"/repos/{REPO}/pulls")


def prs_for(username, prs):
	usertag = f"@{username}"
	for pr in prs:
		role = None
		if pr["state"] == "open" and usertag in pr["body"]:
			role = "a reviewer"
		elif pr["user"]["login"] == username:
			role = "the author"

		if role is not None:
			yield role, pr


def fetch_comments(pr_number):
	# first get the pr-level comments, which are comments on specific lines of code
	pr_comments = get("/repos/%s/pulls/%d/comments" % (REPO, pr_number))
	# next get the issue-level comments, which are not tied to any line of code
	issue_comments = get("/repos/%s/issues/%d/comments" % (REPO, pr_number))
	# now combine them and sort by timestamp
	return sorted(pr_comments + issue_comments, key=lambda c: c["created_at"])

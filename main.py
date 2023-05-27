import os
import re
import sys
import base64
import requests
from github import Github, GithubException
from datetime import datetime

STARTS_WITH = '<!--QOTD_STARTS_HERE-->'
ENDS_WITH = '<!--QOTD_ENDS_HERE-->'
REPL_PATTERN = f'{STARTS_WITH}[\\s\\S]+{ENDS_WITH}'

REPO = os.getenv('INPUT_REPO')
TOKEN = os.getenv('INPUT_TOKEN')

def decode_readme(data: str) -> str:
  decoded_bytes = base64.b64decode(data)
  return str(decoded_bytes, 'utf-8')

def generate_new_readme(readme: str, quote: str) -> str:
  update_readme_with = f'{STARTS_WITH}\n{quote}\n{ENDS_WITH}'
  return re.sub(REPL_PATTERN, update_readme_with, readme)

def get_qotd() -> str:
  date_str = datetime.now().strftime('%A, %B %d, %Y')
  quote_str = f'<blockquote>&ldquo;Today I failed, but tomorrow I will try again. Failure is not the end of the road, but a chance to learn and grow.&rdquo; &mdash; <footer>{date_str}</footer></blockquote>'
  response = requests.get('https://zenquotes.io/api/today')
  if response.status_code == 200:
    if response.json()[0]['a'] != 'zenquotes.io':
      quote_str = response.json()[0]['h']
  return quote_str

if __name__ == '__main__':

  g = Github(TOKEN)

  try:
    readme_repo = g.get_repo(REPO)
  except GithubException:
    print('Authentication Error!')
    sys.exit(1)
  
  readme_obj = readme_repo.get_readme()
  readme_content = readme_obj.content
  readme_content_decoded = decode_readme(readme_content)

  qotd = get_qotd()

  new_readme = generate_new_readme(readme=readme_content_decoded, quote=qotd)

  readme_repo.update_file(path=readme_obj.path, message='Update quote of the day', content=new_readme, sha=readme_obj.sha)

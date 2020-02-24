import json, os, re, dateutil.parser
from nltk.tokenize import word_tokenize
import string
from nltk.corpus import stopwords
import nltk
import markdown2
from bs4 import BeautifulSoup

nltk.download('punkt')
nltk.download('stopwords')

repos = ['react', 'angular', 'vue', 'backbone', 'ember.js', 'jquery']
fields = ['title', 'body', 'num', 'd']

for repo in repos:
  with open('%s_issues_dirty.json' % repo, 'r') as dirty:
    issues = json.loads(dirty.read())
    for issue in issues:
      num = None
      d = None
      for field in list(issue.keys()):
        if field == 'url':
          search = re.search('(\d+)', issue['url'])
          num = search.group(0)
        if field == 'created_at':
          date = dateutil.parser.parse(issue['created_at'])
          d = '{}/{}'.format(date.month, date.year)
        if (field == 'title' or field == 'body'):
          text = markdown2.markdown(issue[field]) if issue[field] is not None else ''
          soup = BeautifulSoup(text, 'html.parser')
          for tag in soup.find_all('code'):
            tag.replaceWith('')
          text = markdown2.markdown(soup.get_text())
          text = re.sub('<[^<]+?>', '', text)
          text = re.sub(r"http\S+", "", text)
          tokens = word_tokenize(text)
          tokens = [w.lower() for w in tokens]
          table = str.maketrans('', '', string.punctuation)
          stripped = [w.translate(table) for w in tokens]
          words = [word for word in stripped if word.isalpha()]
          stop_words = set(stopwords.words('english'))
          words = [w for w in words if not w in stop_words]
          issue[field] = ' '.join(words)
        if field not in fields:
          del issue[field]
      if num is not None:
        issue['num'] = num
      if d is not None:
        issue['d'] = d
  with open('%s_issues_clean.json' % repo, 'w+') as clean:
    json.dump(issues, clean)
  os.remove('%s_issues_dirty.json' % repo)
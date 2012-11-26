from django.core.cache import get_cache
import random, string
import urlparse, urllib

def random_string(length=50, chars=None):
    chars = chars if chars else string.ascii_lowercase
    return ''.join(random.choice(chars) for x in range(length))

def add_query_param(url, name, value):
    """
    Add the query param name=value to the url string and return a new url string.

    >>> add_query_param('http://www.nyt.com/?last=Smith#bar', 'name', 'John')
    'http://www.nyt.com/?last=Smith&name=John#bar'
    """
    o = urlparse.urlparse(url)
    qs = urlparse.parse_qs(o.query)
    qs[name] = [value]
    o2 = urlparse.ParseResult(o.scheme, o.netloc, o.path, o.params,
                              urllib.urlencode(qs, doseq=True),
                              o.fragment)
    return o2.geturl()

def add_token(url, expiry=10):
    token = random_string()
    get_cache('shared').set(token, url, expiry)
    return add_query_param(url, 'url_token', token)

def check_token(token, url):
    url2 = get_cache('shared').get(token)
    return (token and url==urllib.unquote(url2))

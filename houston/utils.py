import re

def extract_onclick(onclick, base_url):
    before = re.escape("javascript:ViewHTML=window.open('")
    after = re.escape("','ViewHTML")
    token_re = "{}(.*){}".format(before, after)
    result = re.search(token_re, onclick)
    url = result.group(1)

    if not url.startswith('http'):
        url = '{}{}'.format(base_url, url)

    return url


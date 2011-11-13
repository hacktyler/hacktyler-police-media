#!/usr/bin/env python

import os.path
import re
import sys
import time

import requests

SEARCH_ROOT_URL = 'http://www.tylerpolice.com/PIR/user/DoSearch.aspx'
MOST_RECENT_URL = 'http://www.tylerpolice.com/PIR/user/SearchResults.aspx?searchType=1'
MEDIA_REPORT_URL = 'http://www.tylerpolice.com/PIR/user/ViewReport.aspx?id=%s'
REPORT_URL_REGEX = re.compile('ViewReport\.aspx\?id=([\d]{9})')

root = requests.get(SEARCH_ROOT_URL)

if root.status_code != 200:
    sys.exit('Root request failed.')

session_cookies = root.cookies

recent = requests.get(MOST_RECENT_URL, cookies=session_cookies)

if recent.status_code != 200:
    sys.exit('Recent request failed.')

recent_urls = REPORT_URL_REGEX.search(recent.content)
newest_id = recent_urls.group(1)

year = int(newest_id[:2])
report_id = int(newest_id[2:])

while report_id >= 0:
    next_id = '%i%07i' % (year, report_id)

    if os.path.exists('page_cache/%s.html' % next_id):
        report_id -= 1
        continue

    if os.path.exists('page_cache/%s.skip' % next_id):
        report_id -= 1
        continue

    print 'Fetching report %s' % next_id
    report = requests.get(MEDIA_REPORT_URL % next_id, cookies=session_cookies)

    if report.status_code != 200:
        print 'Request failed'
        continue

    if report.url == MEDIA_REPORT_URL % next_id:
        print 'Saving report'

        with open('page_cache/%s.html' % next_id, 'w') as f:
            f.write(report.content)
    elif report.url == SEARCH_ROOT_URL:
        print 'No report'

        with open('page_cache/%s.skip' % next_id, 'w') as f:
            f.write('NO REPORT')

    report_id -= 1
    time.sleep(1)

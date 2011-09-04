#!/usr/bin/env python

import os
import sqlite3

from lxml import html
from dateutil import parser

sql = sqlite3.connect('scrape.sqlite')
sql.execute("""
    create table if not exists reports (
        case_number integer primary key,
        call_title text,
        date_of_incident text,
        day_of_week text,
        incident_location text,
        reporting_officer text,
        date_reported text,
        case_status text,
        location_type text)
    """)

def parse_report(report_id, f):
    parsed = html.parse(f)

    root = parsed.getroot()

    body = root.xpath('//div[contains(@style,\'800px\')]')[0]
    #body.xpath('comment()')[0]
    incident_table = body.xpath('//table')[0]
    rows = incident_table.xpath('tr')

    data = []
    
    for row in rows:
        cells = row.xpath('td')
        assert len(cells) == 2

        value = unicode(cells[1].text_content())

        if len(data) == 0:
            value = report_id

        if len(data) == 2 or len(data) == 6:
            dt = parser.parse(value) 
            value = dt.isoformat()
    
        data.append(value)

    sql.execute('insert into reports values (?, ?, ?, ?, ?, ?, ?, ?, ?)', data)
    sql.commit()

for filename in os.listdir('page_cache'):
    if filename[-4:] == 'skip':
        continue

    report_id = filename[:-5]
    parse_report(report_id, open('page_cache/%s' % filename, 'r'))

sql.close()

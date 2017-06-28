# evccScheduleParser takes downloaded html pages from https://www.everettcc.edu/classes/index.cfm?list=B782&dept=ALL&open=on&st=bas
# and extracts the course info.
# course html page must be in the scripts relative file Path.
# -Perquisites are not collected since not all of the courses have perquisites in the html
# - Web scraping was attempted but I gave up since I couldn't get past the robots.txt

from lxml import html as a
import numpy as np

def print_row(row):
    for i in row:
        print a.tostring(i)
        break
    print "-------------------"

#
page = file("Summer_Class Schedule __ EvCC.html")

tree = a.fromstring(page.read())

page.close()

course_title = tree.xpath('//*[contains(@id,"div")]/td/table/tr/td/h3/text()')
desc = tree.xpath('//*[contains(@id,"div")]/td/table/tr/td/p[1]')

# filter out empty descriptions
desc_result = []
desc = [desc_result.append(x.text) if x.text else '' for x in desc ]

section = tree.xpath('//*[contains(@id,"div")]/td/table/tr/td/table/tr[2]/td[2]/text()[normalize-space(.) != .]')

credits = tree.xpath('//*[contains(@id,"div")]/td/table/tr/td/table/tr[2]/td[3]/text()')

capacity = tree.xpath('//*[contains(@id,"div")]/td/table/tr/td/table/tr[4]/td[1]/text()')


enrolled = tree.xpath('//*[contains(@id,"div")]/td/table/tr/td/table/tr[4]/td[2]/text()')

start_end_time = tree.xpath('//*[contains(@id,"div")]/td/table/tr/td/table/tr[6]/td[1]/text()')

days = tree.xpath('//*[contains(@id,"div")]/td/table/tr/td/table/tr[6]/td[2]')

# remove empty days
days = [x.text if x.text else '' for x in days]

location = tree.xpath('//*[contains(@id,"div")]/td/table/tr/td/table/tr[6]/td[3]/text()')
table = [course_title,desc_result,section,credits,capacity,enrolled,start_end_time,days,location]

schedule = np.empty((len(section),len(table)),dtype=object)
for i in range(len(table)):
    schedule[:,i] = table[i]
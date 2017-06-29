# evccScheduleParser takes downloaded html pages from https://www.everettcc.edu/classes/index.cfm?list=B782&dept=ALL&open=on&st=bas
# and extracts the course info.
# course html page must be in the scripts relative file Path.
# -Perquisites are not collected since not all of the courses have perquisites in the html
# - Web scraping was attempted but I gave up since I couldn't get past the robots.txt

from lxml import html as a
import numpy as np
import xlwt

def print_row(row):
    for i in row:
        print a.tostring(i)
        break
    print "-------------------"

def create_exel(quarters, schedule):
    wb = xlwt.Workbook()
    for curr_quarter in range(len(quarters)):
        ws = wb.add_sheet(quarters[curr_quarter] + " Schedule",cell_overwrite_ok=True)
        labels = ["Course", "Desc", "Section", "Credits", "Capacity", "Enrolled", "Time","Day","Location"]
        for curr_label in range(len(labels)):
            ws.write(0,curr_label, labels[curr_label],style=xlwt.Style.easyxf(strg_to_parse="font: bold on;"))

        for i in range(np.size(schedule[curr_quarter],0)):
            for j in range(np.size(schedule[curr_quarter],1)):

                # scheduleschedule[curr_quarter][i,j] is used instead of schedule[curr_quarter,i,j] because
                # schedule is a 2d java array of 2d numpy arrays
                ws.write(1+i,j, schedule[curr_quarter][i,j])
    wb.save("test.xls")


def create_schedule(target_qrt):
    page = file(target_qrt + "_Class Schedule_EvCC.html")

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
    return schedule

if __name__ == "__main__":
    #
    quarters = ["Summer", "Fall", "Spring"]
    schedules = []
    for i in quarters:
        schedules.append(create_schedule(i))

    create_exel(quarters, schedules)



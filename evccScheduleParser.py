# evccScheduleParser takes downloaded html pages from https://www.everettcc.edu/classes/index.cfm?list=B782&dept=ALL&open=on&st=bas
# and extracts the course info.
# course html page must be in the scripts relative file Path.
# -Perquisites are not collected since not all of the courses have perquisites in the html
# - Web scraping was attempted but I gave up since I couldn't get past the robots.txt

from lxml import html as a
import numpy as np
import xlwt
import csv
def print_row(row):
    for i in row:
        print a.tostring(i)
        break
    print "-------------------"


def create_cvs(quarter, schedule):
   # wb = xlwt.Workbook()
   #  for curr_quarter in range(len(quarters)):
   #      ws = wb.add_sheet(quarters[curr_quarter] + " Schedule",cell_overwrite_ok=True)
   #      labels = ["Course", "Desc", "Section", "Credits", "Start Time","End Time","Day","Location"]
   #      for curr_label in range(len(labels)):
   #          ws.write(0,curr_label, labels[curr_label],style=xlwt.Style.easyxf(strg_to_parse="font: bold on;"))
   #
   #      for i in range(np.size(schedule[curr_quarter],0)):
   #          print str(i) +"/ " + str(np.size(schedule[curr_quarter],0))
   #
   #          for j in range(np.size(schedule[curr_quarter],1)):
   #              ws.write(1+i,j, schedule[curr_quarter][i][j])
   #  wb.save("test.xls")

  # source for use of zip function with dictionary init:
  # https://stackoverflow.com/questions/209840/map-two-lists-into-a-dictionary-in-python

    # encode all unicode characters into ascii in the description
   for i in schedule:
           i[4] =  i[4].encode('ascii', 'ignore')

   with open(quarter+".csv", 'w') as csvfile:
        fieldnames = ["CourseNumber","Title","MinCredit", "MaxCredit","Description" , "StartTimeID", "EndTimeID","DayID","QuarterID","Year","Status"];
        writer = csv.DictWriter(csvfile,fieldnames=fieldnames)
        writer.writeheader()
        for i in schedule:
            print i
            writer.writerow(dict(zip(fieldnames,i)))

def convert_to_numerical_time(start, end):
    for i in range(len(start)):
        if start[i] == "":
            continue
        curr_time =start[i]
        curr_time = curr_time.strip()
        time = curr_time[0:-3]
        time_atts_start = time.split(":")

        am_pm = curr_time[-2:-1]

        if am_pm == "P" and time_atts_start[0] != '12':
            time_atts_start[0] = int(time_atts_start[0]) + 12

        score_hr = int(time_atts_start[0]) *6
        score_min = int(time_atts_start[1]) / 10
        score = score_hr + score_min + 1
        start[i] = score


    for i in range(len(start)):
        if end[i] == "":
            continue
        curr_time = end[i]
        curr_time = curr_time.strip()
        time = curr_time[0:-3]
        time_atts_start = time.split(":")

        am_pm = curr_time[-2:-1]

        if am_pm == "P" and time_atts_start[0] != '12':
            time_atts_start[0] = int(time_atts_start[0]) + 12

        score_hr = int(time_atts_start[0]) * 6
        score_min = int(time_atts_start[1]) / 10
        score = score_hr + score_min + 1
        end[i] = score


def parse_title(titles):
    numbers = []
    titles_r = []

    for i in range(len(titles)):
        core_info = titles[i].split("-")[1].strip()
        core_info = core_info.split(" ")

        numbers.append(core_info[0] + " " + core_info[1])
        titles_r.append(" ".join(core_info[2:len(core_info)]))

    return [numbers,titles_r]
def parse_days_from_string(days):
    "MTWTh"

   # 1 Monday
   # 2 Tuesday
   # 3 Wednesday
   # 4 Thursday
   # 5 Friday
   # 6 Saturday
   # 7 Sunday


    result = []

    for i in range(len(days)):

        a = []
        curr_day = days[i]
        curr_day = curr_day.strip()
        if curr_day == "ARRANGED" or curr_day == "" or curr_day == "DAILY":

            result.append([])
            continue
        for j in range(len(curr_day)):



            if curr_day[j] == "M":
                a.append(1)
            elif curr_day[j] == "W":
                a.append(3)
            elif curr_day[j] == "F":
                a.append(5)
            elif curr_day[j] == "T":

                if(j == len(curr_day) -1):
                    a.append(2)

                elif (curr_day[j+1] == "h"):

                    a.append(4)
                else:
                    a.append(2)
            elif curr_day[j] == "S":

                if (j == len(days) or days[j + 1] != "a"):
                    a.append(7)

                else:
                    a.append(6)
        result.append(a)

    return result

def get_qtr_id(qtr):

    # 1 Fall
    # 2 Winter
    # 3 Spring
    # 4 Summer
    if qtr == "Fall":
        return 1
    elif qtr == "Winter":
        return 2
    elif qtr == "Spring":
        return 3
    else:
        return 4

def create_schedule(target_qrt):
    page = file(target_qrt + "_Class Schedule_EvCC.html")

    tree = a.fromstring(page.read())

    page.close()

    course_title = tree.xpath('//*[contains(@id,"div")]/td/table/tr/td/h3/text()')
    desc = tree.xpath('//*[contains(@id,"div")]/td/table/tr/td/p[1]')

    # filter out empty descriptions

    # Create a list of descriptions containing stripped version of the data read from the p tag. Replace the misformmated
    # "No Description Available" to a stripped representaion.
    desc = [x.text.strip() if "No Description Available" not in x.text else "No Description Available" for x in desc ]

    section = tree.xpath('//*[contains(@id,"div")]/td/table/tr/td/table/tr[2]/td[2]/text()[normalize-space(.) != .]')

    credits = tree.xpath('//*[contains(@id,"div")]/td/table/tr/td/table/tr[2]/td[3]/text()')

    capacity = tree.xpath('//*[contains(@id,"div")]/td/table/tr/td/table/tr[4]/td[1]/text()')

    enrolled = tree.xpath('//*[contains(@id,"div")]/td/table/tr/td/table/tr[4]/td[2]/text()')

    start_end_time = tree.xpath('//*[contains(@id,"div")]/td/table/tr/td/table/tr[6]/td[1]/text()')
    start_time = [x.split("-")[0] if '-' in x  else '' for x in start_end_time]
    end_time = [x.split("-")[1] if '-' in x else '' for x in start_end_time]

    convert_to_numerical_time(start_time, end_time)
    days = tree.xpath('//*[contains(@id,"div")]/td/table/tr/td/table/tr[6]/td[2]')

    # remove empty days
    days = [x.text if x.text else '' for x in days]

    location = tree.xpath('//*[contains(@id,"div")]/td/table/tr/td/table/tr[6]/td[3]/text()')
    #add duplicates per days

    day_list = parse_days_from_string(days)
    #print day_list
    #print course_title
    [course_numbers,course_titles] = parse_title(course_title)
    schedule = []
    for i in range(len(day_list)):
        #print i
        for j in range(len(day_list[i])):
            if len(day_list[i])  != 0:
                #schedule.append([course_title[i],desc_result[i],section[i],credits[i],start_time[i],end_time[i],day_list[i][j],location[i]])
                schedule.append([course_numbers[i],course_titles[i],-1, credits[i], desc[i],start_time[i],end_time[i],day_list[i][j] ,get_qtr_id(target_qrt), -1,-1])

    #for i in range(len(table)):
     #   schedule[:,i] = table[i]


    #schedule = [x * for x in schedule]
    return schedule

if __name__ == "__main__":
    #
    quarters = ["Summer", "Fall", "Spring"]

    for i in range(len(quarters)):
        schedule = create_schedule(quarters[i])
        print "\n" + quarters[i]

        create_cvs(quarters[i], schedule)
    #print schedules


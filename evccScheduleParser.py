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


def create_csv(filename, schedules, fieldnames):
  # source for use of zip function with dictionary init:
  # https://stackoverflow.com/questions/209840/map-two-lists-into-a-dictionary-in-python

    # encode all unicode characters into ascii in the description
    if "Description" in fieldnames:
        for i in range(len(schedules)):
            for j in schedules[i]:
                j[5] = j[5].encode('ascii', 'ignore')

    with open(filename+".csv", 'w') as csvfile:
        writer = csv.DictWriter(csvfile,fieldnames=fieldnames)
        writer.writeheader()
        for i in range(len(schedules)):
            for j in schedules[i]:
                writer.writerow(dict(zip(fieldnames,j)))

# takes start and end arrays of string times and converts them to the time ids 
def convert_to_numerical_time(start, end):

    # convert all the start times
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

    # convert all the end times
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


# split course titles into type and course number
def parse_title(titles):
    numbers = []
    titles_r = []

    for i in range(len(titles)):
        core_info = titles[i].split("-")[1].strip()
        core_info = core_info.split(" ")

        # courses like ENG T 300 have 3 fields
        if len(core_info) == 3:
            numbers.append(core_info[0] + " " + core_info[1] + " " +core_info[2])
            titles_r.append(" ".join(core_info[3:len(core_info)]))
        else:

            numbers.append(core_info[0] + " " + core_info[1])
            titles_r.append(" ".join(core_info[2:len(core_info)]))

    return [numbers,titles_r]

# takes the string of course offerings and converts it into an array of thier ids.
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

        # arranged courses are ignored
        if curr_day == "ARRANGED" or curr_day == "":

            result.append([])
            continue

        # daily courses are offered mon to friday
        if curr_day == "DAILY":
            result.append([1,2,3,4,5]);
            continue;
        for j in range(len(curr_day)):

            if curr_day[j] == "M":
                a.append(1)
            elif curr_day[j] == "W":
                a.append(3)
            elif curr_day[j] == "F":
                a.append(5)

            # check if it is tuesday or thursday
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

# returns the qtr id of the string representation
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

# returns array of array of course and array of course schedulings
#[scheduleCourse,scheduleCourseTime]
# target_qtr is the name of the quarter to read the info from the file
#
# It is assumed that a file with name [target_qrt]_Class Schedule_EvCC.html
# exists
def create_schedule(target_qrt):
    page = file(target_qrt + "_Schedule.html")

    tree = a.fromstring(page.read())

    page.close()

    course_title = tree.xpath('//*[contains(@id,"div")]/td/table/tr/td/h3/text()')


    desc = tree.xpath('//*[contains(@id,"div")]/td/table/tr/td/p[1]')

    # filter out empty descriptions
    # Create a list of descriptions containing stripped version of the data read from the p tag. Replace the misformmated
    # "No Description Available" to a stripped representaion.
    desc = [x.text.strip() if "No Description Available" not in x.text else "No Description Available" for x in desc ]

    raw_prereq = tree.xpath('//*[contains(@id,"div")]/td/table/tr/td')
    prereq = []

    # get the prereqs
    for i in range(len(raw_prereq)):
        c = raw_prereq[i].getchildren()
        count  = 0

        # all the p tags in the prereq table data
        p_tags = [x  for x in c if a._element_name(x) == 'p']


        # append the prereq course. if there is no courses add empty string
        if len(p_tags) == 0:
            continue
        elif len(p_tags) == 1 :
            prereq.append("")

        else:
            current_string = str(p_tags[1].text_content().strip().encode('ascii', 'ignore'))

            if "Prereq:" not in current_string:
                prereq.append("")
            else:
                prereq.append(current_string.split("Prereq: ")[1])




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

    day_list = parse_days_from_string(days)

    [course_numbers,course_titles] = parse_title(course_title)
    scheduleCourse = []
    scheduleCourseTime = []

    # append to both scheduleCourse and scheduleCourseTime
    for course in range(len(course_numbers)):
        print course_numbers[course]
        scheduleCourse.append([course_numbers[course] ,section[course], course_titles[course], credits[course], credits[course], desc[course],prereq[course]])
        scheduleDays = day_list[course]
        for i in range(len(scheduleDays)):
            scheduleCourseTime.append([course_numbers[course], section[course], start_time[course],end_time[course],scheduleDays[i] ,get_qtr_id(target_qrt), 1,-1])


    return [scheduleCourse,scheduleCourseTime]

if __name__ == "__main__":
    # all the quaters that have schedules
    quarters = ["Summer", "Fall", "Spring"]

    # array of course info
    scheduleCourses = []

    # array of course schedule time
    scheduleCourseTimes = []
    for i in range(len(quarters)):
        scheduleCourse, scheduleCourseTime = create_schedule(quarters[i])
        scheduleCourses.append(scheduleCourse)
        scheduleCourseTimes.append(scheduleCourseTime)

    # create csv for courses
    create_csv("scheduleCourse" , scheduleCourses, ["CourseNumber", "Section", "Title","MinCredit", "MaxCredit", "Description", "PreRequisites"])

    # create csv for course scheduling
    create_csv("scheduleCourseTime" , scheduleCourseTimes, ["CourseNumber", "Section", "StartTimeID","EndTimeID","DayID" ,"QuarterID", "Year","Status"])

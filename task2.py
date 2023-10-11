#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Feb 13 03:23:21 2022

@author: ashikkhan
"""

import ply.lex as lex
import ply.yacc as yacc
import task1 as t1
import datetime

# GLOBAL VARIABLES

countrylist = []
continentlist = []

country_links = {}

country_info = {}
continent_info = {}
world_info = {}

pendamicPeriod =[]
reportValue = {}
closestSimilarReport = {}

#history log file
logfile = open("history.log","w")

# lexical analyzer
tokens = (
            'LINK',
            'ANCHOR',
            'TD_OPEN',
            'TD_CLOSE',
            'TD_NULL',
            'TR_WORLD',
            'TR_CONTINENT',
            'NOBR_CLOSE',
            'NOBR',
            'NEWCASEDATE',
            'NEWCASEDATA',
            'NEWCASECLOSE',
            'ACTIVECASESSTART',
            'ACTIVECASESDATE',
            'ACTIVECASESDATA',
            'NACTIVECASES',
            'NDAILYDEATH_DATE',
            'DAILYDEATH_DATE',
            'DAILYDEATH_DATA',
            'BRECOVERY_COUNTRY',
            'LRECOVERY',
            'ALL'
          )


# TOKEN DEFINITION
t_TD_CLOSE                  =   r'''</td>+'''
t_TD_OPEN                   =   r'''<td\sstyle="[\d\w() -.'\"()\s\:;=]+">+'''
t_TR_WORLD                  =   r'''<tr\sclass="total_row_world">'''
t_TR_CONTINENT              =   r'''<tr\sclass="total_row_world\srow_continent"\sdata-continent="[\w\s\d /:-]+"\sstyle="[\w\s\d:]+">'''
t_TD_NULL                   =   r'''<td>+'''
t_NOBR                      =   r'''<nobr>'''
t_NOBR_CLOSE                =   r'''</nobr>'''
t_LINK						= 	r'''<a\sclass="[\d\w()\-\]"\shref="country/[\d\w()\-\ _ "=]+>'''
t_ANCHOR					=	r'''<\/a>'''
t_ALL						= 	r'''[\d\w() -.'\/\"()\s\$]+'''
t_NEWCASEDATE               =   r'''<\/h3>\s<div\sid="[\d\w() -.'\/\"()\s\$]+"><\/div>\s<script\stype="[\d\w() -.'\/\"()\s\$]+">[\d\w() -.'\/\"()\s\$]+{[\d\w() : {} -.'\/\"()\s\$]+Daily\sNew\sCases[\d\w() : {} -.'\/\"()\s\$]+<br>[\d\w() : {} -.'\/\"()\s\$]+categories:\s\['''
t_NEWCASEDATA               =   r'''\][\d\w() : ; {} -.'\/\"()\s\$]+\[{\sname:\s'Daily\sCases'[\d\w() : {} -.'\/\"()\s\$]+data:\s\['''
t_NEWCASECLOSE              =   r''']\s}[[\d\w() : {} -.'\/\"()\s;\]\$]+'''
t_ACTIVECASESSTART          =   r'''<\/script>\s<div\sstyle="[\d\w() -.'\"()\s\:;=]+">+[\d\w() -.'\"()\s\:;=]+<a\sstyle="[\d\w() -.'\"()\s\:;=]+>[\d\w() -.'\"()\s\:;=]+<\/a>\s<\/div>\s<\/div>\s<\/div>\s<div\sclass="[\d\w() -.'\"()\s\:;=]+">\s<div\sclass="[\d\w() -.'\"()\s\:;=]+>\s<h3>Active\sCases\sin\s'''
t_ACTIVECASESDATE           =   r'''<\/h3>\s<div\sid="[\d\w() -.'\"()\s\:;=]+><\/div>\s<script\stype="text\/javascript">[\d\w() {} -.'\"()\s\:;=]+\['''
t_ACTIVECASESDATA           =   r'''\][\d\w() : ; {} -.'\/\"()\s\$]+\[{\sname:\s'Currently\sInfected'[\d\w() : ; {} -.'\/\"()\s\$]+\['''
t_NACTIVECASES              =   r'''<\/script>\s<div\sstyle="[\d\w() -.'\"()\s\:;=]+">+[\d\w() -.'\"()\s\:;=]+<a\sstyle="[\d\w() -.'\"()\s\:;=]+>[\d\w() -.'\"()\s\:;=]+<\/a>\s<\/div>\s<\/div>\s<\/div>\s<div\sclass="[\d\w() -.'\"()\s\:;=]+">\s<div\sclass="[\d\w() -.'\"()\s\:;=]+>\s<h3>Total\sCoronavirus\sDeaths\sin\s'''
t_NDAILYDEATH_DATE          =   r'''<\/h3>\s<style>[\d\w() -.'\/\"(){}:;<>=\s\$]+\[[\d\w() -.'\/\"()\s\$]+\]\s}[\d\w() -.'\/\"():{}\s\$]+\[{[\d\w() -.'\/\"():\s\$]+\[[\d\w() -.'\/\"()\s\$]+\]\s}\][\d\w() -.'\/\":{()\s\$]+\[{[\d\w() -.'\/\"():{}\s\$]+\]\s[\d\w() -.'\/\"(){};:\s\$]+\[[\d\w() -.'\/\"()\s\$]+\]\s}[\d\w() -.'\/\"():{}\s\$]+\[{[\d\w() -.'\/\"():\s\$]+\[[\d\w() -.'\/\"()\s\$]+\]\s}\][\d\w() -.'\/\"():{\s\$]+\[{[\d\w() -.'\/\"():{}\s\$]+\][\d\w() -.'\/\"();<>=:\s{}\$]+'Daily\sDeaths'[\d\w() -.'\/\"()\s{}:<>\$]+'''
t_DAILYDEATH_DATE           =   r'''\]\s}\s\],[\d\w() :{} [\]; -.'\/\"()\s\$]+<\/script>\s<\/div>\s<\/div>\s<div\sclass="[\d\w() -.'\/\"()\s\$]+>\s<div\sclass="[\d\w() -.'\/\"()\s\$]+>\s<h3>[\d\w() -.'\/\"()\s\$]+<\/h3>\s<style>[\d\w() { :;} -.'\/\"()>\s\$]+<\/style>\s[<>{:}[\];=\d\w() -.'\/\"()\s\$]+<h3>Daily\sNew\sDeaths\sin\s[\d\w() -.'\/\"()\s\$]+<\/h3>[<=>{:}\d\w() -.'\/\"()\s\$]+text:\s'Daily\sDeaths'[\d\w()}:{<> -.'\/\"()\s\$]+\['''
t_DAILYDEATH_DATA           =   r''']\s}[\d\w():{}; -.'\/\"()\s\$]+\[{\sname:\s'Daily\sDeaths',[\d\w(): -.'\/\"()\s\$]+\['''
t_BRECOVERY_COUNTRY         =   r'''[\d\w]+<\/h3>\s<div\sid="cases-cured-daily">'''
t_LRECOVERY                 =   r'''<\/div>\s<script\stype="text\/javascript">\s[\d\w() {} -.'\"()\s\:;=]+\[[\d\w() -.'\/\"()\s\$]+\]\s},[\d\w() -.'\/\"():{}\s\$]+\[{\sname:\s'New\sRecoveries',[\d\w() -.'\/\"():\s\$]+\['''
t_ignore_COMMENT            =   r'\#.*'
t_ignore                    =   ' \t'    # ignores spaces and tabs

def t_error (t):
#   print("Illegal character '%s'" % t.value[0])
    t.lexer.skip(1)

def p_start(p):
    '''Start : S1
            | S2
            | S3
            | S4
            | S5
            | S6
            | S7
            | S8
            | S9
            | S10
            | S11
            | S12
            | S13
            | S14
            | S15
            '''



def p_country_data(p):
    'S1 : TD_OPEN LINK ALL ANCHOR TD_CLOSE TD_OPEN ALL TD_CLOSE TD_OPEN ALL TD_CLOSE TD_OPEN ALL TD_CLOSE TD_OPEN ALL TD_CLOSE TD_OPEN ALL TD_CLOSE TD_OPEN ALL TD_CLOSE TD_OPEN ALL TD_CLOSE TD_OPEN ALL TD_CLOSE TD_OPEN ALL TD_CLOSE TD_OPEN ALL TD_CLOSE TD_OPEN ALL TD_CLOSE TD_OPEN ALL TD_CLOSE'
    store_country_data(p[3].strip(), p[7].strip(), p[10].strip(), p[13].strip(), p[16].strip(), p[19].strip(), p[22].strip(),p[25].strip(), p[28].strip(), p[31].strip(), p[34].strip(), p[37].strip(), p[40].strip())

def p_new_death_less_country_data(p):
    'S2 : TD_OPEN LINK ALL ANCHOR TD_CLOSE TD_OPEN ALL TD_CLOSE TD_OPEN ALL TD_CLOSE TD_OPEN ALL TD_CLOSE TD_OPEN TD_CLOSE TD_OPEN ALL TD_CLOSE TD_OPEN ALL TD_CLOSE TD_OPEN ALL TD_CLOSE TD_OPEN ALL TD_CLOSE TD_OPEN ALL TD_CLOSE TD_OPEN ALL TD_CLOSE TD_OPEN ALL TD_CLOSE TD_OPEN ALL TD_CLOSE'
    store_country_data(p[3].strip(), p[7].strip(), p[10].strip(), p[13].strip(), 0, p[18].strip(),p[21].strip(), p[24].strip(), p[27].strip(), p[30].strip(), p[33].strip(), p[36].strip(),p[39].strip())

def p_new_recover_less_country_data(p):
    'S3 : TD_OPEN LINK ALL ANCHOR TD_CLOSE TD_OPEN ALL TD_CLOSE TD_OPEN ALL TD_CLOSE TD_OPEN ALL TD_CLOSE TD_OPEN TD_CLOSE TD_OPEN ALL TD_CLOSE TD_OPEN ALL TD_CLOSE TD_OPEN TD_CLOSE TD_OPEN ALL TD_CLOSE TD_OPEN ALL TD_CLOSE TD_OPEN ALL TD_CLOSE TD_OPEN ALL TD_CLOSE TD_OPEN ALL TD_CLOSE'
    store_country_data(p[3].strip(), p[7].strip(), p[10].strip(), p[13].strip(), 0, p[18].strip(), 0,p[23].strip(), p[26].strip(), p[29].strip(), p[32].strip(), p[35].strip(), p[38].strip())

def p_new_case_less_country_data(p):
    'S4 : TD_OPEN LINK ALL ANCHOR TD_CLOSE TD_OPEN ALL TD_CLOSE TD_OPEN TD_CLOSE TD_OPEN ALL TD_CLOSE TD_OPEN TD_CLOSE TD_OPEN ALL TD_CLOSE TD_OPEN TD_CLOSE TD_OPEN ALL TD_CLOSE TD_OPEN ALL TD_CLOSE TD_OPEN ALL TD_CLOSE TD_OPEN ALL TD_CLOSE TD_OPEN ALL TD_CLOSE TD_OPEN ALL TD_CLOSE'
    store_country_data(p[3].strip(), p[7].strip(), 0, p[12].strip(), 0, p[17].strip(), 0, p[22].strip(),p[25].strip(), p[28].strip(), p[31].strip(), p[34].strip(), p[37].strip())

def p_critical_case_less_country_data(p):
    'S5 : TD_OPEN LINK ALL ANCHOR TD_CLOSE TD_OPEN ALL TD_CLOSE TD_OPEN TD_CLOSE TD_OPEN ALL TD_CLOSE TD_OPEN TD_CLOSE TD_OPEN ALL TD_CLOSE TD_OPEN TD_CLOSE TD_OPEN ALL TD_CLOSE TD_OPEN TD_CLOSE TD_OPEN ALL TD_CLOSE TD_OPEN ALL TD_CLOSE TD_OPEN ALL TD_CLOSE TD_OPEN ALL TD_CLOSE'
    store_country_data(p[3].strip(), p[7].strip(), 0, p[12].strip(), 0, p[17].strip(), 0, p[22].strip(), 0,p[27].strip(), p[30].strip(), p[33].strip(), p[36].strip())

def p_new_death_critical_case_less_country_data(p):
    'S6 : TD_OPEN LINK ALL ANCHOR TD_CLOSE TD_OPEN ALL TD_CLOSE TD_OPEN ALL TD_CLOSE TD_OPEN ALL TD_CLOSE TD_OPEN TD_CLOSE TD_OPEN ALL TD_CLOSE TD_OPEN ALL TD_CLOSE TD_OPEN ALL TD_CLOSE TD_OPEN TD_CLOSE TD_OPEN ALL TD_CLOSE TD_OPEN ALL TD_CLOSE TD_OPEN ALL TD_CLOSE TD_OPEN ALL TD_CLOSE'
    store_country_data(p[3].strip(), p[7].strip(), p[10].strip(), p[13].strip(), 0, p[18].strip(), p[21].strip(), p[24].strip(), 0,p[29].strip(), p[32].strip(), p[35].strip(), p[38].strip())

def p_only_critical_case_less_country_data(p):
    'S7 : TD_OPEN LINK ALL ANCHOR TD_CLOSE TD_OPEN ALL TD_CLOSE TD_OPEN ALL TD_CLOSE TD_OPEN ALL TD_CLOSE TD_OPEN ALL TD_CLOSE TD_OPEN ALL TD_CLOSE TD_OPEN ALL TD_CLOSE TD_OPEN ALL TD_CLOSE TD_OPEN TD_CLOSE TD_OPEN ALL TD_CLOSE TD_OPEN ALL TD_CLOSE TD_OPEN ALL TD_CLOSE TD_OPEN ALL TD_CLOSE'
    store_country_data(p[3].strip(), p[7].strip(), p[10].strip(), p[13].strip(), p[16].strip(), p[19].strip(), p[22].strip(), p[25].strip(), 0,p[30].strip(), p[33].strip(), p[36].strip(), p[39].strip())

def p_only_new_covered_less_country_data(p):
    'S8 : TD_OPEN LINK ALL ANCHOR TD_CLOSE TD_OPEN ALL TD_CLOSE TD_OPEN ALL TD_CLOSE TD_OPEN ALL TD_CLOSE TD_OPEN ALL TD_CLOSE TD_OPEN ALL TD_CLOSE TD_OPEN TD_CLOSE TD_OPEN ALL TD_CLOSE TD_OPEN ALL TD_CLOSE TD_OPEN ALL TD_CLOSE TD_OPEN ALL TD_CLOSE TD_OPEN ALL TD_CLOSE TD_OPEN ALL TD_CLOSE'
    store_country_data(p[3].strip(), p[7].strip(), p[10].strip(), p[13].strip(), p[16].strip(), p[19].strip(), 0, p[24].strip(), p[27].strip(),p[30].strip(), p[33].strip(), p[36].strip(), p[39].strip())

def p_only_new_cases_death_less_country_data(p):
    'S9 : TD_OPEN LINK ALL ANCHOR TD_CLOSE TD_OPEN ALL TD_CLOSE TD_OPEN TD_CLOSE TD_OPEN ALL TD_CLOSE TD_OPEN TD_CLOSE TD_OPEN ALL TD_CLOSE TD_OPEN ALL TD_CLOSE TD_OPEN ALL TD_CLOSE TD_OPEN ALL TD_CLOSE TD_OPEN ALL TD_CLOSE TD_OPEN ALL TD_CLOSE TD_OPEN ALL TD_CLOSE TD_OPEN ALL TD_CLOSE'
    store_country_data(p[3].strip(), p[7].strip(), 0, p[12].strip(), 0, p[17].strip(), p[20].strip(), p[23].strip(), p[26].strip(),p[29].strip(), p[32].strip(), p[35].strip(), p[38].strip())

def p_check_data(p):
    'S10 : TD_OPEN LINK ALL ANCHOR TD_CLOSE TD_OPEN ALL TD_CLOSE TD_OPEN TD_CLOSE TD_OPEN ALL TD_CLOSE TD_OPEN ALL TD_CLOSE TD_OPEN ALL TD_CLOSE TD_OPEN TD_CLOSE TD_OPEN ALL TD_CLOSE TD_OPEN ALL TD_CLOSE TD_OPEN ALL TD_CLOSE TD_OPEN ALL TD_CLOSE TD_OPEN ALL TD_CLOSE TD_OPEN ALL TD_CLOSE'
    store_country_data(p[3].strip(), p[7].strip(), 0,p[12].strip(), p[15].strip(), p[18].strip(), 0, p[23].strip(),p[26].strip(), p[29].strip(), p[32].strip(), p[35].strip(), p[38].strip())

def p_world_data(p):
    'S11 : TR_WORLD TD_NULL TD_CLOSE TD_OPEN ALL TD_CLOSE TD_NULL ALL TD_CLOSE TD_NULL ALL TD_CLOSE TD_NULL ALL TD_CLOSE TD_NULL ALL TD_CLOSE TD_NULL ALL TD_CLOSE TD_NULL ALL TD_CLOSE TD_NULL ALL TD_CLOSE TD_NULL ALL TD_CLOSE TD_NULL ALL TD_CLOSE TD_NULL ALL TD_CLOSE'
    world_info['total_cases'] = p[8]
    world_info['new_cases'] = p[11]
    world_info['total_death'] = p[14]
    world_info['new_death'] = p[17]
    world_info['total_recovered'] = p[20]
    world_info['new_recovered'] = p[23]
    world_info['active_cases'] = p[26]
    world_info['critical'] = p[29]
    world_info['cases_million'] = p[32]
    world_info['death_million'] = p[35]
    # print(world_info)

def p_continent_data(p):
    'S12 : TR_CONTINENT TD_NULL TD_CLOSE TD_OPEN NOBR ALL NOBR_CLOSE TD_CLOSE TD_NULL ALL TD_CLOSE TD_NULL ALL TD_CLOSE TD_NULL ALL TD_CLOSE TD_NULL ALL TD_CLOSE TD_NULL ALL TD_CLOSE TD_NULL ALL TD_CLOSE TD_NULL ALL TD_CLOSE TD_NULL ALL TD_CLOSE'
    continent_name = p[6]
    continent_info[continent_name] = {}
    continent_info[continent_name]['continent_name'] = p[6]
    continent_info[continent_name]['total_cases'] = p[10]
    continent_info[continent_name]['new_cases'] = p[13]
    continent_info[continent_name]['total_death'] = p[16]
    continent_info[continent_name]['new_death'] = p[19]
    continent_info[continent_name]['total_recovered'] = p[22]
    continent_info[continent_name]['new_recovered'] = p[25]
    continent_info[continent_name]['active_cases'] = p[28]
    continent_info[continent_name]['critical'] = p[30]
    # print(continent_info)


def store_country_data(country_name,total_cases,new_cases,total_death,new_death,total_recovered,new_recovered,active_cases,critical,cases_million,death_million,total_test,test_million):
    country_info[country_name] = {}
    country_info[country_name]['country_name'] = country_name
    country_info[country_name]['total_cases'] = total_cases
    country_info[country_name]['new_cases'] = new_cases
    country_info[country_name]['total_death'] = total_death
    country_info[country_name]['new_death'] = new_death
    country_info[country_name]['total_recovered'] = total_recovered
    country_info[country_name]['new_recovered'] = new_recovered
    country_info[country_name]['active_cases'] = active_cases
    country_info[country_name]['critical'] = critical
    country_info[country_name]['cases_million'] = cases_million
    country_info[country_name]['death_million'] = death_million
    country_info[country_name]['total_test'] = total_test
    country_info[country_name]['test_million'] = test_million
    country_info[country_name]['test_million'] = test_million
    # print(country_info[country_name], len(country_info))


def p_covid_new_case_report(p):
    'S13 : NEWCASEDATE ALL NEWCASEDATA ALL NEWCASECLOSE ACTIVECASESSTART ALL ACTIVECASESDATE ALL ACTIVECASESDATA ALL DAILYDEATH_DATE ALL DAILYDEATH_DATA ALL'
    newcase_date = p[2]
    newcase_data = p[4]
    country_name = p[7]
    activecase_date = p[9]
    activecase_data = p[11]
    dailydeath_date = p[13]
    dailydeath_data = p[15]
    store_report_data(newcase_date, newcase_data, country_name, activecase_date, activecase_data, dailydeath_date, dailydeath_data)


def p_Rest_Report_Data(p):
    'S14 : NEWCASEDATE ALL NEWCASEDATA ALL NEWCASECLOSE NACTIVECASES ALL NDAILYDEATH_DATE ALL DAILYDEATH_DATA ALL'
    newcase_date = p[2]
    newcase_data = p[4]
    country_name = p[7]
    dailydeath_date = p[9]
    dailydeath_data = p[11]
    store_report_data(newcase_date, newcase_data, country_name, '', '', dailydeath_date, dailydeath_data)

def store_report_data(newcase_date, newcase_data, country_name, activecase_date, activecase_data, dailydeath_date, dailydeath_data):
    if (country_name == "the United Kingdom"):
        country_name = "UK"
    elif (country_name == "the Netherlands"):
        country_name = "Netherlands"
    elif (country_name == "the United States"):
        country_name = "USA"
    elif (country_name == "the Philippines"):
        country_name = "Philippines"
    # print(country_name)
    reportValue[country_name] = {}
    reportValue[country_name]["newcase_date"] = processReportData(newcase_date)
    reportValue[country_name]["newcase_data"] = newcase_data.split(",")
    pendamicPeriod = reportValue[country_name]["newcase_date"]

    if(activecase_date):
        reportValue[country_name]["activecase_date"] = processReportData(activecase_date)
        reportValue[country_name]["activecase_data"] = activecase_data.split(",")

    reportValue[country_name]["dailydeath_date"] = processReportData(dailydeath_date)
    reportValue[country_name]["dailydeath_data"] = dailydeath_data.split(",")

def p_Recovery_Data(p):
    '''S15 : BRECOVERY_COUNTRY LRECOVERY ALL '''
    country_name = p[1].split('<')[0]
    recovery_rate = p[3].split(",")
    reportValue[country_name]["recovery_rate"] = recovery_rate

def p_error(p):
    pass

def processReportData(data):
    data = data.split('","')
    data[0] = data[0].split('"')[1]
    data[-1] = data[-1].split('"')[0]

    return data

def getYesterdayData(data):
    delim = '<table id="main_table_countries_yesterday" class="table table-bordered table-hover main_table_countries" style="width:100%;margin-top: 0px !important;display:none;">'
    data = data.partition(delim)[2]
    delim_before = '<table id="main_table_countries_yesterday2" class="table table-bordered table-hover main_table_countries" style="width:100%;margin-top: 0px !important;display:none;">'
    data = data.split(delim_before)[0]
    return data

def getReportData(data):
    delim = '<h3>Daily New Cases in '
    data = data.partition(delim)[2]
    delim_before = '</a></strong>'
    data = data.split(delim_before)[0]
    return data

def checkRecoveryData(data):
    delim = "name: 'New Recoveries',"
    delim_before = '<h3>Outcome of Cases (Recovery or Death) in'
    if(data.find(delim) == -1 ):
        return False
    elif(data.find(delim_before) == -1):
        return False
    elif(data.find(delim) > data.find(delim_before)):
        return False
    return True

def getRecoveryData(data):
    delim = '<h3>Newly Infected vs. Newly Recovered in '
    data = data.partition(delim)[2]
    delim_before = '<h3>Outcome of Cases (Recovery or Death) in'
    data = data.split(delim_before)[0]
    return data

def read_html(data):
    data = getYesterdayData(data)
    # print(data)
    lexer = lex.lex()
    parser = yacc.yacc()
    parser.parse(data)

    country_dict = t1.get_country_dic()

    for continent in country_dict:
        for country in country_dict[continent]:
            country_path = "./HTML/"+continent+"/" + country + ".html"
            country_file = open(country_path, "r")
            m_content = country_file.read()
            content = getReportData(m_content)
            # print(country)
            parser.parse(content)

            if(checkRecoveryData(m_content) == True):
                recovery_content = getRecoveryData(m_content)
                # print("country")
                f = open("hi.txt", "w")
                f.write(recovery_content)
                f.close()
                parser.parse(recovery_content)

    # print("Parsing Done!")

#---------------FIle Wise----------------------------------------
def extract_countrylist():
    inputFileName = "worldometers_countrylist.txt"
    with open(inputFileName) as f:
        content = f.readlines()
    content = [x.strip() for x in content]
    stand = 0

    for country in content:
        if country.endswith(":"):
            country.strip()
            country = country[:-1]
            continentlist.append(country)
        elif not country:
            stand = 1
        elif country.endswith("-"):
            stand = 0
        elif stand == 1:
            country.strip()
            continentlist.append(country)
        else:
            country.strip()
            countrylist.append(country)

#-----------------------------------------------------

def checkOptionNo(element,lenth):
    try:
        if(int(element) and int(element) <= lenth):
            return True
        else:
            return False
    except ValueError:
        return False

def dateRange(country_name,startDate,endDate):
    value=0
    startdateVal = ""
    endDateVal = ""
    try:
        if(startDate.count('-') == 2 and endDate.count('-') == 2):
            startDate = startDate.split('-')
            startD = datetime.datetime(int(startDate[2]), int(startDate[1]), int(startDate[0]))
            startdateVal = startD.strftime("%b %d, %Y")
            endDate = endDate.split('-')
            endD = datetime.datetime(int(endDate[2]), int(endDate[1]), int(endDate[0]))
            endDateVal  = endD.strftime("%b %d, %Y")
            startdateIndex = reportValue[country_name]["newcase_date"].index(startdateVal)
            enddateIndex = reportValue[country_name]["newcase_date"].index(endDateVal)
            if ( startdateIndex <= enddateIndex):
                value = 1
            else:
                print("Invalid Range.")
    except:
        value=0
    return (value,startdateVal,endDateVal)

def countryQuery():
    optionListLowerCase = []
    for option_reg in countrylist:
        optionListLowerCase.append(option_reg.lower())

    print(" ---------------------------")
    print("|       Select Country     |")
    print(" ---------------------------")
    for (i, country) in enumerate(countrylist, start=1):
        print(":   {}. {}".format(i, country))
    print(" ---------------------------")
    while (1):
        option_no = input("\nEnter Country name/no (Enter (back) for going back):\n")

        if (option_no == "back"):
            break
        elif (checkOptionNo(option_no, len(countrylist))):
            country_name = countrylist[int(option_no) - 1]
            print(country_name)
            queryMenu(country_name)
        elif (option_no in countrylist):
            country_name = option_no
            print(country_name)
            queryMenu(country_name)
        elif (option_no in optionListLowerCase):
            country_name = countrylist[optionListLowerCase.index(option_no)]
            print(country_name)
            queryMenu(country_name)
        else:
            print("Invalid option.\n")

def showQueryResult(country_name,startdateIndex,enddateIndex,option_no,queryOption,queryFullName,similarity):

    try:
        req_list = reportValue[country_name][queryOption[option_no]]
        if(req_list[startdateIndex] == 'null' and  req_list[enddateIndex] == 'null'):
            changeinrate = 0
        elif((req_list[startdateIndex] == 'null' and  req_list[enddateIndex] != 'null') or (req_list[startdateIndex] == '0')):
            changeinrate = 100
        elif (req_list[startdateIndex] != 'null' and req_list[enddateIndex] == 'null'):
            changeinrate = -100
        else:
            startData = int(req_list[startdateIndex])
            endData = int(req_list[enddateIndex])
            changeinrate = ((endData- startData ) / endData) * 100

        if(similarity == 0):
            print("{} :{} to {} --> {} :{}".format(country_name,reportValue[country_name]["newcase_date"][startdateIndex],
                                                   reportValue[country_name]["newcase_date"][enddateIndex],
                                                   queryFullName[option_no], changeinrate))
            loc_str = '<' + country_name + '>' + ' ' + '< Query  -' + str(option_no+1) + '>' + ' ' + '< '+ str(changeinrate) +' >' + '\n'
            logfile.writelines(loc_str)
        else:
            closestSimilarReport[country_name][queryOption[option_no]] = changeinrate
    except:
        if (similarity == 0):
            print("{} :{} to {} --> {} :{}".format(country_name,reportValue[country_name]["newcase_date"][startdateIndex],
                                                   reportValue[country_name]["newcase_date"][enddateIndex],
                                                   queryFullName[option_no], 0))
            loc_str = '<' + country_name + '>' + ' ' + '< Query  -'+ str(option_no+1) + '>' + ' ' + '< 0 >' + '\n'
            logfile.writelines(loc_str)
        else:
            closestSimilarReport[country_name][queryOption[option_no]] = 0

def getBestSimilarity(country_name,startdateIndex,enddateIndex):

    queryOption = ['activecase_data', 'dailydeath_data', 'recovery_rate', 'newcase_data', ]
    queryFullName = [' Change in active cases in % ', 'Change in daily death in %', 'Change in new recovered in % ','Change in new cases in %  ']
    similarity = 1
    for country in countrylist:
        closestSimilarReport[country] = {}
        for opt in queryOption:
            closestSimilarReport[country][opt] = []
            option_no = queryOption.index(opt)
            showQueryResult(country, startdateIndex, enddateIndex, option_no, queryOption, queryFullName, similarity)

    queryOption = ['activecase_data', 'dailydeath_data', 'recovery_rate', 'newcase_data', ]
    activecase_near_country = ''
    activecase_near_value = 0
    dailydeath_near_country = ''
    dailydeath_near_value = 0
    recovery_near_country = ''
    recovery_near_value = 0
    newcase_near_country = ''
    newcase_near_value = 0
    start = 0

    for country in closestSimilarReport:
        if(country != country_name):

            if(start == 0 or abs(closestSimilarReport[country_name][queryOption[0]] - closestSimilarReport[country][queryOption[0]]) < activecase_near_value):
                activecase_near_country = country
                activecase_near_value = abs(closestSimilarReport[country_name][queryOption[0]] - closestSimilarReport[country][queryOption[0]])

            if (start == 0 or abs(closestSimilarReport[country_name][queryOption[1]] - closestSimilarReport[country][queryOption[1]]) < dailydeath_near_value):
                dailydeath_near_country = country
                dailydeath_near_value = abs(closestSimilarReport[country_name][queryOption[1]] - closestSimilarReport[country][queryOption[1]])

            if (start == 0 or abs(closestSimilarReport[country_name][queryOption[2]] - closestSimilarReport[country][queryOption[2]]) < recovery_near_value):
                recovery_near_country = country
                recovery_near_value = abs(closestSimilarReport[country_name][queryOption[2]] - closestSimilarReport[country][queryOption[2]])

            if (start == 0 or abs(closestSimilarReport[country_name][queryOption[3]] - closestSimilarReport[country][queryOption[3]]) < newcase_near_value):
                newcase_near_country = country
                newcase_near_value = abs(closestSimilarReport[country_name][queryOption[3]] - closestSimilarReport[country][queryOption[3]])
            #continuious
            start = 1

    similarity_dict = {}
    similarity_dict['similarity_value'] = []
    similarity_dict['similarity_value'] = [activecase_near_value, dailydeath_near_value, recovery_near_value,newcase_near_value]
    similarity_dict['similarity_country'] = []
    similarity_dict['similarity_country'] = [activecase_near_country, dailydeath_near_country, recovery_near_country,newcase_near_country]

    best_similarity = min(activecase_near_value,dailydeath_near_value,recovery_near_value,newcase_near_value)
    best_smlr_cntry = ''
    similar_option = ''
    if(best_similarity == activecase_near_value):
        best_smlr_cntry = activecase_near_country
        similar_option = "Change in active cases in %  "
    elif(best_similarity == dailydeath_near_value):
        best_smlr_cntry = dailydeath_near_country
        similar_option = "Change in daily death in %   "
    elif (best_similarity == recovery_near_value):
        best_smlr_cntry = recovery_near_country
        similar_option = "Change in new recovered in %  "
    elif (best_similarity == newcase_near_value):
        best_smlr_cntry = newcase_near_country
        similar_option = "Change in new cases in %   "

    return (similar_option,best_smlr_cntry,best_similarity,similarity_dict)

def queryMenu(country_name):
    print("---------------------------------------------------------")
    print("     {} COVID-19 Coronavirus Pandemic Query   ".format(country_name))
    print("---------------------------------------------------------")
    print("|   1. Change in active cases in %                      |")
    print("|   2. Change in daily death in %                       |")
    print("|   3. Change in new recovered in %                     |")
    print("|   4. Change in new cases in %                         |")
    print("|   5. Closest country similar to any query between 1-4 |")
    print("---------------------------------------------------------")

    queryOption = ['activecase_data','dailydeath_data','recovery_rate','newcase_data',]
    queryFullName = [' Change in active cases in % ', 'Change in daily death in %', 'Change in new recovered in % ', 'Change in new cases in %  ']

    while (1):
        option_no = input("\nEnter the QUERY no ( number only ) (Enter (back) for going back):\n")

        if (option_no == "back"):
            break
        elif (checkOptionNo(option_no, 5)):
            option_no = int(option_no)

            print("Enter Query Start Date and End Date in range of {} and {}".format(reportValue[country_name]["newcase_date"][0],
                                                                                     reportValue[country_name]["newcase_date"][-1]))
            startDate = input("Start Date(Format 01-01-2022):")
            endDate = input("End Date(Format 01-01-2022):")
            (val,startDate,endDate) = dateRange(country_name,startDate,endDate)
            if(val == 0):
                print("Wrong Date Format! Try again.")
                break
            else:
                startdateIndex = reportValue[country_name]["newcase_date"].index(startDate)
                enddateIndex = reportValue[country_name]["newcase_date"].index(endDate)

                (similar_option, best_smlr_cntry, best_similarity, similarity_dict) = getBestSimilarity(country_name, startdateIndex, enddateIndex)

                if (option_no < 5):
                    similarity = 0
                    option_no = option_no - 1
                    showQueryResult(country_name,startdateIndex,enddateIndex,option_no,queryOption,queryFullName,similarity)
                    print("Closest country similar to {} : {} , difference margin {}".format(queryFullName[option_no],similarity_dict["similarity_country"][option_no],similarity_dict["similarity_value"][option_no]))
                else:
                    for x in range(4):
                        print("\n{} :{} to {} --> {} :{}".format(country_name, reportValue[country_name]["newcase_date"][startdateIndex],reportValue[country_name]["newcase_date"][enddateIndex],queryFullName[x], closestSimilarReport[country_name][queryOption[x]]))
                        print("Closest country similar to {} : {} , difference margin {}".format(queryFullName[x],similarity_dict["similarity_country"][x], similarity_dict["similarity_value"][x]))
                    print("\nDifference with {} and {} on based of {}: {}".format(country_name, best_smlr_cntry,similar_option, best_similarity))
                    print("\n{} :{} to {} --> Closest country similar to any query between 1-4 :{} ".format(country_name,reportValue[country_name]["newcase_date"][startdateIndex], reportValue[country_name]["newcase_date"][enddateIndex], best_smlr_cntry))

                    loc_str = '<' + country_name + '>' + ' ' + '< Query  -5>' + ' ' + '< ' + best_smlr_cntry + ' >' + '\n'
                    logfile.writelines(loc_str)

        else:
            print("Invalid option.\n")

def world_percentage(option_no,suboptionIndex,comp_data):
    world_percen = "not available"
    try:
        if (option_no not in [5, 7]):
            world_percen = world_info[suboptionIndex[int(option_no) - 1]]

            world_percen = world_percen.replace(",", "")
            world_percen = world_percen.replace("+", "")
            world_percen = int(world_percen)

            comp_data = comp_data.replace(",", "")
            comp_data = comp_data.replace("+", "")
            comp_data = int(comp_data)

            world_percen = (comp_data/world_percen)*100
    except:
        world_percen = "null"

    return world_percen

def subOptionMenu(menu,givenOption):
    suboption = ['Total cases','Active cases','Total deaths','Total recovered','Total tests','Death/million','Tests/million','New case','New death','New recovered']
    suboptionIndex = ['total_cases', 'active_cases', 'total_death', 'total_recovered', 'total_test', 'death_million','test_million', 'new_cases', 'new_death', 'new_recovered']

    print("----------------------------------------------------------")
    print("|  {} COVID-19 Coronavirus Pandemic Information  ".format(givenOption))
    print("----------------------------------------------------------")

    j=1
    for (i,option) in enumerate(suboption, start=1):
        # if(menu == 'Continent')
        if (menu == "World" and i not in [5, 7]):
            print("|   {}. {}".format(j, option))
            j = j + 1
        elif (menu == "Continent" and i not in [5,6, 7]):
            print("|   {}. {}".format(j, option))
            j = j + 1
        elif (menu == "Country"):
            print("|   {}. {}".format(j, option))
            j = j + 1
    print("-----------------------------------------------------------")
    option_no = input("\nEnter Info name/no:\n")

    if (menu == "World" and checkOptionNo(option_no, 8)):
        option_no = int(option_no)
        if (option_no > 5):
            option_no += 2
        elif (option_no > 4):
            option_no += 1

        print("{} --> {} : {}".format(givenOption,suboption[int(option_no) - 1],world_info[suboptionIndex[int(option_no) - 1]]))

        loc_str = '<' + givenOption + '>' + ' ' + '<' + suboption[int(option_no) - 1] + '>' + ' ' + '<' + str(world_info[suboptionIndex[int(option_no) - 1]]) + '>' + '\n'
        logfile.writelines(loc_str)

    elif (menu == "Continent" and checkOptionNo(option_no, 7)):

        option_no = int(option_no)
        if (option_no > 4):
            option_no += 3

        world_percen = world_percentage(option_no,suboptionIndex,continent_info[givenOption][suboptionIndex[int(option_no) - 1]])

        print("{} --> {} : {}  ,the percent of total world cases :  {}".format(givenOption,suboption[int(option_no) - 1],continent_info[givenOption][suboptionIndex[int(option_no) - 1]],world_percen))

        loc_str = '<' + givenOption + '>' + ' ' + '<' + suboption[int(option_no) - 1] + '>' + ' ' + '<' + str(continent_info[givenOption][suboptionIndex[int(option_no) - 1]]) + '>' + '\n'
        logfile.writelines(loc_str)

    elif (menu == "Country" and checkOptionNo(option_no, 10)):
        world_percen = world_percentage(option_no, suboptionIndex,country_info[givenOption][suboptionIndex[int(option_no) - 1]])

        print("{} --> {} : {}  ,the percent of total world cases :  {}".format(givenOption,suboption[int(option_no) - 1],country_info[givenOption][suboptionIndex[int(option_no) - 1]],world_percen))

        loc_str = '<' + givenOption + '>'+' '+'<'+ suboption[int(option_no) - 1] + '>'+' '+'<' + str(country_info[givenOption][suboptionIndex[int(option_no) - 1]] )+ '>' + '\n'
        logfile.writelines(loc_str)
    elif (menu == "World" and option_no in suboption and option_no not in ['Total tests','Tests/million']):
        option_no = suboption.index(option_no)

        print("{} --> {} : {}".format(givenOption,suboption[int(option_no) - 1],world_info[suboptionIndex[int(option_no) - 1]]))

        loc_str = '<' + givenOption + '>' + ' ' + '<' + suboption[int(option_no) - 1] + '>' + ' ' + '<' + str(world_info[suboptionIndex[int(option_no) - 1]]) + '>' + '\n'
        logfile.writelines(loc_str)
    elif (menu == "Continent" and option_no in suboption and option_no not in ['Total tests','Death/million','Tests/million']):
        option_no = suboption.index(option_no)
        world_percen = world_percentage(option_no, suboptionIndex, continent_info[givenOption][suboptionIndex[int(option_no) - 1]])

        print("{} --> {} : {} , the percent of total world cases :  {}".format(givenOption,suboption[int(option_no) - 1],continent_info[givenOption][suboptionIndex[int(option_no) - 1]],world_percen))

        loc_str = '<' + givenOption + '>' + ' ' + '<' + suboption[int(option_no) - 1] + '>' + ' ' + '<' + str(continent_info[givenOption][suboptionIndex[int(option_no) - 1]]) + '>' + '\n'
        logfile.writelines(loc_str)
    elif (menu == "Country" and option_no in suboption):
        option_no = suboption.index(option_no)
        world_percen = world_percentage(option_no, suboptionIndex,country_info[givenOption][suboptionIndex[int(option_no) - 1]])

        print("{} --> {} : {}  ,,the percent of total world cases :  {}".format(givenOption,suboption[int(option_no) - 1],country_info[givenOption][suboptionIndex[int(option_no) - 1]],world_percen))

        loc_str = '<' + givenOption + '>' + ' ' + '<' + suboption[int(option_no) - 1] + '>' + ' ' + '<' + str(country_info[givenOption][suboptionIndex[int(option_no) - 1]]) + '>' + '\n'
        logfile.writelines(loc_str)
    else:
        print("Invalid option.\n")



def optionMenu(optionList,menu):

    optionListLowerCase = []
    for option_reg in optionList:
        optionListLowerCase.append(option_reg.lower())

    print(" ---------------------------")
    print("       {} List        ".format(menu))
    print(" ---------------------------")
    for (i, option) in enumerate(optionList, start=1):
        print("|   {}. {}".format(i, option))
    print(" ---------------------------")

    while(1):
        option_no = input("\nEnter {} name/no (Enter (back) for going back):\n".format(menu))

        if (option_no == "back"):
            break
        elif (checkOptionNo(option_no, len(optionList))):
            country_name = optionList[int(option_no) - 1]
            # print(country_name)
            subOptionMenu(menu, country_name)
        elif (option_no in optionList ):
            country_name = option_no
            # print(country_name)
            subOptionMenu(menu, country_name)
        elif (option_no in optionListLowerCase):
            country_name = optionList[optionListLowerCase.index(option_no)]
            # print(country_name)
            subOptionMenu(menu, country_name)
        else:
            print("Invalid option.\n")

def main():

    url = "https://www.worldometers.info/coronavirus/"
    page = "coronavirus"

    main_path = "./HTML/" + page + ".html"
    f = open(main_path, "r")
    content = f.read()

    extract_countrylist()
    all_country_links = t1.extract_all_country_links(content)
    for country in countrylist:
        country_links[country] = t1.get_country_link(all_country_links, country)

    read_html(content)

    i = 0
    for country in  countrylist :
        if(country not in country_info):
            print(country)
            i=i+1
            print(i)

    while (1):
        print(" ---------------------------------------------")
        print(" | COVID-19 Coronavirus Pandemic Information |")
        print(" ---------------------------------------------")
        print(" |        1. Country                         |")
        print(" |        2. Continent                       |")
        print(" |        3. World                           |")
        print(" |        4. Query                           |")
        print(" ---------------------------------------------")
        info_type = input("Enter option name/no (Enter (exit) for the exit):\n")
        info_type = info_type.strip()

        if(info_type == "Country" or info_type == "country" or info_type == '1'):
            info_type = "Country"
            optionMenu(countrylist,info_type)

        elif(info_type == "Continent" or info_type == "continent" or info_type == '2'):
            info_type = "Continent"
            optionMenu(continentlist,info_type)

        elif (info_type == "World" or info_type == "world" or info_type == '3'):
            info_type = "World"
            subOptionMenu(info_type,info_type)

        elif (info_type == "Query" or info_type == "query" or info_type == '4'):
            info_type = "Query"

            countryQuery()

        elif(info_type == "exit"):
            break
        else:
            print("Invalid option.\n")

    # logfile.writelines("End!")
    logfile.close()

if __name__=="__main__":
    main()



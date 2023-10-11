#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Feb 26 16:11:21 2022

@author: ashikkhan
"""
import ply.lex as lex
import ply.yacc as yacc
import os
import re
import task1 as t1
import task2 as t2
from urllib.request import Request, urlopen
import datetime
from wordcloud import WordCloud, STOPWORDS
import matplotlib.pyplot as plt
from collections import Counter
import nltk
from nltk.corpus import stopwords
nltk.download('stopwords')
from nltk.tokenize import word_tokenize
import pandas as pd


# GLOBAL VARIABLE
countrylist = t2.countrylist
country_links = t2.country_links
country_info = t2.country_info
continentlist = t2.continentlist

timeline_data = {}
response_data = {}
country_wise_news = {}
news_countryList = []
covid_word_dictionary = []

current_year = 0
response     = 0
countryNews  = 0
countryNews_country = ""
countryNews_year = 2020


# lexical analyzer
tokens = (
            'LI',
            'TIMELINE_LINK',
            'RESPONSE_LINK',
            'ANCHOR',
            'DAILYNEWSCLOSE',
            'DAILYNEWSCLOSEXTRA',
            'COUNTRY_TIMELINE_LINK',
            'COUNTRY_TIMELINEXTRA_LINK',
            'COUNTRY_TIMELINEG_LINK',
            'COUNTRYNEWSCLOSE',
            'COUNTRYNEWSCLOSEH2',
            'COUNTRYNEWSCLOSEXTRA',
            'COUNTRYNEWSMONTHCLOSE',
            'COUNTRYNEWSMONTHCLOSEXTRA',
            'COUNTRYNEWSMONTHCLOSEH2',
            'ALL'
          )


# TOKEN DEFINITION
t_LI                        =   r'''<li>+'''
t_TIMELINE_LINK             =   r'''<a\shref="\/wiki\/Timeline_of_the_COVID-19_pandemic_in_+[\w]+_[\d]+"\stitle="[\w\d\s -]+">'''
t_COUNTRY_TIMELINE_LINK     =   r'''<a\shref="\/wiki\/Timeline_of_the_COVID-19_pandemic_in_[\w]+"\stitle="[\w\d\s -]+">'''
t_COUNTRY_TIMELINEXTRA_LINK =   r'''<a\shref="\/wiki\/Timeline_of_the_COVID-19_pandemic_in_[\w]+_\([\w\d\%\_]+\)"\stitle="[\w\s\d \-()–]+">'''
t_COUNTRY_TIMELINEG_LINK    =   r'''<a\shref="\/wiki\/Timeline_of_the_COVID-19_pandemic_in_[\w]+_\([\w\d\%\_]+\)"\sclass="mw-redirect"\stitle="[\w\s\d \-()–]+">'''
t_RESPONSE_LINK             =   r'''<a\shref="\/wiki\/Responses_to_the_COVID-19_pandemic_in_[\w]+_[\d]+"\stitle="[\w\d\s -]+">'''
t_ANCHOR                    =   r'''<\/a>'''
t_ALL						= 	r'''[\d\w() -.'\/\"()–\s\$]+'''
t_DAILYNEWSCLOSE            =   r'''[\d]+\s[\w]+<\/span>(.*?)\s<h3>'''
t_DAILYNEWSCLOSEXTRA        =   r'''[\d]+\s[\w]+<\/span>(.*?)\s<h2>'''
t_COUNTRYNEWSCLOSE          =   r'''[\w\s\d,–]+\s[\d]+<\/span></h3>\s(.*?)\s<h3>'''
t_COUNTRYNEWSCLOSEH2        =   r'''[\w]+\s[\d]+<\/span></h2>\s(.*?)\s<h2>'''
t_COUNTRYNEWSCLOSEXTRA      =   r'''[\w]+\s[\d]+<\/span></h3>\s(.*?)\s<h2>'''
t_COUNTRYNEWSMONTHCLOSE     =   r'''(January|February|March|April|May|June|July|August|September|October|November|December|january|february|march|april|may|june|july|august|september|october|november|december)+<\/span></h3>\s(.*?)\s<h3>'''
t_COUNTRYNEWSMONTHCLOSEXTRA =   r'''(January|February|March|April|May|June|July|August|September|October|November|December|january|february|march|april|may|june|july|august|september|october|november|december)+<\/span></h3>\s(.*?)\s<h2>'''
t_COUNTRYNEWSMONTHCLOSEH2   =   r'''(January|February|March|April|May|June|July|August|September|October|November|December|january|february|march|april|may|june|july|august|september|october|november|december)+<\/span></h2>\s(.*?)\s<h2>'''
t_ignore_COMMENT            =   r'\#.*'
t_ignore                    =   ' \t'    # ignores spaces and tabs

def t_error (t):
#   print("Illegal character '%s'" % t.value[0])
    t.lexer.skip(1)

def p_start(p):
    '''Start : S1
            |  S2
            |  S3
            |  S4
            |  S5
            '''

def p_timeline_data_Link(p):
    'S1 : LI TIMELINE_LINK ALL ANCHOR '
    timeline_Wiki_Links(p[2],p[3])

def p_response_data_Link(p):
    'S2 : LI RESPONSE_LINK ALL ANCHOR '
    reponse_Wiki_Links(p[2],p[3])

def p_daily_month_news(p):
    '''S3 : DAILYNEWSCLOSE
    |   DAILYNEWSCLOSEXTRA
        '''
    # print(p[1])
    if countryNews == 0:
        store_daily_news(current_year,response,p[1])


def p_country_timeline_data_Link(p):
    '''S4 : LI COUNTRY_TIMELINE_LINK ALL ANCHOR
     | LI COUNTRY_TIMELINEXTRA_LINK ALL ANCHOR
     | LI COUNTRY_TIMELINEG_LINK ALL ANCHOR'''
    country = p[3]
    if "(" in country:
        country = country.split("(")[0]
    if "," in country:
        country = country.split(",")[0]
    country = country.strip()
    if(country == "Republic of Ireland"):
        country = "Ireland"
    if country in news_countryList:
        if country not in country_wise_news:
            country_wise_news[country] = {}
        mainhref = "https://en.wikipedia.org"
        if "timeline_link" not in country_wise_news[country]:
            country_wise_news[country]["timeline_link"] = []
        country_wise_news[country]["timeline_link"].append(mainhref + p[2].split('"')[1])

def p_country_news(p):
    '''S5 : COUNTRYNEWSCLOSE
        |   COUNTRYNEWSCLOSEH2
        |   COUNTRYNEWSCLOSEXTRA
        |   COUNTRYNEWSMONTHCLOSE
        |   COUNTRYNEWSMONTHCLOSEXTRA
        |   COUNTRYNEWSMONTHCLOSEH2
        '''
    if countryNews == 1:
        store_country_daily_news(countryNews_year,p[1])



def p_error(p):
    pass

def timeline_Wiki_Links(link,dateYear):
    month = dateYear.split(" ")[0]
    year = dateYear.split(" ")[1]
    mainhref = "https://en.wikipedia.org"
    href = mainhref + link.split('"')[1]

    if year in timeline_data:
        if month in year:
            timeline_data[year][month]["timeline_link"] = href
        else:
            timeline_data[year][month] = {}
            timeline_data[year][month]["timeline_link"] = href
    else:
        timeline_data[year] = {}
        timeline_data[year][month] = {}
        timeline_data[year][month]["timeline_link"] = href


def reponse_Wiki_Links(link,dateYear):
    month = dateYear.split(" ")[0]
    year = dateYear.split(" ")[1]
    mainhref = "https://en.wikipedia.org"
    href = mainhref+link.split('"')[1]

    if year in response_data:
        if month in year:
            response_data[year][month]["reponse_link"] = href
        else:
            response_data[year][month] = {}
            response_data[year][month]["reponse_link"] = href
    else:
        response_data[year] = {}
        response_data[year][month] = {}
        response_data[year][month]["reponse_link"] = href

def refinet_date_data(dailyNews):

    dailyNews = re.sub(r'<style.*?>.*?</style>', '', dailyNews)
    dailyNews = re.sub(r'<div\sclass="thumbinner.*?>.*?</div>', '', dailyNews)
    dailyNews = re.sub(r'<a.*?>', '', dailyNews)
    dailyNews = re.sub(r'</a>', '', dailyNews)
    # dailyNews = re.sub(r'</span>', '</sn>', dailyNews)
    # dailyNews = re.sub(r'<a.*?>.*?</a>', '', dailyNews)
    dailyNews = re.sub(r'<td class="bb-c">.*?</td>', '', dailyNews)
    dailyNews = re.sub(r'<span id=[\w\d_."]+><\/span>', '', dailyNews)
    # dailyNews = re.sub(r'<tr.*?>.*?</tr>', '', dailyNews)
    dailyNews = re.sub(r'<span class="mw-editsection"><span class="([a-zA-Z]+(-[a-zA-Z]+)+)"(?:[^"]|"")*"([a-zA-Z]+(-[a-zA-Z]+)+)">]</span></span>', '', dailyNews)
    dailyNews = re.sub(r'<span class="[\w\d-]+"><span class="[\w\d-]+">\[<\/span><a href=["/\d\w.?=(%)&;\s: – -]+>[\w]+<\/a><span class="[\w\d-]+">]<\/span>', '', dailyNews)
    dailyNews = re.sub(r'<div\stitle=".*?>.*?<\/div>', '', dailyNews)
    dailyNews = re.sub(r'<table>\s<caption\s[\s\w=\d"->]+<\/table>', '', dailyNews)
    # dailyNews = re.sub(r'<table[\s\w=\d"->]+>[\s\w=\d"->]+<\/table>', '', dailyNews)
    dailyNews = re.sub(r'<div id="[\s\w=\d"-]+>.*?</div>', '', dailyNews)
    dailyNews = re.sub(r'<div class="[\s\w=\d"-]+>.*?</div>', '', dailyNews)
    dailyNews = re.sub(r'<div\s[\s\w\d"=:;()+.-]+>', '', dailyNews)
    dailyNews = re.sub(r'<sup.*?></sup>', '', dailyNews)
    dailyNews = re.sub(r'</div>', '', dailyNews)
    dailyNews = re.sub(r'<li class="toclevel[\s\w=\d"-]+><\/li>', '', dailyNews)
    dailyNews = re.sub(r'<b>', '', dailyNews)
    dailyNews = re.sub(r'</b>', '', dailyNews)
    dailyNews = re.sub(r'<i>', '', dailyNews)
    dailyNews = re.sub(r'</i>', '', dailyNews)
    dailyNews = re.sub(r'<ul><li>', '', dailyNews)
    # dailyNews = re.sub(r'<li>', '', dailyNews)
    dailyNews = re.sub(r'<h4><span class="mw-headline" id="[\d\w]+">', '', dailyNews)
    dailyNews = re.sub(r'<link[\s\w\r=:"-]+\/>', '', dailyNews)
    dailyNews = re.sub(r'<sup\s[\d\w\s=".:-]+>[\d\w\s&#;]+<\/sup>', '', dailyNews)

    return dailyNews

def refine_data(dailyNews):

    dailyNews = re.sub(r'<sup.*?>.*?</sup>', '', dailyNews)
    dailyNews = re.sub(r'<span.*?>.*?</span>', '', dailyNews)
    dailyNews = re.sub(r'<h2>.*?</h2>', '', dailyNews)
    dailyNews = re.sub(r'<h3>', '', dailyNews)
    dailyNews = re.sub(r'<h2>', '', dailyNews)
    dailyNews = re.sub(r'<a.*?>', '', dailyNews)
    dailyNews = re.sub(r'</a>', '', dailyNews)
    dailyNews = re.sub(r'<ul>', '', dailyNews)
    dailyNews = re.sub(r'</ul>', '', dailyNews)
    dailyNews = re.sub(r'<li>', '', dailyNews)
    dailyNews = re.sub(r'<div.*?>.*?</div>', '', dailyNews)
    dailyNews = re.sub(r'</li>', '\n', dailyNews)

    dailyNews = re.sub(r'<b>', '', dailyNews)
    dailyNews = re.sub(r'</b>', '', dailyNews)
    dailyNews = re.sub(r'<i>', '', dailyNews)
    dailyNews = re.sub(r'</i>', '', dailyNews)
    dailyNews = re.sub(r'<p>', '', dailyNews)
    dailyNews = re.sub(r'</p>', '\n', dailyNews)

    return dailyNews

def store_daily_news(current_year,response,news):
    dateMonth = news.split("</span>")[0]
    month = dateMonth.split(" ")[1]

    dailyNews = news[(len(dateMonth)+7):]
    if "</h3>" in dailyNews:
        dailyNews = dailyNews.split("</h3>")[1]
    if "<p>" in dailyNews:
        dailyNews = dailyNews.partition("<p>")[2]
    dailyNews = refine_data(dailyNews)

    if response == 0:
        if dateMonth in  timeline_data[current_year][month] :
            timeline_data[current_year][month][dateMonth].append(dailyNews)
        else:
            timeline_data[current_year][month][dateMonth] = []
            timeline_data[current_year][month][dateMonth].append(dailyNews)
    if response == 1:
        if  month in response_data[current_year]:
            if dateMonth in  response_data[current_year][month] :
                response_data[current_year][month][dateMonth].append(dailyNews)
            else:
                response_data[current_year][month][dateMonth] = []
                response_data[current_year][month][dateMonth].append(dailyNews)
        else:
            response_data[current_year][month] = {}
            response_data[current_year][month][dateMonth] = []
            response_data[current_year][month][dateMonth].append(dailyNews)

def store_country_daily_news(current_year,news):
    global countryNews_year

    news = re.sub(r'</span></h4>', '', news)
    news = re.sub(r'</ul>', '', news)
    # news = re.sub(r'</li> <li>', '', news)
    news = re.sub(r'<h3>', '', news)
    news = re.sub(r'</h3>', '', news)
    news = re.sub(r'<p>', '', news)
    news = re.sub(r'&amp;', '', news)
    news = re.sub(r'"', '', news)

    dateMonth = news.partition("</span>")[0]
    dailyNews = news.partition("</span>")[2]
    if " " in dateMonth:
        month = dateMonth.split(" ")[0]
        year  = dateMonth.split(" ")[1]
        year  = year.strip()
        if ',' in year:
            year = dateMonth.split(",")[1]
            year = year.strip()
        if '–' in year:
            year = current_year
    else:
        month = dateMonth
        year  = current_year

    if month == 'December':
        countryNews_year = str(int(year) + 1)
    else:
        countryNews_year = year

    monthArray = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
    monthLowerCaseArray = ['january', 'february', 'march', 'april', 'may', 'june', 'july', 'august', 'september', 'october', 'november', 'december']

    newsByDate = re.findall(r'''([0-9]+\s+January|[0-9]+\s+February|[0-9]+\s+March|[0-9]+\s+April|[0-9]+\s+May|[0-9]+\s+June|[0-9]+\s+July|[0-9]+\s+August|[0-9]+\s+September|[0-9]+\s+October|[0-9]+\s+November|[0-9]+\s+December|[0-9]+\s+january|[0-9]+\s+february|[0-9]+\s+march|[0-9]+\s+april|[0-9]+\s+may|[0-9]+\s+june|[0-9]+\s+july|[0-9]+\s+august|[0-9]+\s+september|[0-9]+\s+october|[0-9]+\s+november|[0-9]+\s+december|January+\s+[0-9]{1,2}|February+\s+[0-9]{1,2}|March+\s+[0-9]{1,2}|April+\s+[0-9]{1,2}|May+\s+[0-9]{1,2}|June+\s+[0-9]{1,2}|July+\s+[0-9]{1,2}|August+\s+[0-9]{1,2}|September+\s+[0-9]{1,2}|October+\s+[0-9]{1,2}|November+\s+[0-9]{1,2}|December+\s+[0-9]{1,2}|january+\s+[0-9]{1,2}|february+\s+[0-9]{1,2}|march+\s+[0-9]{1,2}|april+\s+[0-9]{1,2}|may+\s+[0-9]{1,2}|june+\s+[0-9]{2}|july+\s+[0-9]{1,2}|august+\s+[0-9]{1,2}|september+\s+[0-9]{1,2}|october+\s+[0-9]{1,2}|november+\s+[0-9]{1,2}|december+\s[0-9]{1,2})+(.*?)<''',dailyNews)

    if year not in country_wise_news[countryNews_country]:
        country_wise_news[countryNews_country][year] = {}
        if '–' in month:
            month1 = month.split("–")[0]
            month1 = month1.strip()
            month2 = month.split("–")[1]
            month2 = month2.strip()
            country_wise_news[countryNews_country][year][month1] = {}
            country_wise_news[countryNews_country][year][month2] = {}
        else:
            country_wise_news[countryNews_country][year][month] = {}
        # country_wise_news[countryNews_country][year][month] = {}
    else:
        if month not in country_wise_news[countryNews_country][year]:
            if '–' in month:
                month1 =  month.split("–")[0]
                month1 = month1.strip()
                month2 = month.split("–")[1]
                month2 = month2.strip()
                country_wise_news[countryNews_country][year][month1] = {}
                country_wise_news[countryNews_country][year][month2] = {}
            else:
                country_wise_news[countryNews_country][year][month] = {}

    if newsByDate != []:
        for news in newsByDate:
            if news[1].count(' ') > 2:
                month_date = news[0]
                curr_month = news[0].split(" ")[1]
                if(news[0].split(" ")[0] in  monthLowerCaseArray):
                    month_index = monthLowerCaseArray.index(news[0].split(" ")[0])
                    curr_month = monthArray[month_index]
                    month_date =  news[0].split(" ")[1]+" "+monthArray[month_index]
                elif (news[0].split(" ")[0] in monthArray ):
                    month_date = news[0].split(" ")[1] + " " + news[0].split(" ")[0]
                    curr_month = news[0].split(" ")[0]
                elif (news[0].split(" ")[1] in monthLowerCaseArray ):
                    month_index = monthLowerCaseArray.index(news[0].split(" ")[1])
                    curr_month = monthArray[month_index]
                    month_date =  news[0].split(" ")[0] + " " + monthArray[month_index]

                #news insertion
                if curr_month in country_wise_news[countryNews_country][year]:
                    if month_date not in country_wise_news[countryNews_country][year][curr_month]:
                        country_wise_news[countryNews_country][year][curr_month][month_date] = []
                    country_wise_news[countryNews_country][year][curr_month][month_date].append(news[1])


                # if curr_month not in country_wise_news[countryNews_country][year]:
                #     if monthArray.index(curr_month) < 6 and year != "2022":
                #         country_wise_news[countryNews_country][year][curr_month] = {}
                #         if month_date not in country_wise_news[countryNews_country][year][curr_month]:
                #             country_wise_news[countryNews_country][year][curr_month][month_date] = []
                #         country_wise_news[countryNews_country][year][curr_month][month_date].append(news[1])
                # else:
                #     if monthArray.index(curr_month) < 6 and year != "2022":
                #         if month_date not in country_wise_news[countryNews_country][year][curr_month]:
                #             country_wise_news[countryNews_country][year][curr_month][month_date] = []
                #         country_wise_news[countryNews_country][year][curr_month][month_date].append(news[1])


def getPart(data,delim,delim_before):
    data = data.partition(delim)[2]
    data = data.split(delim_before)[0]
    return data

def parseMonthNews(url,page,type):

    if not os.path.exists("./HTML/" + type):
        os.mkdir("./HTML/" + type)

    content = get_wiki_content(url)
    main_path = "./HTML/" + type + "/" + page + ".html"
    if not os.path.isfile(main_path):
        with open(os.path.join(os.path.dirname(__file__), main_path), 'w') as input_file:
            input_file.write(content)
            input_file.close()

    delim = ""
    delim_before = ""
    if(type == "Timeline"):
        delim = '<h2><span class="mw-headline" id="Pandemic_chronology">'
        delim_before = '<span class="mw-headline" id="Summary">'
    elif(type == "Response"):
        delim = '</ul> </div> <h2><span'
        delim_before = '<span class="mw-headline" id="See_also">'
    elif(type == "Country_Timeline"):
        delim = '<body class="mediawiki '
        delim_before = '<span class="mw-headline" id="References">References'

    data = getPart(content, delim, delim_before)
    return data

def parse_wiki(data):
    global current_year
    global response
    global countryNews
    global countryNews_country
    global countryNews_year
    delim = 'The following are the timelines of the COVID-19 pandemic respectively in: '
    delim_before = '<dl><dt>Responses</dt></dl>'
    news = getPart(data, delim, delim_before)
    lexer = lex.lex()
    parser = yacc.yacc()
    lexer.input(news)
    parser.parse(news)

    for year in timeline_data:
        for month in timeline_data[year]:
            page = year+"_"+month+"_Wiki_Timeline"
            month_news = parseMonthNews(timeline_data[year][month]["timeline_link"],page,"Timeline")
            current_year = year
            lexer.input(month_news)
            parser.parse(month_news)

    delim = '<dl><dt>Responses</dt></dl>'
    delim_before = '<h2><span class="mw-headline" id="Timeline_by_country">Timeline by country'
    response = getPart(data, delim, delim_before)
    parser.parse(response)
    response = 1
    for year in response_data:
        for month in response_data[year]:
            page = year+"_"+month+"_Wiki_Timeline"
            if "reponse_link" in response_data[year][month]:
                month_response = parseMonthNews(response_data[year][month]["reponse_link"],page,"Response")
                current_year = year
                lexer.input(month_response)
                parser.parse(month_response)

    delim = '<h2><span class="mw-headline" id="Timeline_by_country">'
    delim_before = '<h2><span class="mw-headline" id="Worldwide_cases_by_month_and_year">'
    infomarionbycountry = getPart(data, delim, delim_before)
    parser.parse(infomarionbycountry)
    response = 0

    countryNews = 1
    for country in country_wise_news:
        if country == 'Canada':
            countryNews_year = 2019
        else:
            countryNews_year = 2020
        countryNews_country = country
        for link in country_wise_news[country]["timeline_link"]:
            indx = country_wise_news[country]["timeline_link"].index(link)
            page = country+"_"+str(indx)+"_country_Timeline"
            month_news = parseMonthNews(link,page,"Country_Timeline")
            month_news = refinet_date_data(month_news)
            if country == "Pakistan" or country == "India" or country == "Turkey" or country == "Australia":
                month_news = re.sub(r'<h3><span class="mw-headline" id="[\w\d_]+">', '', month_news)
                month_news = re.sub(r'<\/span><\/h3>', '', month_news)
                month_news = re.sub(r'<\/span><\/li>', '', month_news)
            lexer.input(month_news)
            parser.parse(month_news)

def get_wiki_content(url):
    req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    web_byte = urlopen(req).read()
    html_text = web_byte.decode('utf-8')
    html_text = re.sub("\s+", " ", html_text)

    return html_text

def checkOptionNo(element,lenth):
    try:
        if(int(element) and int(element) <= lenth):
            return True
        else:
            return False
    except ValueError:
        return False

#Choose a country name for further queries
def countryChoiceList(menuChoice,subMenuChoice):
    countryListLowerCase = []
    for option_reg in news_countryList:
        countryListLowerCase.append(option_reg.lower())

    print(" ---------------------------")
    print("       Country List         ")
    print(" ---------------------------")
    for (i, option) in enumerate(news_countryList, start=1):
        print("|   {}. {}".format(i, option))
    print(" ---------------------------")

    while (1):
        option_no = input("\nEnter Country name/no (Enter (back) for going back):\n")

        if (option_no == "back"):
            break
        elif (checkOptionNo(option_no, len(news_countryList))):
            country_name = news_countryList[int(option_no) - 1]
            # print(country_name)
            if menuChoice == 7 :
                countryNewsDuration(country_name)
            elif menuChoice == 8 :
                countryNewsInformation(country_name)
            elif menuChoice == 9:
                countryNewsJaccardSimilarity(country_name,subMenuChoice)
        elif (option_no in news_countryList):
            country_name = option_no
            # print(country_name)
            if menuChoice == 7 :
                countryNewsDuration(country_name)
            elif menuChoice == 8:
                countryNewsInformation(country_name)
            elif menuChoice == 9:
                countryNewsJaccardSimilarity(country_name,subMenuChoice)
        elif (option_no in countryListLowerCase):
            country_name = news_countryList[countryListLowerCase.index(option_no)]
            # print(country_name)
            if menuChoice == 7 :
                countryNewsDuration(country_name)
            elif menuChoice == 8:
                countryNewsInformation(country_name)
            elif menuChoice == 9:
                countryNewsJaccardSimilarity(country_name,subMenuChoice)
        else:
            print("Invalid option.\n")

#Given a country name, show the date range for which news information is available for that country.
def countryNewsDuration(country):
    monthArray = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October',
                  'November', 'December']
    startYear = 0
    endYear = 0
    startMonth = ""
    endMonth = ""
    for year in country_wise_news[country]:
        if (year != "timeline_link"):
            for month in country_wise_news[country][year]:
                if (startMonth == "" and startYear == 0 ) or (monthArray.index(startMonth) > monthArray.index(month) and startYear == int(year)) or ( startYear > int(year)):
                    startMonth = month
                    startYear = int(year)
                if (endMonth == "" and endYear == 0 ) or (monthArray.index(endMonth) < monthArray.index(month) and endYear == int(year)) or (endYear < int(year)):
                    endMonth = month
                    endYear = int(year)
    print(f' {country} :  ({startMonth},{startYear} - {endMonth},{endYear}) \n')

#Given a country name and date range, extract all the news between the time duration,plot a word cloud.
def countryNewsInformation(country):
    monthArray = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October',
                  'November', 'December']

    startDate = input("Start Date(Format 01-01-2022):")
    endDate = input("End Date(Format 01-01-2022):")
    news_corpus = []

    (val, startdateValue, enddateValue) = dateRange(startDate, endDate)
    if (val == 0):
        print("Wrong Date Format! Try again.")
    else:
        print("\n")
        print(f' {country} ({startDate} to {endDate}) :\n')
        for year in country_wise_news[country]:
            if ( year != "timeline_link"):
                for month in country_wise_news[country][year]:
                    year_month_sorted = sorted(country_wise_news[country][year][month], key=sort_date)
                    for dateMonth in year_month_sorted:
                        mn = monthArray.index(dateMonth.split(" ")[1]) + 1
                        dt = dateMonth.split(" ")[0]
                        currVal = int(year) * 10000 + int(mn) * 100 + int(dt)
                        if (startdateValue <= currVal and currVal <= enddateValue):
                            print("{},{}".format(dateMonth, year))
                            for news in country_wise_news[country][year][month][dateMonth]:
                                news_corpus.append(news)
                                print(news)
        comment_words = ''
        stopwordset = set(STOPWORDS)
        getCovidWordDictionary()

        # iterate through the corpus
        for val in news_corpus:
            # typecaste each val to string
            val = str(val)
            # split the value
            tokens = val.split()
            # Converts each token into lowercase
            for i in range(len(tokens)):
                tokens[i] = tokens[i].lower()
            comment_words += " ".join(tokens) + " "

        wordcloud = WordCloud(width=800, height=800,
                              background_color='white',
                              stopwords=stopwordset,
                              min_font_size=10).generate(comment_words)

        plt.figure(figsize=(8, 8), facecolor=None)
        plt.imshow(wordcloud)
        plt.gca().set_title('WORD CLOUD')
        plt.axis("off")
        plt.tight_layout(pad=0)

        plt.show()

def dateRange(startDate,endDate):
    value=0
    startdateIndex = 0
    enddateIndex = 0

    try:
        if(startDate.count('-') == 2 and endDate.count('-') == 2):
            startDate = startDate.split('-')
            startD = datetime.datetime(int(startDate[2]), int(startDate[1]), int(startDate[0]))
            startdateVal = startD.strftime("%d %b")
            endDate = endDate.split('-')
            endD = datetime.datetime(int(endDate[2]), int(endDate[1]), int(endDate[0]))
            endDateVal  = endD.strftime("%d %b")

            startdateIndex = int(startDate[2])*10000+int(startDate[1])*100+ int(startDate[0])
            enddateIndex =  int(endDate[2])*10000+int(endDate[1])*100+ int(endDate[0])

            if ( startdateIndex <= enddateIndex):
                value = 1
            else:
                print("Invalid Range.")
    except:
        value=0
    return (value,startdateIndex,enddateIndex)

def sort_date(elem):
    if  (elem != "reponse_link" and elem != "timeline_link" ):
        return int(elem.split(" ")[0])
    else:
        return 0

#(given a time range as input, including start & end date)-
# Show all the worldwide news between the time range.
# Show all the worldwide responses between the time range
def showNews(optionValue):

    monthArray = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']

    startDate = input("Start Date(Format 01-01-2022):")
    endDate = input("End Date(Format 01-01-2022):")

    (val, startdateValue, enddateValue) = dateRange( startDate, endDate)
    if (val == 0):
        print("Wrong Date Format! Try again.")
    else:
        print("\n")
        for year in optionValue:
            for month in optionValue[year]:
                year_month_sorted =  sorted(optionValue[year][month], key = sort_date)
                for dateMonth in year_month_sorted:
                    if (dateMonth != "reponse_link" and dateMonth != "timeline_link" ):
                        mn = monthArray.index(dateMonth.split(" ")[1])+1
                        dt = dateMonth.split(" ")[0]
                        currVal = int(year)*10000+int(mn)*100+ int(dt)
                        if(startdateValue <= currVal and currVal <= enddateValue):
                            print("{},{}".format(dateMonth, year))
                            for news in optionValue[year][month][dateMonth]:
                                print(news)

#Crawl the Wikipedia Covid-19 timeline page, and answer the user queries
def wikiOptions():

    while (1):
        print("+-------------------------------------------------------+")
        print("|   Wikipedia Timeline of the COVID-19 pandemic         |")
        print("+-------------------------------------------------------+")
        print("|   1. All the worldwide news                           |")
        print("|   2. All the worldwide responses                      |")
        print("+-------------------------------------------------------+")

        option_no = input("Enter option no (Enter (back) for going back):\n")
        option_no = option_no.strip()


        if (option_no == "back"):
            break
        elif (option_no == '1'):
            option_no = "news"
            showNews(timeline_data)
        elif (option_no == '2'):
            option_no = "responses"
            showNews(response_data)
        else:
            print("Invalid option.\n")



def parseNews():
    url = "http://en.wikipedia.org/wiki/Timeline_of_the_COVID-19_pandemic"
    page = "Wikipedia_pandemic"
    content = get_wiki_content(url)
    main_path = "./HTML/" + page + ".html"
    if not os.path.isfile(main_path):
        with open(os.path.join(os.path.dirname(__file__), main_path), 'w') as input_file:
            input_file.write(content)
            input_file.close()

    parse_wiki(content)


def getNewsCountryList():
    global  news_countryList
    with open("covid_country_list.txt") as f:
        content = f.readlines()
    news_countryList = [x.strip() for x in content]

def getCovidWordDictionary():
    global covid_word_dictionary
    with open("covid_word_dictionary.txt") as f:
        content = f.readlines()
    covid_word_dictionary = [x.strip() for x in content]

def checkOverlapping(startDate, endDate,startDateSec, endDateSec):
    overlapping=0
    startdateIndex = 0
    enddateIndex = 0
    startDateSecIndex = 0
    endDateSecIndex = 0

    try:
        if(startDate.count('-') == 2 and endDate.count('-') == 2):
            startDate = startDate.split('-')
            endDate = endDate.split('-')
            startDateSec = startDateSec.split('-')
            endDateSec = endDateSec.split('-')

            startdateIndex = int(startDate[2])*10000+int(startDate[1])*100+ int(startDate[0])
            enddateIndex =  int(endDate[2])*10000+int(endDate[1])*100+ int(endDate[0])

            startDateSecIndex = int(startDateSec[2])*10000+int(startDateSec[1])*100+ int(startDateSec[0])
            endDateSecIndex =  int(endDateSec[2])*10000+int(endDateSec[1])*100+ int(endDateSec[0])

            if ( startdateIndex <= enddateIndex and enddateIndex < startDateSecIndex and startDateSecIndex <= endDateSecIndex):
                overlapping = 1
            else:
                print("Invalid Range.")
    except:
        overlapping=0
        
    return overlapping

# Given two non-overlapping time ranges,
# Plot two different word clouds for all the common words (ignore stopwords) and only covid related common words.
# Print the percentage of covid related words in common words (ignore stopwords).
# Print the top-20 common words (ignore stopwords) and covid related words.
def wordcloud():
    monthArray = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October',
                  'November', 'December']

    print("Input two non overlapping date range.")
    print("First Date Range:")
    startDate = input("Start Date(Format 01-01-2022):")
    endDate = input("End Date(Format 01-01-2022):")

    print('\n')
    print("Second Date Range:")
    startDateSec = input("Start Date(Format 01-01-2022):")
    endDateSec = input("End Date(Format 01-01-2022):")

    corpus = []
    
    overlapping = checkOverlapping(startDate, endDate,startDateSec, endDateSec)

    (val, startdateValue, enddateValue) = dateRange(startDate, endDate)
    (valSec, startdateValueSec, enddateValueSec) = dateRange(startDateSec, endDateSec)
    if (overlapping == 0):
        print("Overlapping Date Range! Try again.")
    elif (val == 0 or valSec == 0):
        print("Wrong Date Format! Try again.")
    else:
        print("\n")
        for year in timeline_data:
            for month in timeline_data[year]:
                year_month_sorted = sorted(timeline_data[year][month], key=sort_date)
                for dateMonth in year_month_sorted:
                    if (dateMonth != "reponse_link" and dateMonth != "timeline_link"):
                        mn = monthArray.index(dateMonth.split(" ")[1]) + 1
                        dt = dateMonth.split(" ")[0]
                        currVal = int(year) * 10000 + int(mn) * 100 + int(dt)
                        if ((startdateValue <= currVal and currVal <= enddateValue) or (startdateValueSec <= currVal and currVal <= enddateValueSec)):
                            for news in timeline_data[year][month][dateMonth]:
                                corpus.append(news)

        comment_words = ''
        stopwordset = set(STOPWORDS)
        getCovidWordDictionary()

        # iterate through the corpus
        for val in corpus:
            # typecaste each val to string
            val = str(val)
            # split the value
            tokens = val.split()
            # Converts each token into lowercase
            for i in range(len(tokens)):
                tokens[i] = tokens[i].lower()
            comment_words += " ".join(tokens) + " "
        if not comment_words:
            print("Not Enough Words ! Try with greater time limit .")
        else:
            text_tokens = comment_words.split(" ")
            tokens_without_sw = [word for word in text_tokens if not word in stopwords.words()]
            tokens_related_covid = [word for word in tokens_without_sw if word in covid_word_dictionary]

            precentage_covid_common = (len(tokens_related_covid) / len(tokens_without_sw)) * 100


            # Print the percentage of covid related words in common words (ignore stopwords).

            print(f'The percentage of covid related words in common words is {precentage_covid_common} %')

            
            # Print the top-20 common words (ignore stopwords) and covid related words.
            common_word = Counter(tokens_without_sw)
            if len(common_word) > 20:
                top_common_words = [word for word, word_count in Counter(common_word).most_common(20)]
                print(f'The top-20 common words {top_common_words}')
            else:
                top_common_words = [word for word, word_count in Counter(common_word).most_common(len(common_word))]
                print(f'The top-20 common words {top_common_words}')

            covid_common_word = Counter(tokens_related_covid)
            if len(covid_common_word) > 20:
                top_covid_common_word = [word for word, word_count in Counter(covid_common_word).most_common(20)]
                print(f'The top-20 common words {top_covid_common_word}')
            else:
                top_covid_common_word = [word for word, word_count in
                                         Counter(covid_common_word).most_common(len(covid_common_word))]
                print(f'The top-20 covid related words {top_covid_common_word}')

            covid_common_words = ' '.join(tokens_related_covid)

            wordcloud = WordCloud(width=800, height=800,
                                  background_color='white',
                                  stopwords=stopwordset,
                                  min_font_size=10).generate(comment_words)

            common_covid_wordcloud = WordCloud(width=800, height=800,
                                               background_color='white',
                                               stopwords=stopwordset,
                                               min_font_size=10).generate(covid_common_words)

            # plot the WordCloud image
            # Plot two different word clouds for all the common words (ignore stopwords) and only covid related common words.
            plt.figure(figsize=(8, 8), facecolor=None)
            plt.imshow(wordcloud)
            plt.gca().set_title('COMMON WORD CLOUD')
            plt.axis("off")
            plt.tight_layout(pad=0)

            plt.figure(figsize=(8, 8), facecolor=None)
            plt.imshow(common_covid_wordcloud)
            plt.gca().set_title('COVID WORD CLOUD')
            plt.axis("off")
            plt.tight_layout(pad=0)

            plt.show()

# Provide names of the top-3 closest countries according to the Jaccard similarity of the extracted news.
# Provide names of the top-3 closest countries according to Jaccard similarity of covid words match.
def jaccard_similarity():

    while (1):
        print("+-------------------------------------------------------+")
        print("|   Jaccard similarity Among Countries                  |")
        print("+-------------------------------------------------------+")
        print("|   1. Country News Based Jaccard similarity            |")
        print("|   2. Covid words match Based Jaccard similarity       |")
        print("+-------------------------------------------------------+")

        option_no = input("Enter option no (Enter (back) for going back):\n")
        option_no = option_no.strip()

        if (option_no == "back"):
            break
        elif (option_no == '1'):
            option_no = "Country News"
            countryChoiceList(9,1)
        elif (option_no == '2'):
            option_no = "Covid words match"
            countryChoiceList(9,2)
        else:
            print("Invalid option.\n")

#Implementation of Jaccard Similarity
def calculate_Jaccard_Similarity(words_doc1, words_doc2):

    jac_sim = 0

    # Find the intersection of words list of doc1 & doc2
    intersection = words_doc1.intersection(words_doc2)

    # Find the union of words list of doc1 & doc2
    union = words_doc1.union(words_doc2)

    if len(intersection) != 0 and len(union) != 0:
        jac_sim  = float(len(intersection)) / len(union)

    return jac_sim

def get_country_news_token(country,startdateValue,enddateValue):
    monthArray = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October',
                  'November', 'December']
    corpus = []

    for year in country_wise_news[country]:
        if (year != "timeline_link"):
            for month in country_wise_news[country][year]:
                year_month_sorted = sorted(country_wise_news[country][year][month], key=sort_date)
                for dateMonth in year_month_sorted:
                    mn = monthArray.index(dateMonth.split(" ")[1]) + 1
                    dt = dateMonth.split(" ")[0]
                    currVal = int(year) * 10000 + int(mn) * 100 + int(dt)
                    if (startdateValue <= currVal and currVal <= enddateValue):
                        for news in country_wise_news[country][year][month][dateMonth]:
                            corpus.append(news)
    comment_words = ''

    # iterate through the corpus
    for val in corpus:
        # typecaste each val to string
        val = str(val)
        # split the value
        tokens = val.split()
        # Converts each token into lowercase
        for i in range(len(tokens)):
            tokens[i] = tokens[i].lower()
        comment_words += " ".join(tokens) + " "
    tokens_without_sw = set()
    tokens_related_covid = set()
    if not comment_words:
        tokens_without_sw = set([])
        tokens_related_covid = set([])
    else:
        text_tokens = comment_words.split(" ")
        tokens_without_sw = set([word for word in text_tokens if not word in stopwords.words()])
        tokens_related_covid = set([word for word in tokens_without_sw if word in covid_word_dictionary])

    return corpus,tokens_without_sw,tokens_related_covid

#Calculate JAccard Similarity between two country
def countryNewsJaccardSimilarity(country_name,subMenuChoice):

    corpus = {}
    tokens_without_sw  = {}
    tokens_related_covid  = {}
    jaccad_smlrty_without_sw = {}
    jaccad_smlrty_related_covid = {}

    startDate = input("Start Date(Format 01-01-2022):")
    endDate = input("End Date(Format 01-01-2022):")

    (val, startdateValue, enddateValue) = dateRange(startDate, endDate)
    if (val == 0):
        print("Wrong Date Format! Try again.")
    else:
        print("\n")
        getCovidWordDictionary()
        stopwordset = set(STOPWORDS)

        corpus_country_name,tokens_without_sw_country_name,tokens_related_covid_country_name = get_country_news_token(country_name, startdateValue, enddateValue)

        for country in news_countryList:
            if country != country_name:
                corpus[country] = []
                tokens_without_sw[country] = set()
                tokens_related_covid[country] = set()
                corpus[country],tokens_without_sw[country],tokens_related_covid[country] = get_country_news_token(country, startdateValue, enddateValue)
                jaccad_smlrty_without_sw[country] = 0
                jaccad_smlrty_without_sw[country] = calculate_Jaccard_Similarity(tokens_without_sw_country_name,tokens_without_sw[country])
                jaccad_smlrty_related_covid[country] = 0
                jaccad_smlrty_related_covid[country] = calculate_Jaccard_Similarity(tokens_related_covid_country_name,tokens_related_covid[country])

        if subMenuChoice == 1:
            # print(jaccad_smlrty_without_sw)
            for country in jaccad_smlrty_without_sw:
                if jaccad_smlrty_without_sw[country] == None:
                    jaccad_smlrty_without_sw[country] = 0
            sorted_jaccad_smlrty_without_sw = sorted(jaccad_smlrty_without_sw.items(), key=lambda x: x[1], reverse=True)
            # print(f'Country News Jaccard Similarity {sorted_jaccad_smlrty_without_sw}')
            print(f'The top-3 closest countries according to Jaccard similarity of Country News ({country_name}):')
            for coun in sorted_jaccad_smlrty_without_sw[0:3]:
                print(coun[0])
        elif subMenuChoice == 2:
            # print(jaccad_smlrty_related_covid)
            for country in jaccad_smlrty_related_covid:
                if jaccad_smlrty_related_covid[country] == None:
                    jaccad_smlrty_related_covid[country] = 0
            sorted_jaccad_smlrty_related_covid = sorted(jaccad_smlrty_related_covid.items(), key=lambda x: x[1], reverse=True)
            # print(f'Covid Match News Jaccard Similarity {sorted_jaccad_smlrty_related_covid}')
            print(f'The top-3 closest countries according to Jaccard similarity of covid words match ({country_name}):')
            for coun in sorted_jaccad_smlrty_related_covid[0:3]:
                print(coun[0])

def main():

    if not os.path.exists("./HTML"):
        os.mkdir("./HTML")

    url = "https://www.worldometers.info/coronavirus/"
    # page = re.search('([^\/])+$', url)
    # page = page.group(0)
    page = "coronavirus"
    content = t1.get_page_content(url)
    main_path = "./HTML/" + page + ".html"
    if not os.path.isfile(main_path):
        with open(os.path.join(os.path.dirname(__file__), main_path), 'w') as input_file:
            input_file.write(content)
            input_file.close()

    all_country_links = t1.extract_all_country_links(content)
    country_dict = t1.get_country_dic()

    for continent in country_dict:
        if not os.path.exists("./HTML/"+continent):
            os.mkdir("./HTML/"+continent)
        for country in country_dict[continent]:
            country_path = "./HTML/"+continent+"/" + country + ".html"
            country_link = t1.get_country_link(all_country_links,country)
            country_url = "https://www.worldometers.info/coronavirus/"+country_link
            country_content = t1.get_page_content(country_url)

            if not os.path.isfile(country_path):
                with open(os.path.join(os.path.dirname(__file__), country_path), 'w') as country_file:
                    country_file.write(country_content)
                    country_file.close()

    page = "coronavirus"

    main_path = "./HTML/" + page + ".html"
    f = open(main_path, "r")
    content = f.read()

    t2.extract_countrylist()
    all_country_links = t1.extract_all_country_links(content)
    for country in countrylist:
        country_links[country] = t1.get_country_link(all_country_links, country)

    t2.read_html(content)
    getNewsCountryList()
    parseNews()

    while (1):
        print(" +-------------------------------------------+")
        print(" | COVID-19 Coronavirus Pandemic Information |")
        print(" +-------------------------------------------+")
        print(" |        1. Country                         |")
        print(" |        2. Continent                       |")
        print(" |        3. World                           |")
        print(" |        4. Query                           |")
        print(" |        5. Wikipedia                       |")
        print(" |        6. Covid Word Cloud                |")
        print(" |        7. Country News Duration           |")
        print(" |        8. Country News Information        |")
        print(" |        9. Jaccard similarity              |")
        print(" +-------------------------------------------+")
        info_type = input("Enter option name/no (Enter (exit) for the exit):\n")
        info_type = info_type.strip()

        if(info_type == "Country" or info_type == "country" or info_type == '1'):
            info_type = "Country"
            t2.optionMenu(countrylist,info_type)

        elif(info_type == "Continent" or info_type == "continent" or info_type == '2'):
            info_type = "Continent"
            t2.optionMenu(continentlist,info_type)

        elif (info_type == "World" or info_type == "world" or info_type == '3'):
            info_type = "World"
            t2.subOptionMenu(info_type,info_type)

        elif (info_type == "Query" or info_type == "query" or info_type == '4'):
            info_type = "Query"

            t2.countryQuery()

        elif (info_type == "Wikipedia" or info_type == "wikipedia" or info_type == '5'):
            info_type = "News"

            wikiOptions()
        elif (info_type == "Covid Word Cloud" or info_type == "Covid Word Cloud" or info_type == '6'):
            info_type = "Covid Word Cloud"

            wordcloud()
        elif (info_type == "Country News Duration" or info_type == "country News Duration" or info_type == '7'):
            info_type = "Country News Duration"

            countryChoiceList(7,0)

        elif (info_type == "Country News Information" or info_type == "country News Information" or info_type == '8'):
            info_type = "Country News Information"

            countryChoiceList(8,0)

        elif (info_type == "Jaccard similarity" or info_type == "jaccard similarity " or info_type == '9'):
            info_type = "Jaccard similarity"

            jaccard_similarity()

        elif(info_type == "exit"):
            break
        else:
            print("Invalid option.\n")

    # logfile.writelines("End!")
    t2.logfile.close()

if __name__=="__main__":
    main()

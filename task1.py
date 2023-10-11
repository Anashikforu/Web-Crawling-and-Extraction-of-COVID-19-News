# ------------------------------------------------------------
#Author: Md Ashik Khan
#ID: 21CS60A02
#Assignment 3 Task 1
# ------------------------------------------------------------
import ply.lex as lex
import ply.yacc as yacc
import requests
import re
import os
import sys

def get_page_content(url):
    r = requests.get(url)
    html_text = r.text
    html_text = re.sub("\s+", " ", html_text)

    return html_text

def extract_all_country_links(content):

    results = re.findall(r'<a class="mt_a" href=".*?">.*?</a>', content)
    return results

def get_country_link(links,country):
    result = ""
    remove_len = len(country)+7
    for country_link in links:
        if(country in country_link):
            result = country_link
            break

    result = re.sub(r'^.*?href="', '', result)
    result = result[:-remove_len]
    result.strip()

    return result

def get_country_dic():

    inputFileName = "worldometers_countrylist.txt"
    with open(inputFileName) as f:
        content = f.readlines()
    content = [x.strip() for x in content]
    continent = ""
    stand = 0
    country_dict = {}

    for country in content:
        if country.endswith(":"):
            country.strip()
            country = country[:-1]
            continent = country
            country_dict[continent] = []
        elif not country:
            stand = 1
        elif country.endswith("-"):
            stand = 0
        elif stand == 1:
            country.strip()
            continent = country
            country_dict[continent] = []
        else:
            country.strip()
            country_dict[continent].append(country)

    return country_dict

def main():
    if not os.path.exists("./HTML"):
        os.mkdir("./HTML")

    url = "https://www.worldometers.info/coronavirus/"
    # page = re.search('([^\/])+$', url)
    # page = page.group(0)
    page = "coronavirus"
    content = get_page_content(url)
    main_path = "./HTML/" + page + ".html"
    if not os.path.isfile(main_path):
        with open(os.path.join(os.path.dirname(__file__), main_path), 'w') as input_file:
            input_file.write(content)
            input_file.close()

    all_country_links = extract_all_country_links(content)
    country_dict = get_country_dic()

    for continent in country_dict:
        if not os.path.exists("./HTML/"+continent):
            os.mkdir("./HTML/"+continent)
        for country in country_dict[continent]:
            country_path = "./HTML/"+continent+"/" + country + ".html"
            country_link = get_country_link(all_country_links,country)
            country_url = "https://www.worldometers.info/coronavirus/"+country_link
            country_content = get_page_content(country_url)

            if not os.path.isfile(country_path):
                with open(os.path.join(os.path.dirname(__file__), country_path), 'w') as country_file:
                    country_file.write(country_content)
                    country_file.close()

            print("download completed ", country_url)

if __name__ == "__main__":
    main()



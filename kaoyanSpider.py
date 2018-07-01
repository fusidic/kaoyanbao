#!usr/bin/python
# -*- coding: utf-8 -*-

import requests
from bs4 import BeautifulSoup
import json
import random
import mysqlWrapper
import getDBInfo
import pymysql


def get_article(link):
    """Get article from the article_link which named in func get_specific_info.

    It is used in func get_specific_info and func get_comm, either of whom has different page css. Though I
    still code like this. It may cause some problem.

    :param link: article link
    :return: article
    :rtype: string
    """
    global article
    try:
        # requests always get the middle page instead of the target page.
        # while len(html) < 500:
        #     print(1)
        html = requests.get(link, headers=hds[random.randint(0, len(hds) - 1)]).content
        soup = BeautifulSoup(html, 'lxml')
        article_pre = soup.select('body > div.waper > div > div.main > div.article > div.articleCon')
        article = article_pre[0].text
    except:
        print("Error:")
    # time = soup.select('body > div.waper > div > div.main > div.article > div.articleInfo > span:nth-of-type(1)')
    return article


# 首页抓取部分用户帖子
def get_comm():
    """Get users personal experience about 'kaoyan', 'xinlu' and 'jingyan' are included.

    :return: comm
    :rtype: dict
    """
    links = ['http://www.kaoyan.com/beikao/xinlu/', 'http://www.kaoyan.com/beikao/jingyan/']
    comm = {}
    for link in links:
        html = requests.get(link, headers=hds[random.randint(0,len(hds)-1)]).content
        soup = BeautifulSoup(html, 'lxml')
        uls = soup.select('body > div.w1000 > div.zsRight > ul')
        for ul in uls:
            for li in ul.select('li'):
                comm_title = li.select('a')[0].text
                comm_link = li.find('a')['href']
                comm_essay = get_comm_essay(comm_link)
                comm[comm_title] = comm_essay
    return comm


def get_comm_essay(link):
    """From comm-link get the essay.

    :param link: comm-link
    :return: essay
    :rtype: str
    """
    essay_html = requests.get(link, headers=hds[random.randint(0, len(hds)-1)]).content
    essay_soup = BeautifulSoup(essay_html, 'lxml')
    essay = essay_soup.select('body > div.waper > div > div.artMian > div.article > div.articleCon')[0].text
    return essay


def get_name(baokao_page="http://www.kaoyan.com/baokao/"):
    school_info = {}
    html = requests.get(baokao_page, headers=hds[random.randint(0,len(hds)-1)]).content
    soup = BeautifulSoup(html, 'lxml')
    uls = soup.select('div.hotCon > ul')
    for ul in uls:
        for li in ul.select('li'):
            school_name = li.find('a')['title']
            school_link = li.find('a')['href']
            school_info[school_name] = school_link
    return school_info


def get_school_dict(name, link):
    """Wrap whole datas in a dict.

    :param name: school name
    :param link: school-page link
    :return: school_dict
    :rtype: dict
    """
    types = {'enrolment_regulation': 'jianzhang', 'major_info': 'zhuanye',
             'reference_book': 'shumu', 'outline': 'dagang', 'grades': 'fenshuxian',
             'rate': 'baolubi'}
    info = get_info(link)
    enrolment_regulation = get_specific_info(name, link, types['enrolment_regulation'])
    major_info = get_specific_info(name, link, types['major_info'])
    reference_book = get_specific_info(name, link, types['reference_book'])
    outline = get_specific_info(name, link, types['outline'])
    grades = get_specific_info(name, link, types['grades'])
    rate = get_specific_info(name, link, types['rate'])
    district = get_district(name)
    school_dict = {'name': name, 'Info': info, 'district': district,
                   'enrolment_regulation': enrolment_regulation,
                   'major_info': major_info, 'reference_book': reference_book,
                   'outline': outline, 'grades': grades, 'rate': rate
                   }
    return school_dict


# 重写了一个内容写入的函数，因为数据库和json结构不一样
def get_content_list(name, link):
    types = {'outline': 'dagang'}
    # types = {'enrolment_regulation': 'jianzhang', 'major_info': 'zhuanye',
    #          'reference_book': 'shumu', 'outline': 'dagang', 'grades': 'fenshuxian',
    #          'rate': 'baolubi'}
    school_name = name
    global sum_input_times
    for sheet_name, info_type in types.items():
        link = link + info_type + "/"
        sheet_name = sheet_name
        html = requests.get(link, headers=hds[random.randint(0, len(hds) - 1)]).content
        soup = BeautifulSoup(html, 'lxml')
        uls = soup.select("body > div.waper > div > div.main > ul.subList")
        part_input_times = 1
        for ul in uls:
            for li in ul.select('li'):
                # time = li.text
                article_link = li.find('a')['href']
                title = li.find('a')['title']
                article_text = get_article(article_link)
                info_dict = getDBInfo.get_content_info_dict(school_name, sheet_name, title, article_text)
                command = mysqlWrapper.gen_content_insert_command(info_dict)
                t = [school_name, sheet_name, part_input_times, sum_input_times]
                print('{0[0]}{0[1]}表单第{0[2]}插入开始，总第{0[3]}次'.format(t))
                print('\n')
                part_input_times += 1
                sum_input_times += 1
                mysqlWrapper.do_content_insert(command)
                print('--------------------------------success--------------------------------------', '\n')


def get_info(link):
    """get school introduce from the school-page.

    checked.

    :param link: school-page
    :return: info
    :rtype: str
    """
    html = requests.get(link, headers=hds[random.randint(0,len(hds)-1)]).content
    soup = BeautifulSoup(html, 'lxml')
    info_link = soup.select("body > div.waper.mt20 > div:nth-of-type(1) "
                            "> div.col300 > div.schoolArea > p.schoolInfo > span")
    info_link = info_link[0].find("a")['href']
    info_html = requests.get(info_link, headers=hds[random.randint(0,len(hds)-1)]).content
    soup_info = BeautifulSoup(info_html, 'lxml')
    info = soup_info.select("body > div.waper > div > div.main > div.article > div.articleCon")[0].text
    return info


def get_specific_info(school, link, info_type):
    """Fetch the 6 parts of informations from school-page.

    Expect three param which indicate 'school name', 'school-page link',
    and the 'type' of the information you want.

    :param school: school name
    :param link: school-page link
    :param info_type: the type of the information
    :return: specific_info
    :rtype: dict
    """
    specific_info = {}
    link = link + info_type + "/"
    html = requests.get(link, headers=hds[random.randint(0,len(hds)-1)]).content
    soup = BeautifulSoup(html, 'lxml')
    uls = soup.select("body > div.waper > div > div.main > ul.subList")
    for ul in uls:
        a = 1
        for li in ul.select('li'):
            # time = li.text
            article_link = li.find('a')['href']
            print(article_link)
            title = li.find('a')['title']
            article_text = get_article(article_link)
            a += 1
            specific_info[title] = article_text
    return specific_info


def get_district(d_name):
    """Get School's District.

    :param d_name: school name
    :rtype: str
    """
    school_map = {'华中地区': {'武汉大学', '华中科技', '中南大学', '河南大学', '湖南大学', '地大武汉', '国防科大',
                           '中南财经', '湖南师大', '武汉理工', '湘潭大学', '中南民族', '郑州大学', '华中师大'},
                  '华东地区': {'复旦大学', '南京大学', '厦门大学', '浙江大学', '上海交大', '同济大学', '清华大学',
                           '华东师大', '山东大学', '华东政法', '华东理工', '石油大学', '中国海洋', '矿大徐州',
                           '厦门大学', '东南大学'},
                  '华北地区': {'北京大学', '人民大学', '中科大', '清华大学', '天津大学'},
                  '其他地区': {'四川大学', '中山大学', '中山大学', '华南理工', '华南师大', '暨南大学', '四川大学',
                           '电子科大', '西安交大', '重庆大学', '广西师大', '西安电子', '第四军医', '西北大学',
                           '广西大学'}
                  }
    district = "null"
    for k, v in school_map.items():
        if d_name in v:
            district = k
    return district


def get_official_link(name, link):
    """Get offical site link of the school.

    :param name: school name
    :param link: school-page link
    :return: official_link
    :rtype: str
    """
    html = requests.get(link, headers=hds[random.randint(0, len(hds) - 1)]).content
    soup = BeautifulSoup(html, 'lxml')
    p = soup.select('body > div.waper.mt20 > div:nth-of-type(1) > div.col300 > div.schoolArea > p.mt5')
    official_link = p[0].find('a')['href']
    return official_link


hds=[{'User-Agent':'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US; rv:1.9.1.6) Gecko/20091201 Firefox/3.5.6'},\
    {'User-Agent':'Mozilla/5.0 (Windows NT 6.2) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.12 Safari/535.11'},\
    {'User-Agent':'Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.2; Trident/6.0)'},\
    {'User-Agent':'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:34.0) Gecko/20100101 Firefox/34.0'},\
    {'User-Agent':'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/44.0.2403.89 Chrome/44.0.2403.89 Safari/537.36'},\
    {'User-Agent':'Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10_6_8; en-us) AppleWebKit/534.50 (KHTML, like Gecko) Version/5.1 Safari/534.50'},\
    {'User-Agent':'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-us) AppleWebKit/534.50 (KHTML, like Gecko) Version/5.1 Safari/534.50'},\
    {'User-Agent':'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Trident/5.0'},\
    {'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.6; rv:2.0.1) Gecko/20100101 Firefox/4.0.1'},\
    {'User-Agent':'Mozilla/5.0 (Windows NT 6.1; rv:2.0.1) Gecko/20100101 Firefox/4.0.1'},\
    {'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_0) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.56 Safari/535.11'},\
    {'User-Agent':'Opera/9.80 (Macintosh; Intel Mac OS X 10.6.8; U; en) Presto/2.8.131 Version/11.11'},\
    {'User-Agent':'Opera/9.80 (Windows NT 6.1; U; en) Presto/2.8.131 Version/11.11'}]


if __name__ == '__main__':
    school_name_and_link = get_name()

    # except_list = {'武汉大学', '东南大学', '华中师大', '天津大学',
    #                '以上大学页面有问题',
    #                '华南理工', '第四军医', '重庆大学', '山东大学', '华中科技',
    #                '武汉理工', '郑州大学', '四川大学', '石油大学', '华东师大',
    #                '广西师大', '上海交大', '中国海洋', '国防科大', '西安交大'}
    # for each_name in school_name_and_link:
    #     if each_name in except_list:
    #         continue
    #     print(each_name + '开始爬取')
    #     ultra_dict = get_school_dict(each_name, school_name_and_link[each_name])
    #     filename = (u"./" + each_name + u".json")
    #     with open(filename, 'w', encoding='utf-8') as json_file:
    #         json.dump(ultra_dict, json_file, ensure_ascii=False)
    #     print(each_name + '完成')

    # mysqlWrapper.do_comm_insert()
    # mysqlWrapper.do_content_insert()
    # info_dict = {'school_name': '上海交大', 'sheet_name': 'major_info', 'title': '123', 'content': '1223'}
    sum_input_times = 1
    for k, v in school_name_and_link.items():
        get_content_list(k, v)


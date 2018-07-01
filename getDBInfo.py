#!usr/bin/python
# -*- coding: utf-8 -*-

import kaoyanSpider


def get_school_info_dict(name, link):
    info_dict = dict()
    info_dict['name'] = name
    info_dict['intro'] = kaoyanSpider.get_info(link)
    info_dict['district'] = kaoyanSpider.get_district(name)
    info_dict['site'] = kaoyanSpider.get_official_link(name, link)
    return info_dict


def get_content_info_dict(school_name, sheet_name, title, content):
    info_dict = dict()
    info_dict['school_name'] = school_name
    info_dict['sheet_name'] = sheet_name
    info_dict['title'] = title
    info_dict['content'] = content
    return info_dict

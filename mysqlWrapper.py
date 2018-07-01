#!/usr/bin/python
# -*- coding: utf-8 -*-


import pymysql
import getDBInfo
import time
import kaoyanSpider


class MySQLWrapper(object):
    """
    数据库操作的封装.
    """
    def __init__(self, command='', *args, **kwargs):
        if command != '':
            conn = self.get_conn()
            try:
                cursor = conn.cursor()
                cursor.execute(command)
            except Exception:
                print('SQL execute error')
            conn.conn_close(conn)

    def get_conn(self):
        conn = pymysql.connect("localhost", "root", "root", "kaoyanboa")
        return conn

    def conn_close(self, conn=None):
        conn.close()

    # def execute(self, command, method_flag=0, conn=None):
    #     cursor = conn.cursor()
    #     # noinspection PyBroadException
    #     try:
    #         if not method_flag:
    #             cursor.execute(command)
    #         else:
    #             cursor.execute(command[0], command[1])
    #         conn.commit()
    #     except Exception:
    #         print('sql execute error!')
    #     return 0


def get_school_key(name):
    command = "select id from school where name = '{}'".format(name)
    db = pymysql.connect("localhost", "root", "root", "kaoyanbao")
    cursor = db.cursor()
    try:
        cursor.execute(command)
        sid = cursor.fetchone()[0]
    except:
        db.rollback()
    db.close()
    return sid


def do_school_insert(name, link):
    command = gen_school_insert_command(getDBInfo.get_school_info_dict(name, link))
    db = pymysql.connect("localhost", "root", "root", "kaoyanbao")
    cursor = db.cursor()
    print(name, "->")
    try:
        cursor.execute(command)
        db.commit()
    except Exception:
        db.rollback()
    db.close()
    print(name, "成功插入")


# def do_enrolment_insert():


def do_comm_insert():
    a = 1
    for k, v in kaoyanSpider.get_comm().items():
        db = pymysql.connect("localhost", "root", "root", "kaoyanbao")
        cursor = db.cursor()
        comm_dict = {'title': k, 'content': v}
        command = gen_comm_insert_command(comm_dict)
        print('第{}条->'.format(a))
        try:
            cursor.execute(command)
            db.commit()
        except Exception:
            db.rollback()
        db.close()
        print('-------------------accomplish-------------------------')
        a += 1


def do_content_insert(command):
    db = pymysql.connect("localhost", "root", "root", "kaoyanbao")
    cursor = db.cursor()
    try:
        cursor.execute(command)
        db.commit()
    except Exception:
        db.rollback()
    db.close()


def gen_comm_insert_command(info_dict):
    info_list = ['title', 'content']
    t = []
    for il in info_list:
        if il in info_dict:
            t.append(info_dict[il])
        else:
            t.append('')
    create_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    t.append(create_time)
    command = (u"INSERT INTO COMM(title, content, create_time, levels, u_id) VALUES "
               u"('{0[0]}', '{0[1]}', '{0[2]}', 2, 1)".format(t))
    return command


def gen_school_insert_command(info_dict):
    """Generate insert sql for school.

    :param info_dict: dict contains with school's information
    :return: command
    :rtype: str
    """
    info_list = ['name', 'intro', 'district', 'site']
    t = []
    for il in info_list:
        if il in info_dict:
            t.append(info_dict[il])
        else:
            t.append('')
    command = (u"INSERT INTO SCHOOL(name, intro, district, site) VALUES "
               u"('{0[0]}', '{0[1]}', '{0[2]}', '{0[3]}')".format(t))
    return command


def gen_content_insert_command(info_dict):
    info_list = ['title', 'content']
    t = [info_dict['sheet_name']]
    for il in info_list:
        if il in info_dict:
            t.append(info_dict[il])
        else:
            t.append('')
    t.append(get_school_key(info_dict['school_name']))
    command = (u"INSERT INTO {0[0]}(title, content, sId) VALUES "
               u"('{0[1]}', '{0[2]}', {0[3]})".format(t))
    return command



import os
import sys
import io
import pymysql
import re

class XMUsql:
    @classmethod
    def del_table(cls, table_name):
        '''
        清空数据表
        '''
        conn = pymysql.connect(host='127.0.0.1', port=3306, user='cxh', passwd='123456', db='xmu_courses', charset='utf8')
        cursor = conn.cursor()
        cursor.execute("truncate table " + table_name)
        conn.commit()
        cursor.close()
        conn.close()


    @classmethod
    def store_rooms(cls, rooms):
        '''
        向classrooms表写入所有教室
        '''
        conn = pymysql.connect(host='127.0.0.1', port=3306, user='cxh', passwd='123456', db='xmu_courses', charset='utf8')
        cursor = conn.cursor()

        sql = "insert into classrooms(room)values(%s)"
        cursor.executemany(sql, rooms)

        conn.commit()
        cursor.close()
        conn.close()


    @classmethod
    def store_courses(cls, courses):
        '''
        向course_info, course_time, course_week表写入所有课程信息
        '''
        conn = pymysql.connect(host='127.0.0.1', port=3306, user='cxh', passwd='123456', db='xmu_courses', charset='utf8')
        cursor = conn.cursor()
        cursor = conn.cursor(cursor=pymysql.cursors.DictCursor)

        sql_info = "insert into course_info(name,day,room)values(%s,%s,%s)"
        sql_time = "insert into course_time(course_id,time)values(%s,%s)"
        sql_week = "insert into course_week(course_id,week)values(%s,%s)"

        for c in courses:
            arg_info = [c['name'], c['day'], c['room']]
            cursor.execute(sql_info, arg_info)
            conn.commit()

            cursor.execute("select id from course_info order by id desc LIMIT 1")
            course_id = cursor.fetchall()[0]['id']

            args_time = []
            st, en = c['times'].split('~')
            for i in range(int(st), int(en) + 1):
                args_time.append([course_id, i])
            cursor.executemany(sql_time, args_time)
            conn.commit()

            args_week = []
            for wkcp in c['weeks'].split(','):
                st_en = re.findall('\d+', wkcp)
                if len(st_en) == 1:
                    args_week.append([course_id, int(st_en[0])])
                else:
                    st, en = st_en[0], st_en[1]
                    if '双' in wkcp:
                        for i in range(int(st), int(en) + 1):
                            if i % 2 == 0:
                                args_week.append([course_id, i])
                    elif '单' in wkcp:
                        for i in range(int(st), int(en) + 1):
                            if i % 2 == 1:
                                args_week.append([course_id, i])
                    else:
                        for i in range(int(st), int(en) + 1):                
                            args_week.append([course_id, i])
            cursor.executemany(sql_week, args_week)
            conn.commit()

        cursor.close()
        conn.close()


    @classmethod
    def get_empty_rooms(cls, week, day, time):
        '''
        查询空教室
        '''
        conn = pymysql.connect(host='127.0.0.1', port=3306, user='cxh', passwd='123456', db='xmu_courses', charset='utf8')
        cursor = conn.cursor()
        cursor = conn.cursor(cursor=pymysql.cursors.DictCursor)

        occupied_rooms = []
        sql = "select room from course_info ci, course_time ct, course_week cw"\
            " where cw.week = {}"\
            " and ci.day = {}"\
            " and ct.time = {}"\
            " and ci.id = cw.course_id"\
            " and ci.id = ct.course_id"\
            .format(week, day, time)
        cursor.execute(sql)
        rows = cursor.fetchall()
        for row in rows:
            occupied_rooms.append(row['room'])

        all_rooms = []
        sql = "select room from classrooms"
        cursor.execute(sql)
        rows = cursor.fetchall()
        for row in rows:
            all_rooms.append(row['room'])

        cursor.close()
        conn.close()

        empty_rooms = list(set(all_rooms) - set(occupied_rooms))
        empty_rooms.sort()

        return empty_rooms


    @classmethod
    def get_empty_rooms2(cls, week, day, time):
        '''
        查询空教室
        '''
        conn = pymysql.connect(host='127.0.0.1', port=3306, user='cxh', passwd='123456', db='xmu_courses', charset='utf8')
        cursor = conn.cursor()
        cursor = conn.cursor(cursor=pymysql.cursors.DictCursor)

        occupied_rooms = []

        if isinstance(time, list):
            sql = "select distinct room from course_info ci, course_time ct, course_week cw"\
            " where cw.week = {}"\
            " and ci.day = {}"\
            " and ct.time >= {}"\
            " and ct.time <= {}"\
            " and ci.id = cw.course_id"\
            " and ci.id = ct.course_id"\
            .format(week, day, time[0], time[1])
        else:
            sql = "select room from course_info ci, course_time ct, course_week cw"\
                " where cw.week = {}"\
                " and ci.day = {}"\
                " and ct.time = {}"\
                " and ci.id = cw.course_id"\
                " and ci.id = ct.course_id"\
                .format(week, day, time)
        cursor.execute(sql)
        rows = cursor.fetchall()
        for row in rows:
            occupied_rooms.append(row['room'])

        all_rooms = []
        sql = "select room from classrooms"
        cursor.execute(sql)
        rows = cursor.fetchall()
        for row in rows:
            all_rooms.append(row['room'])

        cursor.close()
        conn.close()

        empty_rooms = list(set(all_rooms) - set(occupied_rooms))
        empty_rooms.sort()

        return empty_rooms
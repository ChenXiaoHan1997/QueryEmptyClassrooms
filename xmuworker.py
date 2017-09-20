import requests
from scrapy.selector import Selector
import os
import sys
import io
import re
import csv
from xmusql import XMUsql

class XMUworker:
    s = requests.session()
    headers = {'User-agent':'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36'}

    @classmethod
    def crawl_all_courses(cls):
        '''
        抓取网页上所有课程，存入数据库
        '''
        XMUworker.login()
        XMUworker.crawl_html()
        print('已下载网页')
        courses = XMUworker.parse_courses()
        print('已抓取所有课程')
        XMUsql.del_table('course_info')
        XMUsql.del_table('course_time')
        XMUsql.del_table('course_week')
        XMUsql.store_courses(courses)
        print('已将所有课程存入数据库')


    @classmethod
    def read_all_rooms(cls):
        '''
        从本地文件allrooms.txt读取所有教室，存入数据库
        '''
        rooms = []
        with open('all_rooms.txt', 'r', encoding = 'utf-8') as f:
            lines = f.readlines()
            for line in lines:
                rooms.append(line.strip('\n'))
        print('已读取所有教室')
        XMUsql.del_table('classrooms')
        XMUsql.store_rooms(rooms)
        print('已将所有教室存入数据库')


    @classmethod
    def query_empty_rooms(cls, week, day, time):
        '''
        查询某一周、某一天、某一节课的空教室
        '''
        empty_rooms = XMUsql.get_empty_rooms2(week, day, time)
        for r in empty_rooms:
            pass
            print(r)


    @classmethod
    def write_empty_rooms(cls):
        '''
        输出每周、每天的空教室表格
        '''
        for w in range(1, 17):
            for d in range(1, 6):
                with open('results/第{}周/第{}周_星期{}_空教室.csv'.format(w, w, d), 'w') as f:
                    spamwriter = csv.writer(f, dialect = 'excel')
                    for t in range(1, 12):
                        empty_rooms = XMUsql.get_empty_rooms(w, d, t)
                        row = ['第{}节'.format(t)] + empty_rooms
                        spamwriter.writerow(row)
        print('已将空教室写入文件。请查看results目录')


    @classmethod
    def login(cls):
        login_url = 'http://ssfw.xmu.edu.cn/cmstar/userPasswordValidate.portal'
        data = {'Login.Token1':'学号', 
                'Login.Token2':'密码', 
                'goto:http':'//ssfw.xmu.edu.cn/cmstar/loginSuccess.portal', 
                'gotoOnFail:http':'//ssfw.xmu.edu.cn/cmstar/loginFailure.portal'}
        cls.s.post(login_url, data = data, headers = cls.headers)
    
    
    @classmethod
    def crawl_html(cls):
        for i in range(1, 6):
            data = {
                'newSearch': 'true',
                'xnxqdm': '20171',
                'xqdm': '__' + str(i),
                'kszc': '__1',
                'jszc': '__16',
                'xqId': '6',
                'jxlId': '94'
            }
            query_url = 'http://ssfw.xmu.edu.cn/cmstar/index.portal?.p=Znxjb20ud2lzY29tLnBvcnRhbC5zaXRlLmltcGwuRnJhZ21lbnRXaW5kb3d8ZjI2MjR8dmlld3xub3JtYWx8YWN0aW9uPXF1ZXJ5'
            resp = cls.s.post(query_url, data = data, headers = cls.headers)
            with open('html_sources/' + str(i) + '.txt', 'w', encoding = 'utf-8') as f:
                f.write(resp.text)


    @classmethod
    def parse_courses(cls):
        courses = []
        for i in range(1, 6):
            with open('html_sources/' + str(i) + '.txt', 'r', encoding = 'utf-8') as f:
                html = f.read()
                sel = Selector(text = html)
                rows = sel.xpath('//table[@class="portlet-table"]//tr[position()>2]')
                for row in rows:
                    room = row.xpath('.//td[1]/text()').extract()[0]
                    room = room.strip()[-4:]
                    grids = row.xpath('.//td[position()>1]')
                    for grid in grids:
                        if '星期' in grid.extract():
                            name = grid.xpath('./text()').extract()[0].strip()
                            week_time = grid.xpath('./text()').extract()[1].strip()
                            weeks = week_time.split('周')[0].strip('(')
                            times = week_time.split('第')[-1].replace('节)', '')
                            
                            course = {
                                'name': name,
                                'day': i,
                                'weeks': weeks,
                                'times': times,
                                'room': room
                            }
                            courses.append(course)
        return courses


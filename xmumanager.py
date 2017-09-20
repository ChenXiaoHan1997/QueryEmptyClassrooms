import os
import sys
import io
from xmuworker import XMUworker

if __name__=='__main__':

    sys.stdout = io.TextIOWrapper(sys.stdout.buffer,encoding='utf8') #改变标准输出的默认编码

    XMUworker.read_all_rooms()
    XMUworker.crawl_all_courses()
    XMUworker.query_empty_rooms(5, 3, 1)
    XMUworker.write_empty_rooms()

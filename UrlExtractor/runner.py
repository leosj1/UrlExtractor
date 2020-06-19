import os
from scrapy.cmdline import execute

os.chdir(os.path.dirname(os.path.realpath(__file__)))

try:
    execute(
        [
            'scrapy',
            'crawl',
            'catallaxy',
            # '-o',
            # 'Export\\eutimes_2.csv',
        ]
    )
except SystemExit:
    pass
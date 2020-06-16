import os
from scrapy.cmdline import execute

os.chdir(os.path.dirname(os.path.realpath(__file__)))

try:
    execute(
        [
            'scrapy',
            'crawl',
            'eutimes',
            '-o',
            'eutimes_2.csv',
        ]
    )
except SystemExit:
    pass
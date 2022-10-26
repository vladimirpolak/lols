#!/usr/bin/env python
# coding=utf-8

"""sanity check for m3u8downloader

"""

import sys
import logging

from wells.utils import check

from m3u8downloader.config import CONF    # pylint: disable=unused-import
# from m3u8downloader import db

logger = logging.getLogger(__name__)


@check
def check_dumb():
    return True


# @check
# def check_db():
#     with db.get_cursor() as cur:
#         cur.execute(u"""\
# SELECT 1
# """)
#         return cur.fetchone()[0] == 1


def main():
    results = [
        check_dumb(),
        # check_db(),
    ]
    pass_count = len([x for x in results if x])
    fail_count = len(results) - pass_count
    if fail_count:
        logger.error("%s checks passed, %s failed.",
                     pass_count, fail_count)
        sys.exit(fail_count)
    else:
        logger.info("%s checks passed.", pass_count)


if __name__ == '__main__':
    main()

#!/usr/bin/env python3
# coding=utf-8

"""test signal handler and subprocess

"""

import logging
import signal
import subprocess
import sys


logger = logging.getLogger(__name__)


def signal_handler(sig, frame):
    logger.info("Exiting on Ctrl+C...")
    # TODO any threads to stop/kill before calling exit?
    # yes. if ffmpeg command is running, also need to kill that.
    sys.exit(0)


def main():
    logging.basicConfig(
        format='%(asctime)s %(name)s %(levelname)-8s %(message)s',
        level=logging.INFO)
    logger.debug("setup signal_handler for SIGINT")
    signal.signal(signal.SIGINT, signal_handler)

    logger.info("master process running...")
    subprocess.call(["sleep", "60"])


if __name__ == '__main__':
    main()

#-*- coding: utf-8 -*-
import os, re
from os.path import join, exists
from datetime import datetime
from nms import ctx
from nms.utils.console import bold


class Logger(object):

    def __init__(self):
        self.path = path = join(ctx.context['home_path'], 'logs')
        self._timeformat = ctx.settings['log_timeformat']
        self.date = date = datetime.now()
        if not exists(path):
            os.mkdir(path)
        log_file_name = join(
            path, '%d-%d-%d_[%d-%d-%d].log' % (
                date.year, date.month,
                date.day, date.hour,
                date.minute, date.second
            )
        )
        if exists(log_file_name):
            self.log_file = open(log_file_name, 'a')
        else:
            self.log_file = open(log_file_name, 'w')

        # clean 'logs' directory
        self.clean_logs()

    def clean_logs(self):
        """
        Count existing log files.
        If more then 50 log files exist NMS will delete them all.
        """
        log_re = re.compile(
            r'\d{4}-\d{1,2}-\d{1,2}_\[(?:\d{1,2}-){2}\d{1,2}\].log'
        )
        log_counter = 0
        for log in os.listdir(self.path):
            if log_re.match(log):
                log_counter += 1
        if log_counter > 50:
            self.info(bold(
                'The maximum of log files is arrived.'
                ' I\'ll delete all logs!'
            ))
            for log_file in os.listdir(self.path):
                if os.path.isfile(join(self.path, log_file)):
                    os.remove(join(self.path, log_file))


    def debug(self, msg):
        self._log(0, msg)

    def info(self, msg):
        self._log(1, msg)

    def warn(self, msg):
        self._log(2, msg)

    def error(self, msg):
        self._log(3, msg)

    def _log(self, level, msg):
        time = self.date.strftime(self._timeformat)
        level_dict = {
            0: 'DEBUG',
            1: 'INFO',
            2: 'WARNING',
            3: 'ERROR',
        }
        _level = level_dict.get(level)
        output = '%s[%s]\n    %s\n' % (_level, time, msg)
        if level in level_dict.keys():
            if not (level == 0 and not ctx.settings['debug']):
                print output
        self.log_file.write(output)

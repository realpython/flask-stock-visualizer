# -*- coding: UTF-8 -*-
#!/usr/bin/python

import datetime
import re

# from clint.textui import puts, colored
from werckercli.cli import get_term, puts


def store_highest_length(list_lengths, row, props=None):

    if props:
        values_list = props
    else:
        values_list = row

    # print row, props

    for i in range(len(values_list)):

        if props:
            try:
                value = str(row[props[i]])
            except KeyError:
                value = '─'
        else:
            value = str(row[i])

        lines = value.split("\n")

        x_length = 0

        for line in lines:
            if x_length < len(line):
                x_length = len(line)

        x_length += 1

        if x_length > list_lengths[i]:
            list_lengths[i] = x_length

    return list_lengths

    # lines, columns = get_terminal_size()

    # total_length = sum(list_lengths)
    # print total_length


def print_line(list_lengths, row, props=None, line_index=0):

    term = get_term()

    line = u"│ "

    if props:
        values_list = props
    else:
        values_list = row

    more_lines = False

    for i in range(len(values_list)):
        if i > 0:
            line += u"│ "

        if props:
            try:
                value = str(row[props[i]])
            except KeyError:
                value = u'-'
            value = value
        else:
            value = row[i]

        values = value.split("\n")
        if line_index < len(values):
            value = values[line_index]

            if line_index + 1 < len(values):
                more_lines = True
        else:
            value = ""

        value = value.encode("utf-8")

        value = value.ljust(list_lengths[i])
        if value.startswith(u"passed "):
            value = term.green(value)
        elif value.startswith(u"failed "):
            value = term.red(value)

        line += value

    line += u"│"

    puts(line)

    if more_lines:
        print_line(list_lengths, row, props=props, line_index=line_index+1)


def print_hr(lengths, first=False):

    line = u""
    length = len(lengths)
    for i in range(length):

        value = lengths[i]

        if i == 0:
            if first:
                line += u"┌─"
            else:
                line += u"├─"
        else:
            if first:
                line += u"┬─"
            else:
                line += u"┼─"

        line += value * u"─"
        if i == length - 1:
            if first:
                line += u"┐"
            else:
                line += u"┤"
    puts(line)


def format_date(dateString):
    return (datetime.datetime(
        *map(int,
             re.split('[^\d]', dateString)[:-1]
             )
    )).strftime("%x %X")

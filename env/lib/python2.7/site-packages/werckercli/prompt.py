# -*- coding: utf8 -*-

"""
werckercli.prompt
~~~~~~~~~~~~~~~~~~~

Module for simple interactive prompts handling

"""

# from __future__ import absolute_import

from re import match, I


def yn(prompt, default='y', batch=False):
    # A sanity check against default value
    # If not y/n then y is assumed
    if default not in ['y', 'n']:
        default = 'y'

    # Let's build the prompt
    choicebox = '[Y/n]' if default == 'y' else '[y/N]'
    prompt = prompt + ' ' + choicebox + ' '

    # If input is not a yes/no variant or empty
    # keep asking
    while True:
        # If batch option is True then auto reply
        # with default input
        if not batch:
            input = raw_input(prompt).strip()
        else:
            input = ''

        # If input is empty default choice is assumed
        # so we return True
        if input == '':
            if default == 'n':
                return False
            return True

        # Given 'yes' as input if default choice is y
        # then return True, False otherwise
        if match('y(?:es)?', input, I):
            return True

        # Given 'no' as input if default choice is n
        # then return True, False otherwise
        elif match('n(?:o)?', input, I):
            return False


def get_value_with_default(prompt, default):

    value = raw_input(prompt + "(enter=%s): " % default).strip()

    if value == "":
        return default
    else:
        return value

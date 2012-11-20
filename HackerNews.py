#!/usr/bin/python
# -*- coding: utf-8 -*-

import sublime
import sublime_plugin
import os.path
import json
from hn import HackerNews


class OpenHackerNewsCommand(sublime_plugin.WindowCommand):
    def run(self):
        # Open tab:
        view = self.window.new_file()
        
        # Get edit object:
        edit = view.begin_edit()
        
        # Get content:
        hn = HackerNews()
        stories = hn.get_stories()
        
        # Build stories text:
        text = u'HACKER NEWS:\n\n'
        for story in stories['items']:
            print story
            text += "(%d)  %s  - %s\n\n" % (story['points'], story['title'], story['postedBy'])
        
        # Insert text:
        view.insert(edit, 0, text)
        
        # End edit:
        view.end_edit(edit)
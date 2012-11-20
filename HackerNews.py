#!/usr/bin/python
# -*- coding: utf-8 -*-

import sublime
import sublime_plugin

class HackerNews (object):
    
    def get_stories (self):
        return [
            (u'Hello World', 156, 'dotty'),
            (u'Hello World', 156, 'dotty'),
            (u'Hello World', 156, 'dotty'),
            (u'Hello World', 156, 'dotty'),
        ]

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
        for story in stories:
            text += "(%d)  %s  - %s\n\n" % (story[1], story[0], story[2])
        
        # Insert text:
        view.insert(edit, 0, text)
        
        # End edit:
        view.end_edit(edit)
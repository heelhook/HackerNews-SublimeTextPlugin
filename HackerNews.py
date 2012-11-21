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
        view.set_syntax_file('Packages/HackerNews/HackerNews.tmLanguage')
        
        # Get edit object:
        edit = view.begin_edit()
        
        # Get content:
        hn = HackerNews()
        stories = hn.get_stories()
        
        # Get spacing for upvotes:
        largest = 0
        for story in stories['items']:
            if story['points'] > largest:
                largest = story['points']
        
        # Build stories text:
        text = u' Hacker News:'
        for story in stories['items']:
            line = ""
            
            # Add upvotes:
            line += "(%d)" % story['points']
            
            # Add spacing:
            line += " " * int((len(str(largest)) + 1) - len(str(story['points'])))
            
            # Figure out indentation for next line:
            line_indent = len(line)
            
            # Add in headline:
            line += "%s" % (story['title'])
            
            # Comments:
            if story['commentCount'] == 0:
                comments = "discuss"
            elif story['commentCount'] == 1:
                comments = "%d comment" % (story['commentCount'])
            else:
                comments = "%d comments" % (story['commentCount'])
            
            # Add details in below:
            line += "\n" + (" " * line_indent)
            line += "Uploaded by: %s  |  %s" % (story['postedBy'], comments)
            
            # Add to page:
            text += "\n\n" + line
        
        # Insert text:
        view.insert(edit, 0, text)
        
        # End edit:
        view.end_edit(edit)
        view.set_scratch(True)
        view.set_name('Hacker News')
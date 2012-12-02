#!/usr/bin/python
# -*- coding: utf-8 -*-

import sublime
import sublime_plugin
import os.path
import json
from hn import HackerNews
import webbrowser
import re
from MouseEvents import DragSelectCallbackCommand, MouseEventListener


HN_TMLANGUAGE_PATH = 'Packages/HackerNews/HackerNews.tmLanguage'
URL_CACHE = {}


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
            
            # Add URL to cache:
            URL_CACHE[story['title']] = [
                story['url'],
                story['id'],
            ]
            
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
        view.insert(edit, 0, text + "\n")
        
        # End edit:
        view.end_edit(edit)
        view.set_scratch(True)
        view.set_name('Hacker News')


class MouseEventProcessor(MouseEventListener):
    def on_post_mouse_down(self, point, view):
        if view.settings().get('syntax') != HN_TMLANGUAGE_PATH:
            return
        
        region = view.line(point)
        line = view.substr(region)
        
        if re.match('^\(([\d]*)\)([ ]{1,10})(.*)$', line):
            title = re.sub('^\(([\d]*)\)([ ]{1,10})', '', line)
            
            try:
                url = URL_CACHE[title][0]
                
                # Check whether it's an external or HN link:
                foo = "/comments/"
                if url[:len(foo)] == foo:
                    url = "http://news.ycombinator.com/item?id=" + url.replace(foo, '')
                
                webbrowser.open(url)
            except:
                print "HackerNews: couldn't figure out URL"
        
        elif re.match('^([ ]{1,10})Uploaded by:', line):
            word = view.substr(view.word(point)).strip()
            
            if word in ['', ':', '|']:
                return
            elif line.find(word + '  |') > 0:
                webbrowser.open('http://news.ycombinator.com/user?id=' + word)
            elif word[0:7] == 'comment' or word.isdigit() or word == 'discuss':
                # Find line above:
                line_above = view.substr(view.line(region.a - 1))
                comments_title = re.sub('^\(([\d]*)\)([ ]{1,10})', u'', line_above)
                story_id = URL_CACHE[comments_title][1]
                webbrowser.open('http://news.ycombinator.com/item?id=' + str(story_id))
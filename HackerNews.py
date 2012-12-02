#!/usr/bin/python
# -*- coding: utf-8 -*-

import sublime
import sublime_plugin
import os.path
import json
import webbrowser
import re
import urllib2
from MouseEvents import DragSelectCallbackCommand, MouseEventListener


HN_TMLANGUAGE_PATH = 'Packages/HackerNews/HackerNews.tmLanguage'
URL_CACHE = {}


class HackerNews (object):
    def get_stories (self):
        url = 'http://timdavi.es/hackernews/'
        data = urllib2.urlopen(url).read()
        return json.loads(data)


class OpenHackerNewsCommand(sublime_plugin.WindowCommand):
    def run(self):
        # Open tab and set syntax highlighting:
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
        
        # Finish editing the file:
        view.end_edit(edit)
        
        # This tells Sublime that the file doesn't have to be saved when it
        # gets closed, so it doesn't annoy the user:
        view.set_scratch(True)
        
        # Set the tab title:
        view.set_name('Hacker News')


class MouseEventProcessor(MouseEventListener):
    def on_post_mouse_down(self, point, view):
        # Only work on Hacker News pages:
        if view.settings().get('syntax') != HN_TMLANGUAGE_PATH:
            return
        
        # Get the region and the contents of the line that has been selected:
        region = view.line(point)
        line = view.substr(region)
        
        # Check if the point selected is at the very end of the line, which
        # probably means that the user clicked into the whitespace on the right
        # of the line, rather than attempting to click on the link:
        if point == region.b:
            return
        
        # Check whether the user has clicked on the title of the story and if
        # they have, open it up in their webbrowser:
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
        
        # Check whether the user has clicked on the username or the comments
        # link and open the correct page up if they have: 
        elif re.match('^([ ]{1,10})Uploaded by:', line):
            word = view.substr(view.word(point)).strip()
            
            # Discard the click if it was on a space or colon, etc:
            if word in ['', ':', '|']:
                return
            # If the word is before a pipe character, this means it is the
            # username. Bit of a dodgy way of doing it but it works.
            # If it is a username, open the profile up in the user's browser:
            elif line.find(word + '  |') > 0:
                webbrowser.open('http://news.ycombinator.com/user?id=' + word)
            # Check for comments: a digit (i.e. from '67 comments'), the word
            # 'comment' or the word 'discuss'. Open the page up in the user's
            # browser if found:
            elif word[0:7] == 'comment' or word.isdigit() or word == 'discuss':
                # Find line above the line clicked:
                line_above = view.substr(view.line(region.a - 1))
                # Get the title from the line above:
                comments_title = re.sub('^\(([\d]*)\)([ ]{1,10})', u'', line_above)
                # Get the story ID from the URL cache, by looking up the title:
                story_id = URL_CACHE[comments_title][1]
                # Open it up in the default webbrowser:
                webbrowser.open('http://news.ycombinator.com/item?id=' + str(story_id))
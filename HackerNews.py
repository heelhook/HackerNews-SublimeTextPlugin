#!/usr/bin/python
# -*- coding: utf-8 -*-

import sublime
import sublime_plugin
import os.path
import json
from hn import HackerNews
import webbrowser
import re


HN_TMLANGUAGE_PATH = 'Packages/HackerNews/HackerNews.tmLanguage'
URL_CACHE = {}


class DragSelectCallbackCommand(sublime_plugin.TextCommand):
    def run_(self, args):
        for c in sublime_plugin.all_callbacks.setdefault('on_pre_mouse_down',[]):
            c.on_pre_mouse_down(args, self.view)

        #We have to make a copy of the selection, otherwise we'll just have
        #a *reference* to the selection which is useless if we're trying to
        #roll back to a previous one. A RegionSet doesn't support slicing so
        #we have a comprehension instead.
        old_sel = [r for r in self.view.sel()]

        #Only send the event so we don't do an extend or subtract or
        #whatever. We want the only selection to be where they clicked.
        self.view.run_command("drag_select", {'event': args['event']})
        new_sel = self.view.sel()
        click_point = new_sel[0].a

        #Restore the old selection so when we call drag_select in will
        #behave normally.
        new_sel.clear()
        map(new_sel.add, old_sel)

        #This is the "real" drag_select that alters the selection for real.
        self.view.run_command("drag_select", args)

        for c in sublime_plugin.all_callbacks.setdefault('on_post_mouse_down',[]):
            c.on_post_mouse_down(click_point, self.view)

class MouseEventListener(sublime_plugin.EventListener):
    sublime_plugin.all_callbacks.setdefault('on_pre_mouse_down', [])
    sublime_plugin.all_callbacks.setdefault('on_post_mouse_down', [])
    
    def __init__(self, view = None):
        self.current_view = view


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
            URL_CACHE[story['title']] = story['url']
            
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

class MouseEventProcessor(MouseEventListener):
    def on_post_mouse_down(self, point, view):
        if view.settings().get('syntax') != HN_TMLANGUAGE_PATH:
            return
        
        region = view.line(point)
        line = view.substr(region)
        
        if re.match('^\(([\d]*)\)([ ]{1,10})(.*)$', line):
            title = re.sub('^\(([\d]*)\)([ ]{1,10})', '', line)
            
            try:
                url = URL_CACHE[title]
                
                # Check whether it's an external or HN link:
                foo = "/comments/"
                if url[:len(foo)] == foo:
                    url = "http://news.ycombinator.com/item?id=" + url.replace(foo, '')
                
                webbrowser.open(url)
            except:
                print "HackerNews: couldn't figure out URL"
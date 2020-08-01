# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from pelican import signals, contents
import os, urllib.request, json, datetime
from urllib.parse import urlparse

"""
  This plugin is for using with webmention.io jf2 API
"""

def article_url(content):
    #return content.settings[SITEURL]+'/'+content.url
    return WEBMENTION_SITEURL + "/" + content.url

def initialize_module(pelican):
    global WEBMENTION_IO_JF2_URL, WEBMENTION_SITEURL, WEBMENTION_IO_MAX_ITEMS, WEBMENTION_IO_API_KEY, WEBMENTION_IO_CACHE_FILENAME, WEBMENTION_IO_DOMAIN, WEBMENTION_IO_UPDATE_CACHE

    for parameter in [ 'WEBMENTION_IO_JF2_URL', 'WEBMENTION_SITEURL',
    'WEBMENTION_IO_MAX_ITEMS', 'WEBMENTION_IO_API_KEY',
    'WEBMENTION_IO_CACHE_FILENAME', 'WEBMENTION_IO_DOMAIN',
    'WEBMENTION_IO_UPDATE_CACHE', ]:
        if not parameter in pelican.settings.keys():
            print ("webmention_static error: no " + parameter + "defined in settings")
        else:
            globals()[parameter] = pelican.settings.get(parameter)
            ##globals()[parameter] = pelican.settings[parameter]
            ##print (globals()[parameter])
    if WEBMENTION_IO_UPDATE_CACHE:
        update_cache ()

def update_cache ():
    try:
        ##https://webmention.io/api/mentions.jf2?target=
        response = urllib.request.urlopen(WEBMENTION_IO_JF2_URL
            + "?domain=" + WEBMENTION_IO_DOMAIN
            + "&token=" + WEBMENTION_IO_API_KEY)
        data = response.read().decode("utf-8")
        ##data = response.get()
        file = open(WEBMENTION_IO_CACHE_FILENAME, "w+")
        file.write(data)
        file.close()
    except:
        raise

class Discussion(object):
    def __init__(self):
        self.liked = []
        self.mentioned = []
        self.replied = []
        self.reposted = []
        self.bookmarked = []
        self.followed = []
        self.rsvp = []
        self.unclassified = []

def setup_webmentions(generator, metadata):
    metadata['webmentions'] = Discussion()

def fetch_webmentions(generator, content):
    if not WEBMENTION_IO_JF2_URL: return
    print ("Fetching webmentions from URL:", WEBMENTION_IO_JF2_URL)

    ## Get all links "mentioning" this url
    target_url = article_url(content)
    print ("Fetching webmentions for local article:", target_url)

    try:
        file = open(WEBMENTION_IO_CACHE_FILENAME, "r")
        j = json.load(file)
        file.close()

        """
        # use this section if query webmention.io directly
        ##https://webmention.io/api/mentions.jf2?target=
        response = urllib.request.urlopen(WEBMENTION_IO_JF2_URL
        + "?per-page=" + str(WEBMENTION_IO_MAX_ITEMS)
        + "&target=" + target_url)
        data = response.read().decode("utf-8")
        j = json.loads(data)
        """
    except:
        raise
    ##print (j['children'])
    ##for x in j:
    #for x in j['children']:
    for x in j['children']:
      if ( x.get("wm-target", "") == target_url ):
        wm = {
            "wm-property": x.get("wm-property", ""),
            "published": x.get("published", ""),
            "wm-received": x.get("wm-received", ""),
            "name": x.get("name", "Untitled"),
            "summary": x.get("summary", ""),
            "text": x.get("content", {"text": ""}).get("text", ""),
            "author_name": x.get("author", {"name": "An unnamed person"}).get("name", "An unnamed person"),
            "author_photo": x.get("author", {"photo": "https://www.gravatar.com/avatar/no?d=mm"}).get("photo", "https://www.gravatar.com/avatar/no?d=mm"),
            "author_url": x.get("author", {"url": ""}).get("url", ""),
            "wm-source": x.get("wm-source", ""),
            "wm-target": x.get("wm-target", ""),
            "url": x.get("url", ""),
            "rsvp": x.get("rsvp", ""),
        }

        if wm["author_photo"] is None:
            wm["author_photo"] = "https://www.gravatar.com/avatar/no?d=mm"
        if wm["url"]:
            ##wm["parsed_url"] = urlparse.urlparse(wm["url"])
            wm["parsed_url"] = urlparse(wm["url"])
        else:
            wm["parsed_url"] = None
        if wm["published"] is None:
            wm["published"] = wm["wm-received"]

        print (wm["wm-property"], wm["name"], wm["author_name"], wm["author_url"], wm["url"] , wm["published"])

        comment = {
        'wm-property': wm["wm-property"],
        'published': wm["published"],
        'wm-received': wm["wm-received"],
        'name': wm["name"],
        'summary': wm["summary"],
        'text': wm["text"],
        'author_name': wm["author_name"],
        'author_photo': wm["author_photo"],
        'author_url': wm["author_url"],
        'wm-source': wm["wm-source"],
        'wm-target': wm["wm-target"],
        'url': wm["url"],
        'rsvp': wm["rsvp"],
        }

        if wm["wm-property"] == 'like-of':
            comment["reaction"] = 'liked'
            comment["icon"] = '❤️'
            content.webmentions.liked.append(comment)
        elif wm["wm-property"] == 'mention-of':
            comment["reaction"] = 'mentioned'
            comment["icon"] = '💬'
            content.webmentions.mentioned.append(comment)
        elif wm["wm-property"] == 'in-reply-to':
            comment["reaction"] = 'replied'
            comment["icon"] = '📩'
            content.webmentions.replied.append(comment)
        elif wm["wm-property"] == 'repost-of':
            comment["reaction"] = 'replied'
            comment["icon"] = '🔄'
            content.webmentions.reposted.append(comment)
        elif wm["wm-property"] == 'bookmark-of':
            comment["reaction"] = 'bookmarked'
            comment["icon"] = '⭐️'
            content.webmentions.bookmarked.append(comment)
        elif wm["wm-property"] == 'followed-of':
            comment["reaction"] = 'followed'
            comment["icon"] = '👣'
            content.webmentions.followed.append(comment)
        elif wm["wm-property"] == 'rsvp':
            rsvpIcon = {
                'yes': '✅',
                'no': '❌',
                'interested': '💡',
                'maybe': '❔',
            } 
            comment["reaction"] = wm["rsvp"]
            comment["icon"] = rsvpIcon[wm["rsvp"]]
            content.webmentions.rsvp.append(comment)
        else:
            print(f'Unrecognized comment type: {wm["wm-property"]}')
            comment["reaction"] = 'unclassified'
            comment["icon"] = '❔'
            content.webmentions.unclassified.append(comment)

def register():
    signals.initialized.connect(initialize_module)
    signals.article_generator_context.connect(setup_webmentions)
    ##signals.article_generator_finalized.connect(fetch_webmentions)
    signals.article_generator_write_article.connect(fetch_webmentions)

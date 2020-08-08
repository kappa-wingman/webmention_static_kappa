# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from pelican import signals, contents
import os, urllib.request, json, datetime
from urllib.parse import urlparse

#from django.core.paginator import Paginator
import django.core.paginator

import sys

"""
  This plugin is for using with webmention.io jf2 API
"""

#PROCESS = ['articles', 'pages', 'drafts']
#PROCESS = ['articles']

def article_url(content):
    #return content.settings[SITEURL]+'/'+content.url
    return WEBMENTION_SITEURL + "/" + content.url

def initialize_module(pelican):
    global WEBMENTION_IO_JF2_URL, WEBMENTION_SITEURL, WEBMENTION_IO_MAX_ITEMS, WEBMENTION_IO_API_KEY, WEBMENTION_IO_CACHE_FILENAME, WEBMENTION_IO_DOMAIN, WEBMENTION_IO_UPDATE_CACHE, WEBMENTION_IO_REPLIED_PAGINATION_SIZE

    for parameter in [ 'WEBMENTION_IO_JF2_URL', 'WEBMENTION_SITEURL',
    'WEBMENTION_IO_MAX_ITEMS', 'WEBMENTION_IO_API_KEY',
    'WEBMENTION_IO_CACHE_FILENAME', 'WEBMENTION_IO_DOMAIN',
    'WEBMENTION_IO_UPDATE_CACHE', 'WEBMENTION_IO_REPLIED_PAGINATION_SIZE', ]:
        if not parameter in pelican.settings.keys():
            print ("webmention_static error: no " + parameter + "defined in settings")
        else:
            globals()[parameter] = pelican.settings.get(parameter)
            ##globals()[parameter] = pelican.settings[parameter]
            ##print (globals()[parameter])

    global rsvpIcon
    rsvpIcon = {
        'yes': '✅',
        'no': '❌',
        'interested': '💡',
        'maybe': '❔',
    } 

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
        self.replied_paged = dict()
        self.replied_num_pages = 0
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
    current_Item_Count = 0
    ##print (j['children'])
    ##for x in j:
    #for x in j['children']:
    for x in j['children']:
      if ( x.get("wm-target", "") == target_url ):
        if (current_Item_Count >= WEBMENTION_IO_MAX_ITEMS) : break
        wm = {
            "wm-id": x.get("wm-id", ""),
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

        print (wm["wm-property"], wm["name"], wm["author_name"], wm["author_url"], wm["wm-source"] , wm["published"])

        comment = {
        'wm-id': wm["wm-id"],
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
            comment["reaction"] = 'reposted'
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
            comment["reaction"] = wm["rsvp"]
            comment["icon"] = rsvpIcon[wm["rsvp"]]
            content.webmentions.rsvp.append(comment)
        else:
            print(f'Unrecognized comment type: {wm["wm-property"]}')
            comment["reaction"] = 'unclassified'
            comment["icon"] = '❔'
            content.webmentions.unclassified.append(comment)
        current_Item_Count += 1

#def final_update(generator, content):
    if content.webmentions.replied and WEBMENTION_IO_REPLIED_PAGINATION_SIZE > 0:
      # Get all attributes from the generator that are articles or pages
      #posts = [
      #  getattr(generator, attr, None) for attr in PROCESS
      #  if getattr(generator, attr, None) is not None]
      page_size = WEBMENTION_IO_REPLIED_PAGINATION_SIZE
      paginator = django.core.paginator.Paginator(content.webmentions.replied, page_size)
      content.webmentions.replied_num_pages = paginator.num_pages
      print ("DEBUG, paginator count : ", paginator.count)

      page_no = 0
      current_item_no = 0
      for i in range (paginator.num_pages):
        # passing page_no, starting with 1 instead of 0
        page_no = i + 1
        for j in range (page_size):
          if page_no * (j+1) > paginator.count : break
          ## if use pop, the original content.webmentions.replied list would be empty
          ##content.webmentions.replied_paged.setdefault(page_no, []).append(content.webmentions.replied.pop())
          content.webmentions.replied_paged.setdefault(page_no, []).append(content.webmentions.replied[current_item_no])
          current_item_no += 1
          ##content.webmentions.replied_paged.append([content.webmentions.replied[0]])
        paged_json_file_path = os.path.join(generator.output_path, "wm-replied-"+str(page_no)+".json" )
        #print ("DEBUG2: ", paged_json_file_path)
        try:
          # Get the full path to the original source file
          source_out = os.path.join(
            content.settings['OUTPUT_PATH'], content.save_as
          )
          # Get the path to the original source file
          source_out_path = os.path.split(source_out)[0]
          # Create 'copy to' destination for writing later
          paged_json_file_path = os.path.join(
            source_out_path, "wm-replied-"+str(page_no)+".json"
          )
          os.makedirs(source_out_path, 0o775, exist_ok=True)
          file = open(paged_json_file_path, "w+")
          json.dump(content.webmentions.replied_paged.setdefault(page_no, []), file)
          file.close()
        except:
          raise
      ## start with 1 (page no)
      ##print ("DEBUG3: ", content.webmentions.replied_paged[1]);

def register():
    signals.initialized.connect(initialize_module)
    signals.article_generator_context.connect(setup_webmentions)
    signals.article_generator_write_article.connect(fetch_webmentions)
    ##signals.article_writer_finalized.connect(final_update)
    ##signals.article_generator_finalized.connect(final_update)

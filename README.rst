Webmention static comment plugin for Pelican
--------------------------------------------

This plugin is to be used or tested with webmention.io JF2 endpoint.
The output from that endpint should be in JF2 format.

This plugin references multiple projects related to Webmentions and Pelican plugin:

- `Gist from Stuart Langridge <https://gist.github.com/stuartlangridge/ef08d5e1737181e2bee7>`__
- `pelican-webmention plugin by Desmond Rivet <https://github.com/drivet/pelican-webmention>`__
- `Webmention.js by Fluffy <https://github.com/PlaidWeb/webmention.js/blob/master/static/webmention.js>`__
- `Mention Tech by Kevin Marks <https://github.com/kevinmarks/mentiontech>`__
- `Pelican Plugins <https://github.com/getpelican/pelican-plugins/>`__

Options
-------

- PLUGINS += ['webmention_static_kappa']
- WEBMENTION_USERNAME = 'Update to your username in webmention.io'
- WEBMENTION_FETCH_URL = 'https://webmention.io/'+WEBMENTION_USERNAME+'/webmention'
- WEBMENTION_SITEURL = 'Usually same as SITEURL'
- WEBMENTION_IO_JF2_URL = 'https://webmention.io/api/mentions.jf2'
- MAX_ITEMS was effective for old version (non cache version)

  - New version of this plugin fetches all the Webmentions for the domain in one single file

    But this option also control the maximum items to display
  - WEBMENTION_IO_MAX_ITEMS = 50

- You need to create the cache directory manually

  - WARNING, it would overwrite the file in below when static pages start to generate
  - WEBMENTION_IO_CACHE_FILENAME = './webmention-cache/cache.json'

- WEBMENTION_IO_DOMAIN = 'Replace by the hostname of your website here, no need to put https://'
- WEBMENTION_IO_OVERWRITE_INITIAL_CACHE = False - Overwrite initial cache file
- WEBMENTION_IO_UPDATE_INITIAL_CACHE = True - Update initial cache file
- WEBMENTION_IO_REPLIED_PAGINATION_SIZE - For paging replies, WIP

Sample template
---------------

You probably need a template to use display the output from the plugin.
Below is just an example, you should add styling and change the layout.
Repeat for other items like articles.webmentions.liked and etc.

.. code-block:: html+jinja

   {% if article.webmentions.mentioned %}
       <p> List of mentions: </p>
     {% for item_mentioned in article.webmentions.mentioned %}
        <a href="{{ item_mentioned['wm-source'] }}"
           rel="nofollow noopener noreferrer ugc"
           title="{{ item_mentioned['author_name'] }} {{ item_mentioned['reaction'] }}">
        {% if item_mentioned['author_photo'] %}
           <img src="{{ item_mentioned['author_photo'] }}">
        {% endif %}
        {{ item_mentioned['icon'] }}{{ item_mentioned['author_name'] }}
        </a> : {{ item_mentioned['name'] }}
     {% endfor %}
   {% endif %}

Notes
-----

This plugin is not perfect. There are areas for improvement:

- Pagination. Useful if there are lots of Webmentions to display.

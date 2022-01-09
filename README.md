Enhanced Unfurls: A Plugin for Pelican
====================================================

[![Build Status](https://img.shields.io/github/workflow/status/pelican-plugins/enhanced-unfurls/build)](https://github.com/pelican-plugins/enhanced-unfurls/actions)
[![PyPI Version](https://img.shields.io/pypi/v/pelican-enhanced-unfurls)](https://pypi.org/project/pelican-enhanced-unfurls/)
![License](https://img.shields.io/pypi/l/pelican-enhanced-unfurls?color=blue)

Generate metadata for improved link unfurls in Facebook/Slack/Twitter/etc.

Installation
------------

This plugin can be installed via:

    python -m pip install pelican-enhanced-unfurls

Settings
--------

All settings are stored in an `ENHANCED_UNFURLS` dict:

|      Settings       | Default Value | What does it do? |
| ------------------- | ------------- | ---------------- |
| `facebook`          |     False     | Enable creation of Facebook-specific unfurl tags |
| `twitter`           |     False     | Enable creation of Twitter-specific unfurl tags |
| `oembed`            |     False     | Enable creation of oEmbed JSON files with links to reference them |
| `first_image_lede`  |     False     | If a lede image has not been specified either by the content or a default lede, use the first image in the content |
| `default_lede`      |     None      | If the content does not specify a lede image, use this image (can be referenced using {static} or using a full URL) |
| `default_card_type` |     None      | If Twitter support is enabled and the content does not specify a [card type](https://developer.twitter.com/en/docs/twitter-for-websites/cards/overview/abouts-cards), use this value|

Note that Open Graph unfurl tags are always generated.

Usage
-----

Add support for including the desired tags in the `<head>` section of your `base.html` template:

```jinja2
{% if article -%}
{% if article.oembed_url %}
<link type="application/json+oembed" href="{{ article.oembed_url }}" />
{% endif %}
{% if article.unfurl_og -%}
{% for tag, value in article.unfurl_og.items() %}
<meta property="{{ tag }}" content="{{ value|striptags|e }}" />
{% endfor %}
{% endif %}
{% if article.unfurl_fb -%}
{% for tag, value in article.unfurl_fb.items() %}
<meta property="{{ tag }}" content="{{ value|striptags|e }}" />
{% endfor %}
{% endif %}
{% if article.unfurl_twitter -%}
{% for tag, value in article.unfurl_twitter.items() %}
<meta name="{{ tag }}" content="{{ value|striptags|e }}" />
{% endfor %}
{% endif %}
{% endif %}
```

Then add the necessary metadata to your content, which will be mapped to the correct tags:

|    Metadata    |       Open Graph       |       Twitter       |     oEmbed     | Facebook  |
| -------------- | ---------------------- | ------------------- | -------------- | --------- |
|      url       |         og:url         |     twitter:url     |      url       |           |
|     title      |        og:title        |    twitter:title    |     title      |           |
|    summary     |     og:description     | twitter:description |                |           |
|      lede      |        og:image        |    twitter:image    |                |           |
|      type      |        og:type         |                     |                |           |
|     locale     |       og:locale        |                     |                |           |
|      date      | article:published_time |                     |                |           |
|    modified    | article:modified_time  |                     |                |           |
|   card_type    |                        |    twitter:card     |                |           |
|   lede_desc    |                        |  twitter:image:alt  |                |           |
| author_twitter |                        |   twitter:creator   |                |           |
|  site_twitter  |                        |    twitter:site     |                |           |
|      tl1       |                        |   twitter:label1    |                |           |
|      td1       |                        |    twitter:data1    |                |           |
|      tl2       |                        |   twitter:label2    |                |           |
|      td2       |                        |    twitter:data2    |                |           |
|   fb_app_id    |                        |                     |                | fb:app_id |

Contributing
------------

Contributions are welcome and much appreciated. Every little bit helps. You can contribute by improving the documentation, adding missing features, and fixing bugs. You can also help out by reviewing and commenting on [existing issues][].

To start contributing to this plugin, review the [Contributing to Pelican][] documentation, beginning with the **Contributing Code** section.

[existing issues]: https://github.com/pelican-plugins/enhanced-unfurls/issues
[Contributing to Pelican]: https://docs.getpelican.com/en/latest/contribute.html

License
-------

This project is licensed under version 3.0 of the Non-Profit Open Source License.

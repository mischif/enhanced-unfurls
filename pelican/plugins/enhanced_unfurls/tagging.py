################################################################################
#                               enhanced-unfurls                               #
#  Generate metadata for improved link unfurls in Facebook/Slack/Twitter/etc.  #
#                             (C)2022 Jeremy Brown                             #
#            Released under Prosperity Public License version 3.0.0            #
################################################################################

from datetime import datetime
from logging import getLogger
from pathlib import Path

logger = getLogger(__name__)


def map_to_tags(metadata, tag_map):
    """
    Map the metadata of a piece of content to the specified tags.

    :param metadata: (dict) Content metadata
    :param tag_map: (dict) Mapping from metadata keys to tag keys

    :returns: (dict) Content metadata mapped to given tags
    """
    result = {}

    for (src, dst) in tag_map.items():
        val = metadata.get(src)

        if val is not None:
            if isinstance(val, datetime):
                result[dst] = val.date().isoformat()
            else:
                result[dst] = val

    return result


def insert_tags(generator, content):
    """
    Convert content metadata into key/value pairs
    to be consumed by third parties

    :param generator: (pelican.generators.Generator) Content generator
    :param content: (pelican.contents.Content) Content to be tagged
    """
    settings = generator.settings
    siteurl = settings.get("SITEURL")
    eu_settings = settings.get("ENHANCED_UNFURLS", {})
    fb_support = eu_settings.get("facebook", False)
    twitter_support = eu_settings.get("twitter", False)
    oembed_support = eu_settings.get("oembed", False)

    og_map = {
        "type": "og:type",
        "url": "og:url",
        "title": "og:title",
        "summary": "og:description",
        "lede": "og:image",
        "locale": "og:locale",
        "date": "article:published_time",
        "modified": "article:modified_time",
    }

    fb_map = {
        "fb_app_id": "fb:app_id",
    }

    twitter_map = {
        "card_type": "twitter:card",
        "url": "twitter:url",
        "title": "twitter:title",
        "summary": "twitter:description",
        "lede": "twitter:image",
        "lede_desc": "twitter:image:alt",
        "author_twitter": "twitter:creator",
        "site_twitter": "twitter:site",
        "domain": "twitter:domain",
        "tl1": "twitter:label1",
        "td1": "twitter:data1",
        "tl2": "twitter:label2",
        "td2": "twitter:data2",
    }

    if siteurl is not None:
        content.metadata["summary"] = content.get_summary(siteurl)

    content.unfurl_og = map_to_tags(content.metadata, og_map)

    if fb_support:
        tags = map_to_tags(content.metadata, fb_map)
        if tags:
            content.unfurl_fb = tags

    if twitter_support:
        tags = map_to_tags(content.metadata, twitter_map)
        if tags:
            content.unfurl_twitter = tags

    if oembed_support:
        content_path = Path(content.save_as)
        oembed_path = None

        if content_path.name == "index.html":
            oembed_path = content_path.with_name("oembed.json")

        elif content_path.suffix != "":
            oembed_path = content_path.with_suffix(".json")

        if oembed_path is not None and siteurl is not None:
            content.oembed_url = f"{siteurl}/{str(oembed_path)}"
            content.oembed_save_as = str(oembed_path)

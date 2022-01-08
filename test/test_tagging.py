################################################################################
#                               enhanced-unfurls                               #
#  Generate metadata for improved link unfurls in Facebook/Slack/Twitter/etc.  #
#                             (C)2022 Jeremy Brown                             #
#            Released under Prosperity Public License version 3.0.0            #
################################################################################

from datetime import datetime
from unittest.mock import Mock

import pytest

from pelican.plugins.enhanced_unfurls.tagging import insert_tags, map_to_tags
from pelican.tests.support import get_article, get_settings


def test_map_to_tags():
    test_map = {
        "src-key-1": "dest-key-1",
        "src-key-2": "dest-key-2",
        "src-key-3": "dest-key-3",
    }

    test_data = {
        "src-key-0": "val-0",
        "src-key-1": "val-1",
        "src-key-3": datetime(1969, 4, 20, 10, 17, 0),
    }

    result = map_to_tags(test_data, test_map)

    assert "src-key-0" not in result
    assert "src-key-2" not in result
    assert result.get("dest-key-1") == "val-1"
    assert result.get("dest-key-3") == "1969-04-20"


@pytest.mark.parametrize(
    "output_fmt",
    ["posts/{slug}/index.html", "posts/{slug}.html"],
    ids=["common-filename", "unique-filename"],
)
@pytest.mark.parametrize(
    "siteurl", ["http://example.com", None], ids=["siteurl", "no-siteurl"]
)
def test_insert_tags(siteurl, output_fmt):
    eu_settings = {"facebook": True, "twitter": True, "oembed": True}
    mock_gen = Mock()
    mock_gen.settings = get_settings(SITEURL=siteurl, ENHANCED_UNFURLS=eu_settings)

    mock_category = Mock()
    mock_category.slug = "test"
    content_md = {
        "category": mock_category,
        "type": "article",
        "url": f"http://example.com/{output_fmt.format(slug='test-article')}",
        "summary": "Test article content",
        "lede": "http://example.com/test.png",
        "locale": "en_US",
        "date": datetime(1969, 4, 20, 10, 17, 0),
        "modified": datetime(1969, 6, 9, 10, 17, 0),
        "fb_app_id": "1234567",
        "card_type": "summary",
        "lede_desc": "An example image",
        "author_twitter": "@johndoe",
        "site_twitter": "@examplecom",
        "domain": "example.com",
        "tl1": "key-1",
        "td1": "val-1",
        "tl2": "key-2",
        "td2": "val-2",
    }

    mock_content = get_article("Test Article", "Test article content", **content_md)
    mock_content.settings["ARTICLE_SAVE_AS"] = output_fmt

    insert_tags(mock_gen, mock_content)
    assert hasattr(mock_content, "unfurl_og")
    assert len(mock_content.unfurl_og) == 8 if siteurl else 7
    assert mock_content.unfurl_og["article:published_time"] == "1969-04-20"
    assert mock_content.unfurl_og["article:modified_time"] == "1969-06-09"
    assert mock_content.unfurl_og["og:title"] == "Test Article"
    assert mock_content.unfurl_og["og:type"] == content_md["type"]
    assert mock_content.unfurl_og["og:url"] == content_md["url"]
    assert mock_content.unfurl_og["og:image"] == content_md["lede"]
    assert mock_content.unfurl_og["og:locale"] == content_md["locale"]

    assert hasattr(mock_content, "unfurl_fb")
    assert len(mock_content.unfurl_fb) == 1
    assert mock_content.unfurl_fb["fb:app_id"] == content_md["fb_app_id"]

    assert hasattr(mock_content, "unfurl_twitter")
    assert len(mock_content.unfurl_twitter) == 13
    assert mock_content.unfurl_twitter["twitter:title"] == "Test Article"
    assert mock_content.unfurl_twitter["twitter:card"] == content_md["card_type"]
    assert mock_content.unfurl_twitter["twitter:url"] == content_md["url"]
    assert mock_content.unfurl_twitter["twitter:image"] == content_md["lede"]
    assert mock_content.unfurl_twitter["twitter:image:alt"] == content_md["lede_desc"]
    assert (
        mock_content.unfurl_twitter["twitter:creator"] == content_md["author_twitter"]
    )
    assert mock_content.unfurl_twitter["twitter:site"] == content_md["site_twitter"]
    assert mock_content.unfurl_twitter["twitter:domain"] == content_md["domain"]
    assert mock_content.unfurl_twitter["twitter:label1"] == content_md["tl1"]
    assert mock_content.unfurl_twitter["twitter:data1"] == content_md["td1"]
    assert mock_content.unfurl_twitter["twitter:label2"] == content_md["tl2"]
    assert mock_content.unfurl_twitter["twitter:data2"] == content_md["td2"]

    if siteurl:
        assert mock_content.unfurl_og["og:description"] == content_md["summary"]
        assert (
            mock_content.unfurl_twitter["twitter:description"] == content_md["summary"]
        )

        assert hasattr(mock_content, "oembed_save_as")
        if output_fmt.endswith("index.html"):
            assert mock_content.oembed_save_as.endswith("oembed.json")
        else:
            assert mock_content.oembed_save_as.endswith("test-article.json")

        assert hasattr(mock_content, "oembed_url")

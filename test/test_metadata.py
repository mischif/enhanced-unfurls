################################################################################
#                               enhanced-unfurls                               #
#  Generate metadata for improved link unfurls in Facebook/Slack/Twitter/etc.  #
#                             (C)2022 Jeremy Brown                             #
#            Released under Prosperity Public License version 3.0.0            #
################################################################################

from pathlib import Path
from unittest.mock import Mock, patch
from urllib.parse import urlparse

import pytest

from pelican.generators import ArticlesGenerator, StaticGenerator
from pelican.plugins.enhanced_unfurls.metadata import enhance_metadata, get_metadata
from pelican.tests.support import get_context, get_settings


@pytest.mark.parametrize(
    "default_card, article_card",
    [[None, None], ["video", None], ["video", "summary"]],
    ids=["no-card", "default-card", "article-card"],
)
@pytest.mark.parametrize("locale", [[""], ["en_US.UTF8"]], ids=["no-locale", "locale"])
@pytest.mark.parametrize(
    "siteurl", ["http://example.com", ""], ids=["siteurl", "no-siteurl"]
)
@pytest.mark.parametrize(
    "lede", ["none", "rel", "abs", "def-rel", "def-abs", "fil-pres", "fil-miss"]
)
def test_get_metadata(siteurl, lede, locale, default_card, article_card):
    mock_logger = Mock()
    test_data = Path(__file__).parent.joinpath("data")

    eu_settings = {
        "default_card_type": default_card,
        "default_lede": None,
        "first_image_lede": False,
    }

    settings = get_settings(
        SITEURL=siteurl,
        STATIC_PATHS=["static"],
        ARTICLE_PATHS=["posts"],
        ENHANCED_UNFURLS=eu_settings,
    )
    context = get_context(settings)

    StaticGenerator(
        context=context,
        settings=settings,
        path=test_data,
        theme=settings["THEME"],
        output_path=None,
    ).generate_context()

    ArticlesGenerator(
        context=context,
        settings=settings,
        path=test_data,
        theme=settings["THEME"],
        output_path=None,
    ).generate_context()

    content = context["articles"][0]

    if article_card:
        content.metadata["card_type"] = article_card

    if lede == "rel":
        content.metadata["lede"] = "{static}/test/data/static/test.png"

    elif lede == "abs":
        content.metadata["lede"] = "http://example.com/images/abs/test.png"

    elif lede.startswith("def"):
        if lede.endswith("rel"):
            eu_settings["default_lede"] = "{static}/test/data/static/test.png"
        else:
            eu_settings["default_lede"] = "http://example.com/images/abs/test.png"

    elif lede.startswith("fil"):
        eu_settings["first_image_lede"] = True

        if lede.endswith("pres"):
            content.get_static_links = lambda: {
                "static/images/skipme.bmp",
                "test/data/static/test.png",
            }

    result = get_metadata(mock_logger, content, eu_settings, siteurl, locale)

    assert result["type"] == "article"

    if locale[0]:
        assert result["locale"] == "en_US"
    else:
        assert "locale" not in result

    if article_card:
        assert "card_type" not in result
    elif default_card:
        assert result["card_type"] == default_card
    elif "lede" in result:
        assert result["card_type"] == "summary_large_image"
    else:
        assert result["card_type"] == "summary"

    if siteurl:
        assert result["url"] == f"{siteurl}/{content.url}"
        assert result["domain"] == urlparse(siteurl).netloc

        if lede in ("rel", "def-rel", "fil-pres"):
            assert result["lede"] == "http://example.com/test/data/static/test.png"
    else:
        if lede not in ("abs", "def-abs"):
            assert "lede" not in result
        else:
            assert result["lede"] == "http://example.com/images/abs/test.png"


@pytest.mark.parametrize(
    "default_lede",
    [None, "http://example.com/test.png"],
    ids=["no-default-lede", "absolute-default-lede"],
)
@pytest.mark.parametrize(
    "siteurl", ["http://example.com", ""], ids=["siteurl", "no-siteurl"]
)
@patch("pelican.plugins.enhanced_unfurls.metadata.logger")
def test_enhance_metadata(mock_logger, siteurl, default_lede):
    eu_settings = {"default_lede": default_lede}
    test_data = Path(__file__).parent.joinpath("data")

    settings = get_settings(
        SITEURL=siteurl,
        STATIC_PATHS=["static"],
        ARTICLE_PATHS=["posts"],
        ENHANCED_UNFURLS=eu_settings,
    )
    context = get_context(settings)

    stat_gen = StaticGenerator(
        context=context,
        settings=settings,
        path=test_data,
        theme=settings["THEME"],
        output_path=None,
    )

    art_gen = ArticlesGenerator(
        context=context,
        settings=settings,
        path=test_data,
        theme=settings["THEME"],
        output_path=None,
    )
    stat_gen.generate_context()
    art_gen.generate_context()
    enhance_metadata([stat_gen, art_gen])

    if default_lede:
        assert art_gen.articles[0].metadata["card_type"] == "summary_large_image"
        mock_logger.info.assert_called_once_with(
            "Default lede images not using {{static}} assumed to be full URLs"
        )
    else:
        assert art_gen.articles[0].metadata["card_type"] == "summary"

    if siteurl:
        assert art_gen.articles[0].metadata["domain"] == "example.com"
    else:
        mock_logger.warning.assert_called_once_with(
            "SITEURL not defined; tags requiring full URL will not be generated"
        )

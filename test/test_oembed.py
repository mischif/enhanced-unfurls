################################################################################
#                               enhanced-unfurls                               #
#  Generate metadata for improved link unfurls in Facebook/Slack/Twitter/etc.  #
#                             (C)2022 Jeremy Brown                             #
#            Released under Prosperity Public License version 3.0.0            #
################################################################################

from json import loads
from pathlib import Path
from unittest.mock import patch

import pytest

from pelican.generators import ArticlesGenerator
from pelican.plugins.enhanced_unfurls.oembed import OEmbedGenerator, add_generator
from pelican.tests.support import get_context, get_settings


def test_add_generator():
    assert add_generator(None) is OEmbedGenerator


@pytest.mark.parametrize("sitename", ["", "Test Site"], ids=["no-sitename", "sitename"])
@patch("pelican.plugins.enhanced_unfurls.metadata.logger")
def test_generate_output(mock_logger, sitename, tmpdir):
    eu_settings = {"oembed": True}
    test_data = Path(__file__).parent.joinpath("data")

    settings = get_settings(
        SITENAME=sitename,
        STATIC_PATHS=["static"],
        ARTICLE_PATHS=["posts"],
        ENHANCED_UNFURLS=eu_settings,
    )
    context = get_context(settings)

    ArticlesGenerator(
        context=context,
        settings=settings,
        path=test_data,
        theme=settings["THEME"],
        output_path=None,
    ).generate_context()

    gen = OEmbedGenerator(
        context=context,
        settings=settings,
        path=test_data,
        theme=settings["THEME"],
        output_path=str(tmpdir),
    )

    context["articles"][0].metadata["url"] = "http://example.com/test-article.html"
    context["articles"][0].oembed_save_as = "test-article.json"
    context["articles"][0].oembed_url = "http://example.com/test-article.json"
    gen.generate_output()

    oembed_file = tmpdir.join("test-article.json")
    assert oembed_file.exists() and oembed_file.isfile()
    oembed_json = loads(oembed_file.read_text("UTF-8"))
    assert oembed_json["url"] == context["articles"][0].metadata["url"]
    assert oembed_json["title"] == context["articles"][0].metadata["title"]
    if sitename:
        assert oembed_json["provider_name"] == sitename

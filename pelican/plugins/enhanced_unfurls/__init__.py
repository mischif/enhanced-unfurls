################################################################################
#                               enhanced-unfurls                               #
#  Generate metadata for improved link unfurls in Facebook/Slack/Twitter/etc.  #
#                             (C)2022 Jeremy Brown                             #
#       Released under version 3.0 of the Non-Profit Open Source License       #
################################################################################

from pelican import signals

from .metadata import enhance_metadata
from .oembed import add_generator
from .tagging import insert_tags


def register():
    signals.all_generators_finalized.connect(enhance_metadata)
    signals.article_generator_write_article.connect(insert_tags)
    signals.get_generators.connect(add_generator)

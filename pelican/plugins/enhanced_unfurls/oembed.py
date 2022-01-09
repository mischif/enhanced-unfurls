################################################################################
#                               enhanced-unfurls                               #
#  Generate metadata for improved link unfurls in Facebook/Slack/Twitter/etc.  #
#                             (C)2022 Jeremy Brown                             #
#       Released under version 3.0 of the Non-Profit Open Source License       #
################################################################################

from json import dumps
from logging import getLogger
from pathlib import Path

logger = getLogger(__name__)


class OEmbedGenerator:
    def __init__(self, *args, **kwargs):
        self.context = kwargs["context"]
        self.settings = kwargs["settings"].get("ENHANCED_UNFURLS", {})
        self.out_root = Path(kwargs["output_path"])

    def generate_output(self, *args, **kwargs):
        """
        Write oEmbed files for specified content
        """
        if self.settings.get("oembed", False):
            for content in self.context["articles"]:
                oembed_path = self.out_root.joinpath(content.oembed_save_as)
                provider_name = self.context.get("SITENAME")
                info = {
                    "type": "link",
                    "version": "1.0",
                    "url": content.metadata["url"],
                    "title": content.metadata["title"],
                }

                if provider_name:
                    info["provider_name"] = provider_name

                oembed_path.write_text(dumps(info))
                logger.debug(f"Content: {info['url']}")
                logger.debug(f"oEmbed info: {content.oembed_url}")


def add_generator(generators):
    return OEmbedGenerator

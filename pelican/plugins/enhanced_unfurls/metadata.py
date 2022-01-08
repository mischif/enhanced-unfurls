################################################################################
#                               enhanced-unfurls                               #
#  Generate metadata for improved link unfurls in Facebook/Slack/Twitter/etc.  #
#                             (C)2022 Jeremy Brown                             #
#            Released under Prosperity Public License version 3.0.0            #
################################################################################

from logging import getLogger
from urllib.parse import urlparse

from pelican.generators import ArticlesGenerator

logger = getLogger(__name__)
VALID_EXTS = ["jpg", "jpeg", "png", "gif"]


def get_metadata(logger, content, settings, siteurl, locale):
    """
    Prepare raw content metadata to be used downstream,
    and pull additional metadata from elsewhere as necessary

    :param logger: (logging.Logger) Service logger
    :param content: (pelican.contents.Content) Content to gather
                                               metadata of/for
    :param settings: (dict) Enhanced unfurls settings
    :param siteurl: (str) Root URL of site
    :param locale: (list) Locale(s) of site

    :returns: (dict) New and updated metadata
    """

    def _static_to_url(link):
        result = None
        raw_path = link.strip("{static}").lstrip("/")
        link_obj = content._context["static_content"].get(raw_path)

        if siteurl and link_obj is not None:
            result = f"{siteurl}/{link_obj.url}"

        return result

    default_lede = settings.get("default_lede")
    default_card_type = settings.get("default_card_type")

    metadata = {}

    # The content has explicitly specified a lede image
    if "lede" in content.metadata:

        # The provided lede image is only a link
        if content.metadata["lede"].startswith("{static}"):
            lede_url = _static_to_url(content.metadata["lede"])

            if lede_url is not None:
                metadata["lede"] = lede_url

        # The provided lede image is assumed to be a full URL
        else:
            metadata["lede"] = content.metadata["lede"]

    # The default image specified in the settings should be used
    elif default_lede:

        # The provided lede image is only a link
        if default_lede.startswith("{static}"):
            lede_url = _static_to_url(default_lede)

            if lede_url is not None:
                metadata["lede"] = lede_url

        # The provided lede image is assumed to be a full URL
        else:
            metadata["lede"] = default_lede

    # The first image in the content should be used as the lede
    elif settings.get("first_image_lede", False):
        for f in content.get_static_links():
            if siteurl and f.split(".")[-1] in VALID_EXTS:
                metadata["lede"] = f"{siteurl}/{f}"
                break

    if "type" not in content.metadata:
        metadata["type"] = "article"

    if "card_type" not in content.metadata:
        if default_card_type:
            metadata["card_type"] = default_card_type

        elif "lede" in metadata:
            metadata["card_type"] = "summary_large_image"

        else:
            metadata["card_type"] = "summary"

    if locale[0] and "locale" not in content.metadata:
        metadata["locale"] = locale[0].split(".")[0]

    if siteurl:
        metadata["url"] = f"{siteurl}/{content.url}"
        metadata["domain"] = urlparse(siteurl).netloc

    return metadata


def enhance_metadata(generators):
    """
    Update content metadata for use in tagging

    :param generators: (list) Generators to update content for
    """
    warned_missing_siteurl = False
    warned_default_lede_url = False

    no_siteurl = "SITEURL not defined; tags requiring full URL will not be generated"
    lede_note = "Default lede images not using {{static}} assumed to be full URLs"

    for gen in generators:
        content = []
        locale = gen.context.get("LOCALE", [""])
        siteurl = gen.context.get("SITEURL")
        eu_settings = gen.context.get("ENHANCED_UNFURLS", {})

        if not warned_missing_siteurl and not siteurl:
            logger.warning(no_siteurl)
            warned_missing_siteurl = True

        default_lede = eu_settings.get("default_lede")
        if (
            not warned_default_lede_url
            and isinstance(default_lede, str)
            and not default_lede.startswith("{static}")
        ):
            logger.info(lede_note)
            warned_default_lede_url = True

        if isinstance(gen, ArticlesGenerator):
            content = gen.articles + gen.translations

        for c in content:
            c.metadata.update(get_metadata(logger, c, eu_settings, siteurl, locale))

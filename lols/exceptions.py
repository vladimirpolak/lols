class ScraperError(Exception):
    pass


class ScraperInitError(ScraperError):
    """Raised if Scraper failed to initialize properly."""
    pass


class ExtractionError(ScraperError):
    """Raised if error during data extraction."""
    pass


class PasswordRequired(ScraperError):
    """Raised if password is required to access content."""
    pass


class ContentTypeError(ScraperError):
    """Raised if extracted content type unknown."""
    pass


class ParsingError(ScraperError):
    """Raised if error during scraped data parsing."""
    pass


class GoFileStatusUnknownError(ExtractionError):
    """Raised if Gofile response contains an unknown status message."""
    pass

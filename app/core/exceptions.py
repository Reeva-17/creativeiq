class ProviderUnavailableError(RuntimeError):
    """The configured LLM cannot safely produce an analysis."""


class ProviderResponseError(RuntimeError):
    """The LLM response was not valid for the requested schema."""

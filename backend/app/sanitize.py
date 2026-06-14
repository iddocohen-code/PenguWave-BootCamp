"""HTML sanitization utilities. Used by schemas to escape text on output for XSS defense."""

import html


def escape_event_text(text: str | None) -> str | None:
    """HTML-escape text so it's safe to render in a browser without dangerouslySetInnerHTML.

    Converts evt-052's stored XSS payload `<img src=x onerror=alert(...)>` to
    `&lt;img src=x onerror=alert(...)&gt;` so it renders as text, not executable.
    """
    if text is None:
        return None
    return html.escape(text)

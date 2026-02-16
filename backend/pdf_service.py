"""
PDF generation service for newsletter summaries.
Uses reportlab to produce a clean, readable PDF.
"""
import io
from typing import Dict, List
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.colors import HexColor
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, HRFlowable, ListFlowable, ListItem
)


def generate_summary_pdf(
    date_str: str,
    newsletters: List[Dict],
    themes: Dict,
) -> bytes:
    """
    Generate a PDF summarizing newsletters for a given day.

    Args:
        date_str: The date string (YYYY-MM-DD)
        newsletters: List of newsletter summary dicts (id, sender_name, title, summary, key_points)
        themes: Dict with 'themes' list and 'synthesis' string

    Returns:
        PDF file contents as bytes
    """
    buf = io.BytesIO()
    doc = SimpleDocTemplate(
        buf,
        pagesize=letter,
        leftMargin=0.75 * inch,
        rightMargin=0.75 * inch,
        topMargin=0.75 * inch,
        bottomMargin=0.75 * inch,
    )

    styles = getSampleStyleSheet()

    # Custom styles
    title_style = ParagraphStyle(
        "PDFTitle",
        parent=styles["Title"],
        fontSize=20,
        spaceAfter=6,
    )
    subtitle_style = ParagraphStyle(
        "PDFSubtitle",
        parent=styles["Normal"],
        fontSize=11,
        textColor=HexColor("#666666"),
        spaceAfter=16,
    )
    nl_title_style = ParagraphStyle(
        "NLTitle",
        parent=styles["Heading2"],
        fontSize=14,
        spaceBefore=12,
        spaceAfter=2,
    )
    sender_style = ParagraphStyle(
        "Sender",
        parent=styles["Normal"],
        fontSize=10,
        textColor=HexColor("#888888"),
        spaceAfter=8,
    )
    body_style = ParagraphStyle(
        "Body",
        parent=styles["Normal"],
        fontSize=10,
        leading=14,
        spaceAfter=8,
    )
    bullet_style = ParagraphStyle(
        "Bullet",
        parent=styles["Normal"],
        fontSize=10,
        leading=14,
        leftIndent=18,
        spaceAfter=3,
    )
    section_header_style = ParagraphStyle(
        "SectionHeader",
        parent=styles["Heading1"],
        fontSize=16,
        spaceBefore=20,
        spaceAfter=10,
    )
    theme_title_style = ParagraphStyle(
        "ThemeTitle",
        parent=styles["Heading3"],
        fontSize=12,
        spaceBefore=8,
        spaceAfter=2,
    )

    story: list = []

    # Title
    story.append(Paragraph(f"Newsletter Summary &mdash; {date_str}", title_style))
    story.append(Paragraph(f"{len(newsletters)} newsletter{'s' if len(newsletters) != 1 else ''} summarized", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=1, color=HexColor("#cccccc"), spaceAfter=12))

    # Per-newsletter sections
    for idx, nl in enumerate(newsletters):
        title = _escape(nl.get("title", nl.get("subject", "Untitled")))
        sender = _escape(nl.get("sender_name", "Unknown"))
        summary = _escape(nl.get("summary", ""))
        key_points = nl.get("key_points", [])

        story.append(Paragraph(title, nl_title_style))
        story.append(Paragraph(f"From: {sender}", sender_style))

        if summary:
            for para in summary.split("\n"):
                para = para.strip()
                if para:
                    story.append(Paragraph(para, body_style))

        if key_points:
            for point in key_points:
                story.append(Paragraph(f"&bull; {_escape(point)}", bullet_style))

        if idx < len(newsletters) - 1:
            story.append(Spacer(1, 6))
            story.append(HRFlowable(width="100%", thickness=0.5, color=HexColor("#dddddd"), spaceAfter=6))

    # Overlapping themes section
    theme_list = themes.get("themes", [])
    synthesis = themes.get("synthesis", "")

    if theme_list or synthesis:
        story.append(Spacer(1, 12))
        story.append(HRFlowable(width="100%", thickness=1.5, color=HexColor("#333333"), spaceAfter=8))
        story.append(Paragraph("Overlapping Themes", section_header_style))

        if synthesis:
            story.append(Paragraph(_escape(synthesis), body_style))
            story.append(Spacer(1, 6))

        for theme in theme_list:
            t_title = _escape(theme.get("title", ""))
            t_desc = _escape(theme.get("description", ""))
            sources = theme.get("sources", [])

            story.append(Paragraph(t_title, theme_title_style))
            if t_desc:
                story.append(Paragraph(t_desc, body_style))
            if sources:
                story.append(Paragraph(
                    f"<i>Sources: {_escape(', '.join(sources))}</i>",
                    sender_style,
                ))

    doc.build(story)
    return buf.getvalue()


def _escape(text: str) -> str:
    """Escape XML-special characters for reportlab Paragraphs."""
    if not text:
        return ""
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )

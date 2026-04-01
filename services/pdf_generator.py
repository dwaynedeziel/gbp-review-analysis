import io
from datetime import datetime
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    KeepTogether,
    PageBreak,
)
from models.analysis import AnalysisResult


# Brand colors
BRAND_DARK = colors.HexColor("#1B4332")
BRAND_GREEN = colors.HexColor("#2E7D32")
BRAND_GREEN_ACCENT = colors.HexColor("#4CAF50")
BRAND_GREEN_LIGHT = colors.HexColor("#E8F5E9")
SLATE_900 = colors.HexColor("#0F172A")
SLATE_700 = colors.HexColor("#334155")
SLATE_500 = colors.HexColor("#64748B")
SLATE_200 = colors.HexColor("#E2E8F0")
SLATE_100 = colors.HexColor("#F1F5F9")
SLATE_50 = colors.HexColor("#F8FAFC")
WHITE = colors.white
GREEN = colors.HexColor("#059669")
GREEN_LIGHT = colors.HexColor("#ECFDF5")
RED = colors.HexColor("#DC2626")
RED_LIGHT = colors.HexColor("#FEF2F2")
AMBER = colors.HexColor("#D97706")
AMBER_LIGHT = colors.HexColor("#FFFBEB")
MAROON = colors.HexColor("#8B1A1A")

# Star bar colors
STAR_COLORS = {
    "5": colors.HexColor("#22C55E"),
    "4": colors.HexColor("#84CC16"),
    "3": colors.HexColor("#EAB308"),
    "2": colors.HexColor("#F97316"),
    "1": colors.HexColor("#EF4444"),
}

PAGE_WIDTH, PAGE_HEIGHT = letter
MARGIN = 0.6 * inch
CONTENT_WIDTH = PAGE_WIDTH - 2 * MARGIN


def generate_pdf(result: AnalysisResult) -> bytes:
    """Generate the branded PDF report and return as bytes."""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        leftMargin=MARGIN,
        rightMargin=MARGIN,
        topMargin=0.4 * inch,
        bottomMargin=0.5 * inch,
    )

    styles = _build_styles()
    story = []

    # 1. Header
    story.extend(_build_header(result, styles))
    story.append(Spacer(1, 16))

    # 2. Executive Summary
    story.extend(_build_executive_summary(result, styles))
    story.append(Spacer(1, 16))

    # 3. Per-Profile Analysis
    for i, pa in enumerate(result.profile_analyses):
        story.extend(_build_profile_section(pa, styles, index=i + 1))
        if i < len(result.profile_analyses) - 1:
            story.append(Spacer(1, 12))

    story.append(Spacer(1, 16))

    # 4. Impact Summary Table
    story.extend(_build_impact_table(result, styles))
    story.append(Spacer(1, 16))

    # 5. Why This Matters
    story.extend(_build_why_matters(result, styles))
    story.append(Spacer(1, 16))

    # 6. Investment & Pricing
    story.extend(_build_pricing_section(result, styles))
    story.append(Spacer(1, 16))

    # 7. Next Steps
    story.extend(_build_next_steps(result, styles))
    story.append(Spacer(1, 16))

    # 8. Footer
    story.extend(_build_footer(result, styles))

    doc.build(story)
    return buffer.getvalue()


def _build_styles():
    styles = getSampleStyleSheet()

    styles.add(ParagraphStyle(
        "BrandTitle",
        parent=styles["Title"],
        fontName="Helvetica-Bold",
        fontSize=22,
        textColor=WHITE,
        alignment=TA_LEFT,
        spaceAfter=4,
    ))
    styles.add(ParagraphStyle(
        "BrandSubtitle",
        fontName="Helvetica",
        fontSize=11,
        textColor=colors.HexColor("#A8D5BA"),
        alignment=TA_LEFT,
    ))
    styles.add(ParagraphStyle(
        "SectionTitle",
        fontName="Helvetica-Bold",
        fontSize=14,
        textColor=SLATE_900,
        spaceAfter=8,
        spaceBefore=4,
    ))
    styles.add(ParagraphStyle(
        "SubsectionTitle",
        fontName="Helvetica-Bold",
        fontSize=11,
        textColor=SLATE_700,
        spaceAfter=4,
    ))
    styles.add(ParagraphStyle(
        "BodyText2",
        fontName="Helvetica",
        fontSize=9.5,
        textColor=SLATE_700,
        leading=13,
        spaceAfter=6,
    ))
    styles.add(ParagraphStyle(
        "SmallText",
        fontName="Helvetica",
        fontSize=8,
        textColor=SLATE_500,
        leading=10,
    ))
    styles.add(ParagraphStyle(
        "StatValue",
        fontName="Helvetica-Bold",
        fontSize=18,
        textColor=BRAND_GREEN,
        alignment=TA_CENTER,
    ))
    styles.add(ParagraphStyle(
        "StatLabel",
        fontName="Helvetica",
        fontSize=8,
        textColor=SLATE_500,
        alignment=TA_CENTER,
    ))
    styles.add(ParagraphStyle(
        "WhiteText",
        fontName="Helvetica",
        fontSize=9.5,
        textColor=WHITE,
        leading=13,
    ))
    styles.add(ParagraphStyle(
        "WhiteBold",
        fontName="Helvetica-Bold",
        fontSize=10,
        textColor=WHITE,
    ))
    styles.add(ParagraphStyle(
        "CenterBody",
        fontName="Helvetica",
        fontSize=9.5,
        textColor=SLATE_700,
        alignment=TA_CENTER,
        leading=13,
    ))

    return styles


def _build_header(result: AnalysisResult, styles):
    """Dark branded banner with title, client name, date, profile count."""
    report_date = datetime.now().strftime("%B %d, %Y")
    n_profiles = len(result.profile_analyses)

    header_data = [[
        Paragraph("WISE DIGITAL PARTNERS", ParagraphStyle(
            "LogoText", fontName="Helvetica-Bold", fontSize=9,
            textColor=BRAND_GREEN_ACCENT, spaceAfter=6,
        )),
    ], [
        Paragraph("Google Review Performance", styles["BrandTitle"]),
    ], [
        Paragraph("& Opportunity Analysis", ParagraphStyle(
            "TitleLine2", fontName="Helvetica-Bold", fontSize=18,
            textColor=WHITE, spaceAfter=6,
        )),
    ], [
        Paragraph(
            f"Confidential &middot; Prepared Exclusively for {result.business.name}",
            styles["BrandSubtitle"],
        ),
    ]]

    header_table = Table(header_data, colWidths=[CONTENT_WIDTH])
    header_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), BRAND_DARK),
        ("LEFTPADDING", (0, 0), (-1, -1), 20),
        ("RIGHTPADDING", (0, 0), (-1, -1), 20),
        ("TOPPADDING", (0, 0), (0, 0), 16),
        ("BOTTOMPADDING", (-1, -1), (-1, -1), 10),
        ("TOPPADDING", (0, 1), (-1, -1), 0),
        ("BOTTOMPADDING", (0, 0), (-1, -2), 2),
        ("ROUNDEDCORNERS", [8, 8, 0, 0]),
    ]))

    # Metadata row: PREPARED BY | DATE | PROFILES ANALYZED
    meta_label_style = ParagraphStyle(
        "MetaLabel", fontName="Helvetica", fontSize=7,
        textColor=SLATE_500, spaceAfter=2,
    )
    meta_value_style = ParagraphStyle(
        "MetaValue", fontName="Helvetica-Bold", fontSize=9,
        textColor=SLATE_900,
    )

    meta_data = [[
        Table(
            [[Paragraph("PREPARED BY", meta_label_style)],
             [Paragraph("WISE Digital Partners", meta_value_style)]],
            colWidths=[CONTENT_WIDTH / 3 - 14],
        ),
        Table(
            [[Paragraph("DATE", meta_label_style)],
             [Paragraph(report_date, meta_value_style)]],
            colWidths=[CONTENT_WIDTH / 3 - 14],
        ),
        Table(
            [[Paragraph("PROFILES ANALYZED", meta_label_style)],
             [Paragraph(str(n_profiles), meta_value_style)]],
            colWidths=[CONTENT_WIDTH / 3 - 14],
        ),
    ]]

    meta_table = Table(meta_data, colWidths=[CONTENT_WIDTH / 3] * 3)
    meta_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), WHITE),
        ("TOPPADDING", (0, 0), (-1, -1), 10),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
        ("LEFTPADDING", (0, 0), (-1, -1), 20),
        ("ROUNDEDCORNERS", [0, 0, 8, 8]),
        ("LINEABOVE", (0, 0), (-1, 0), 0.5, SLATE_200),
    ]))

    return [header_table, meta_table]


def _section_title_with_accent(title, styles, accent_color=None):
    """Section title with a colored left-border accent bar."""
    if accent_color is None:
        accent_color = BRAND_GREEN
    title_cell = Table(
        [[Paragraph(title, styles["SectionTitle"])]],
        colWidths=[CONTENT_WIDTH - 6],
    )
    title_cell.setStyle(TableStyle([
        ("LEFTPADDING", (0, 0), (-1, -1), 10),
        ("TOPPADDING", (0, 0), (-1, -1), 0),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
    ]))
    accent_table = Table(
        [[""  , title_cell]],
        colWidths=[4, CONTENT_WIDTH - 4],
    )
    accent_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, 0), accent_color),
        ("TOPPADDING", (0, 0), (-1, -1), 0),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ]))
    return accent_table


def _build_executive_summary(result: AnalysisResult, styles):
    """Executive summary with stat cards."""
    elements = []
    elements.append(_section_title_with_accent("Executive Summary", styles, BRAND_GREEN))
    elements.append(Spacer(1, 6))
    elements.append(Paragraph(result.executive_summary, styles["BodyText2"]))
    if result.executive_summary_2:
        elements.append(Paragraph(result.executive_summary_2, styles["BodyText2"]))

    if result.data_is_estimated:
        elements.append(Paragraph(
            "<i>Note: Star distribution data was estimated based on available "
            "totals and averages. Actual distribution may vary.</i>",
            styles["SmallText"],
        ))

    # Stat cards row
    totals = result.totals
    cards_data = [
        (str(totals["total_reviews"]), "TOTAL REVIEWS"),
        (str(totals["total_to_remove"]), "REVIEWS TO REMOVE"),
        (
            f"{totals['profiles_needing_action']} of {totals['total_profiles']}",
            "PROFILES NEEDING ACTION",
        ),
        (f"+{totals['max_lift']:.2f}\u2605", "MAX PROJECTED LIFT"),
    ]

    card_cells = []
    for value, label in cards_data:
        cell = Table(
            [[Paragraph(value, styles["StatValue"])],
             [Paragraph(label, styles["StatLabel"])]],
            colWidths=[CONTENT_WIDTH / 4 - 8],
        )
        cell.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), SLATE_50),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("TOPPADDING", (0, 0), (-1, -1), 10),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
            ("ROUNDEDCORNERS", [6, 6, 6, 6]),
        ]))
        card_cells.append(cell)

    cards_table = Table([card_cells], colWidths=[CONTENT_WIDTH / 4] * 4)
    cards_table.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 3),
        ("RIGHTPADDING", (0, 0), (-1, -1), 3),
    ]))

    elements.append(Spacer(1, 8))
    elements.append(cards_table)
    return elements


def _build_profile_section(pa, styles, index=1):
    """Per-profile analysis: star bars, current vs projected, badges."""
    profile = pa.profile
    elements = []

    # Profile header with green left-border accent
    elements.append(_section_title_with_accent(
        f"Profile {index} \u2014 {profile.name}", styles, BRAND_GREEN
    ))
    elements.append(Spacer(1, 6))

    # Recommendation badge (full width)
    if pa.recommendation == "remove":
        rec_badge = Table(
            [[Paragraph(
                f"<font color='#DC2626'>\u25a0</font> &nbsp;"
                f"<b>RECOMMENDATION: {pa.recommendation_detail}</b>",
                ParagraphStyle(
                    "RecBadge", fontName="Helvetica-Bold", fontSize=9,
                    textColor=RED,
                ),
            )]],
            colWidths=[CONTENT_WIDTH],
        )
        rec_badge.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), RED_LIGHT),
            ("TOPPADDING", (0, 0), (-1, -1), 6),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ("LEFTPADDING", (0, 0), (-1, -1), 10),
            ("ROUNDEDCORNERS", [4, 4, 4, 4]),
        ]))
        elements.append(rec_badge)
        elements.append(Spacer(1, 6))

    # Profile card
    # Card header: name + URL
    card_header_rows = [
        [Paragraph(f"<b>{profile.name}</b>", ParagraphStyle(
            "CardName", fontName="Helvetica-Bold", fontSize=11,
            textColor=SLATE_900,
        ))],
    ]
    if profile.url:
        card_header_rows.append([
            Paragraph(profile.url, ParagraphStyle(
                "CardURL", fontName="Helvetica", fontSize=8,
                textColor=BRAND_GREEN,
            )),
        ])

    # Star distribution bars
    dist = profile.distribution
    star_data = dist.as_dict()
    pcts = dist.percentages()

    bar_rows = []
    for star in ["5", "4", "3", "2", "1"]:
        count = star_data[star]
        pct = pcts[star]
        bar_width = max(2, pct * 1.5)

        bar_cell = Table(
            [[""]], colWidths=[bar_width], rowHeights=[12],
        )
        bar_cell.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), STAR_COLORS[star]),
            ("ROUNDEDCORNERS", [3, 3, 3, 3]),
        ]))

        bar_rows.append([
            Paragraph(f"{star}\u2605", ParagraphStyle(
                f"Star{star}_{index}", fontName="Helvetica-Bold", fontSize=8,
                textColor=SLATE_700,
            )),
            bar_cell,
            Paragraph(f"{count}", ParagraphStyle(
                f"Count{star}_{index}", fontName="Helvetica", fontSize=8,
                textColor=SLATE_500, alignment=TA_RIGHT,
            )),
        ])

    star_table = Table(
        bar_rows,
        colWidths=[30, 100, 35],
        rowHeights=[16] * 5,
    )
    star_table.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 2),
        ("RIGHTPADDING", (0, 0), (-1, -1), 2),
        ("TOPPADDING", (0, 0), (-1, -1), 1),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 1),
    ]))

    # Rating comparison: current → projected
    current_color = SLATE_700
    projected_color = GREEN if pa.what_if.rating_lift > 0 else SLATE_700

    # Current rating
    current_block = Table(
        [[Paragraph(f"<b>{profile.average_rating:.1f}\u2605</b>", ParagraphStyle(
            f"CurRating_{index}", fontName="Helvetica-Bold", fontSize=20,
            textColor=current_color,
        ))],
         [Paragraph(f"CURRENT ({profile.distribution.total} reviews)", ParagraphStyle(
             f"CurLabel_{index}", fontName="Helvetica", fontSize=7,
             textColor=SLATE_500,
         ))]],
        colWidths=[100],
    )
    current_block.setStyle(TableStyle([
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("TOPPADDING", (0, 0), (-1, -1), 0),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
    ]))

    # Arrow
    arrow = Paragraph("\u2192", ParagraphStyle(
        f"Arrow_{index}", fontName="Helvetica", fontSize=16,
        textColor=SLATE_500, alignment=TA_CENTER,
    ))

    # Projected rating
    projected_block = Table(
        [[Paragraph(f"<b>{pa.what_if.new_average:.2f}\u2605</b>", ParagraphStyle(
            f"ProjRating_{index}", fontName="Helvetica-Bold", fontSize=20,
            textColor=projected_color,
        ))],
         [Paragraph(f"PROJECTED ({pa.what_if.new_total} reviews)", ParagraphStyle(
             f"ProjLabel_{index}", fontName="Helvetica", fontSize=7,
             textColor=SLATE_500,
         ))]],
        colWidths=[100],
    )
    projected_block.setStyle(TableStyle([
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("TOPPADDING", (0, 0), (-1, -1), 0),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
    ]))

    ratings_row = Table(
        [[current_block, arrow, projected_block]],
        colWidths=[100, 30, 100],
    )
    ratings_row.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
    ]))

    # Rating lift badge
    if pa.what_if.rating_lift > 0:
        lift_badge = Table(
            [[Paragraph(
                f"<b>+{pa.what_if.rating_lift:.2f}\u2605</b>",
                ParagraphStyle(
                    f"LiftVal_{index}", fontName="Helvetica-Bold", fontSize=10,
                    textColor=GREEN, alignment=TA_CENTER,
                ),
            )],
             [Paragraph("RATING LIFT", ParagraphStyle(
                 f"LiftLbl_{index}", fontName="Helvetica", fontSize=7,
                 textColor=GREEN, alignment=TA_CENTER,
             ))]],
            colWidths=[80],
        )
        lift_badge.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), GREEN_LIGHT),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("TOPPADDING", (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ("ROUNDEDCORNERS", [4, 4, 4, 4]),
        ]))
    else:
        lift_badge = Paragraph("")

    # Right side: ratings + lift badge
    right_content = Table(
        [[ratings_row], [Spacer(1, 4)], [lift_badge]],
        colWidths=[CONTENT_WIDTH / 2 - 10],
    )
    right_content.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
    ]))

    # Left side: card header + star bars
    left_content = Table(
        card_header_rows + [[Spacer(1, 6)], [star_table]],
        colWidths=[CONTENT_WIDTH / 2 - 10],
    )
    left_content.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 4),
    ]))

    # Combine in card
    combined = Table(
        [[left_content, right_content]],
        colWidths=[CONTENT_WIDTH / 2, CONTENT_WIDTH / 2],
    )
    combined.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("BACKGROUND", (0, 0), (-1, -1), SLATE_50),
        ("ROUNDEDCORNERS", [6, 6, 6, 6]),
        ("LEFTPADDING", (0, 0), (-1, -1), 10),
        ("RIGHTPADDING", (0, 0), (-1, -1), 10),
        ("TOPPADDING", (0, 0), (-1, -1), 10),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
        ("BOX", (0, 0), (-1, -1), 0.5, SLATE_200),
    ]))

    elements.append(combined)

    # Remove breakdown text
    if pa.what_if.removed_count > 0:
        elements.append(Spacer(1, 4))
        elements.append(Paragraph(
            f"Removing {pa.what_if.remove_breakdown} "
            f"({pa.what_if.removed_count} total)",
            styles["SmallText"],
        ))

    return [KeepTogether(elements)]


def _build_impact_table(result: AnalysisResult, styles):
    """Impact summary table: all profiles side-by-side with totals row."""
    elements = []
    elements.append(Paragraph("Impact Summary", styles["SectionTitle"]))

    header = ["Profile", "Total Reviews", "Current Rating", "To Remove",
              "Projected Rating", "Rating Lift"]

    rows = [header]
    for pa in result.profile_analyses:
        p = pa.profile
        rows.append([
            p.name,
            str(p.distribution.total),
            f"{p.average_rating:.1f}",
            str(pa.what_if.removed_count),
            f"{pa.what_if.new_average:.1f}",
            f"+{pa.what_if.rating_lift:.2f}" if pa.what_if.rating_lift > 0 else "\u2014",
        ])

    # Totals row
    totals = result.totals
    rows.append([
        "TOTALS",
        str(totals["total_reviews"]),
        "\u2014",
        str(totals["total_to_remove"]),
        "\u2014",
        f"+{totals['max_lift']:.2f}" if totals["max_lift"] > 0 else "\u2014",
    ])

    col_widths = [CONTENT_WIDTH * w for w in [0.25, 0.15, 0.15, 0.13, 0.17, 0.15]]
    table = Table(rows, colWidths=col_widths)

    table_style = [
        # Header row
        ("BACKGROUND", (0, 0), (-1, 0), BRAND_DARK),
        ("TEXTCOLOR", (0, 0), (-1, 0), WHITE),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, 0), 9),
        # Totals row
        ("BACKGROUND", (0, -1), (-1, -1), SLATE_100),
        ("FONTNAME", (0, -1), (-1, -1), "Helvetica-Bold"),
        # All cells
        ("FONTNAME", (0, 1), (-1, -2), "Helvetica"),
        ("FONTSIZE", (0, 1), (-1, -1), 9),
        ("TEXTCOLOR", (0, 1), (-1, -1), SLATE_700),
        ("ALIGN", (1, 0), (-1, -1), "CENTER"),
        ("ALIGN", (0, 0), (0, -1), "LEFT"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("GRID", (0, 0), (-1, -1), 0.5, SLATE_200),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("ROUNDEDCORNERS", [6, 6, 6, 6]),
    ]

    # Alternate row backgrounds
    for i in range(1, len(rows) - 1):
        if i % 2 == 0:
            table_style.append(("BACKGROUND", (0, i), (-1, i), SLATE_50))

    table.setStyle(TableStyle(table_style))
    elements.append(table)
    return elements


def _build_why_matters(result: AnalysisResult, styles):
    """6-item grid: search CTR, calls, competitive positioning, trust, AI, ads."""
    elements = []
    elements.append(_section_title_with_accent(
        "Why This Matters for Your Business", styles, MAROON
    ))
    elements.append(Spacer(1, 6))

    prospect = result.terminology.get("prospect", "prospect")
    customers = result.terminology.get("customers", "customers")

    # Intro paragraph
    elements.append(Paragraph(
        f"This is not a cosmetic improvement. Google ratings directly influence "
        f"{prospect} behavior at every stage of the funnel \u2014 and even a fraction "
        f"of a star places you in a meaningfully different tier of trust and visibility.",
        styles["BodyText2"],
    ))
    elements.append(Spacer(1, 6))

    items = [
        ("Search Click-Through Rate",
         f"Higher ratings earn more clicks from Google Maps and local search results "
         f"\u2014 before a {prospect} even visits your site."),
        ("More Inbound Calls",
         f"Businesses above 4.8\u2605 see significantly higher call volume from their "
         f"Google Business Profile."),
        ("Competitive Positioning",
         f"In most local markets, 4.9\u2605 places you in the top tier \u2014 shifting "
         f"from \"a strong option\" to \"the obvious choice.\""),
        ("Psychological Trust",
         f"{customers.capitalize()} anchor on the lowest reviews. Even a handful of "
         f"1-stars create friction at the decision moment."),
        ("Better AI Visibility",
         f"Review ratings play a significant role in how AI platforms recommend "
         f"local businesses to high-intent {customers}."),
        ("Better Ad Performance",
         f"Google Ads, LSA, and Yelp all perform better when your ratings are strong. "
         f"Star ratings appear directly in ads."),
    ]

    # Build 2x3 grid with green left-border accent cards
    grid_rows = []
    for i in range(0, len(items), 2):
        row_cells = []
        for j in range(2):
            if i + j < len(items):
                title, desc = items[i + j]
                # Inner content
                inner = Table(
                    [[Paragraph(f"<b>{title}</b>", ParagraphStyle(
                        f"WM_T_{i}{j}", fontName="Helvetica-Bold", fontSize=9,
                        textColor=SLATE_900, spaceAfter=3,
                    ))],
                     [Paragraph(desc, ParagraphStyle(
                         f"WM_D_{i}{j}", fontName="Helvetica", fontSize=8,
                         textColor=SLATE_700, leading=11,
                     ))]],
                    colWidths=[CONTENT_WIDTH / 2 - 24],
                )
                inner.setStyle(TableStyle([
                    ("TOPPADDING", (0, 0), (-1, -1), 6),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                    ("LEFTPADDING", (0, 0), (-1, -1), 8),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 8),
                ]))
                # Card with green left border
                cell = Table(
                    [["", inner]],
                    colWidths=[3, CONTENT_WIDTH / 2 - 19],
                )
                cell.setStyle(TableStyle([
                    ("BACKGROUND", (0, 0), (0, -1), BRAND_GREEN),
                    ("BACKGROUND", (1, 0), (1, -1), WHITE),
                    ("BOX", (0, 0), (-1, -1), 0.5, SLATE_200),
                    ("TOPPADDING", (0, 0), (-1, -1), 0),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
                    ("LEFTPADDING", (0, 0), (-1, -1), 0),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ]))
                row_cells.append(cell)
            else:
                row_cells.append("")
        grid_rows.append(row_cells)

    grid = Table(grid_rows, colWidths=[CONTENT_WIDTH / 2] * 2)
    grid.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 4),
        ("RIGHTPADDING", (0, 0), (-1, -1), 4),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))

    elements.append(grid)
    return elements


def _build_pricing_section(result: AnalysisResult, styles):
    """Investment & Pricing section."""
    elements = []
    pricing = result.pricing

    elements.append(Paragraph("Investment & Pricing", styles["SectionTitle"]))
    elements.append(Spacer(1, 4))

    # Price header row: label left, price right
    if pricing.original_per_review > 0:
        price_right = Paragraph(
            f"<font color='#059669' size='18'><b>${pricing.per_review}</b></font>"
            f" &nbsp;<strike><font color='#94A3B8' size='12'>${pricing.original_per_review}</font></strike>",
            ParagraphStyle("PriceRight", fontName="Helvetica-Bold", fontSize=18,
                           textColor=GREEN, alignment=TA_RIGHT),
        )
    else:
        price_right = Paragraph(
            f"<font color='#059669' size='18'><b>${pricing.per_review}</b></font>",
            ParagraphStyle("PriceRight", fontName="Helvetica-Bold", fontSize=18,
                           textColor=GREEN, alignment=TA_RIGHT),
        )

    price_header = Table(
        [[Paragraph("<b>Cost Per Review Removal</b>", ParagraphStyle(
            "PriceLabel", fontName="Helvetica-Bold", fontSize=12,
            textColor=SLATE_900,
        )), price_right]],
        colWidths=[CONTENT_WIDTH * 0.5, CONTENT_WIDTH * 0.5],
    )
    price_header.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), SLATE_50),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 12),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 12),
        ("LEFTPADDING", (0, 0), (0, 0), 16),
        ("RIGHTPADDING", (-1, 0), (-1, 0), 16),
        ("ROUNDEDCORNERS", [6, 6, 0, 0]),
        ("BOX", (0, 0), (-1, -1), 0.5, SLATE_200),
    ]))
    elements.append(price_header)

    # Three stat columns with colored header bars
    standard_total = pricing.standard_total
    discounted_total = pricing.discounted_total
    savings = pricing.savings

    TEAL = colors.HexColor("#0D9488")
    PRICE_RED = colors.HexColor("#DC2626")

    card_data = [
        (str(pricing.total_reviews), "REVIEWS TO REMOVE", TEAL, SLATE_700),
        (f"${standard_total:,}", "STANDARD TOTAL", SLATE_500, SLATE_700),
        (f"${discounted_total:,}", "WITH BULK DISCOUNT", PRICE_RED, RED),
    ]

    card_cells = []
    for value, label, header_color, text_color in card_data:
        # Header bar
        header_bar = Table([[""]], colWidths=[CONTENT_WIDTH / 3 - 16], rowHeights=[4])
        header_bar.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), header_color),
        ]))
        cell = Table(
            [[header_bar],
             [Paragraph(label, ParagraphStyle(
                 f"PL_{label}", fontName="Helvetica", fontSize=7,
                 textColor=SLATE_500, alignment=TA_CENTER,
             ))],
             [Paragraph(f"<b>{value}</b>", ParagraphStyle(
                 f"PC_{label}", fontName="Helvetica-Bold", fontSize=18,
                 textColor=text_color, alignment=TA_CENTER,
             ))]],
            colWidths=[CONTENT_WIDTH / 3 - 12],
        )
        cell.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), WHITE),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("TOPPADDING", (0, 0), (0, 0), 0),
            ("TOPPADDING", (0, 1), (-1, -1), 8),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
            ("BOX", (0, 0), (-1, -1), 0.5, SLATE_200),
        ]))
        card_cells.append(cell)

    cards = Table([card_cells], colWidths=[CONTENT_WIDTH / 3] * 3)
    cards.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 4),
        ("RIGHTPADDING", (0, 0), (-1, -1), 4),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    elements.append(cards)

    # Discount banner
    if pricing.discount_pct > 0 and savings > 0:
        banner = Table(
            [[Paragraph(
                f"<font color='#1B4332'>\u25a0</font> &nbsp;"
                f"<b>Limited Bulk Discount \u2014 {pricing.discount_pct}% Off This Order</b>",
                ParagraphStyle(
                    "DiscTitle", fontName="Helvetica-Bold", fontSize=10,
                    textColor=BRAND_DARK,
                ),
            )],
             [Paragraph(
                 f"Approve all {pricing.total_reviews} review removals together and receive "
                 f"{pricing.discount_pct}% off the entire order, saving you ${savings:,}. "
                 f"As always, you are only invoiced when we successfully remove a review "
                 f"\u2014 zero risk, zero upfront cost.",
                 ParagraphStyle(
                     "DiscDesc", fontName="Helvetica", fontSize=8,
                     textColor=SLATE_700, leading=11,
                 ),
             )]],
            colWidths=[CONTENT_WIDTH - 24],
        )
        banner.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), GREEN_LIGHT),
            ("TOPPADDING", (0, 0), (0, 0), 10),
            ("TOPPADDING", (0, 1), (0, 1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
            ("LEFTPADDING", (0, 0), (-1, -1), 12),
            ("RIGHTPADDING", (0, 0), (-1, -1), 12),
            ("ROUNDEDCORNERS", [0, 0, 6, 6]),
        ]))
        elements.append(banner)

    return elements


def _build_next_steps(result: AnalysisResult, styles):
    """Light green cards with numbered steps."""
    elements = []

    elements.append(Paragraph(
        "<b>Recommended Next Steps</b>",
        styles["SectionTitle"],
    ))
    elements.append(Spacer(1, 4))

    for i, step in enumerate(result.next_steps, 1):
        step_card = Table(
            [[Paragraph(f"STEP {i:02d}", ParagraphStyle(
                f"StepLabel{i}", fontName="Helvetica-Bold", fontSize=8,
                textColor=GREEN,
            ))],
             [Paragraph(f"<b>{step['title']}</b>", ParagraphStyle(
                 f"StepTitle{i}", fontName="Helvetica-Bold", fontSize=11,
                 textColor=SLATE_900, spaceAfter=2,
             ))],
             [Paragraph(step["description"], ParagraphStyle(
                 f"StepDesc{i}", fontName="Helvetica", fontSize=9,
                 textColor=SLATE_700, leading=12,
             ))]],
            colWidths=[CONTENT_WIDTH - 24],
        )
        step_card.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), GREEN_LIGHT),
            ("LEFTPADDING", (0, 0), (-1, -1), 12),
            ("RIGHTPADDING", (0, 0), (-1, -1), 12),
            ("TOPPADDING", (0, 0), (0, 0), 10),
            ("TOPPADDING", (0, 1), (-1, -1), 2),
            ("BOTTOMPADDING", (-1, -1), (-1, -1), 10),
            ("ROUNDEDCORNERS", [6, 6, 6, 6]),
        ]))
        elements.append(step_card)
        elements.append(Spacer(1, 6))

    return elements


def _build_footer(result: AnalysisResult, styles):
    """Wise Digital Partners branding and confidentiality note."""
    elements = []
    elements.append(Spacer(1, 8))

    business_name = result.business.name if result.business else "the intended recipient"

    footer_table = Table(
        [[Paragraph(
            "<b>WISE DIGITAL PARTNERS</b>",
            ParagraphStyle(
                "FooterLeft", fontName="Helvetica-Bold", fontSize=8,
                textColor=BRAND_GREEN,
            ),
        ),
          Paragraph(
            f"Confidential \u2014 Prepared for {business_name}",
            ParagraphStyle(
                "FooterRight", fontName="Helvetica", fontSize=7,
                textColor=SLATE_500, alignment=TA_RIGHT,
            ),
        )]],
        colWidths=[CONTENT_WIDTH * 0.5, CONTENT_WIDTH * 0.5],
    )
    footer_table.setStyle(TableStyle([
        ("LINEABOVE", (0, 0), (-1, 0), 0.5, SLATE_200),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ]))

    elements.append(footer_table)
    return elements

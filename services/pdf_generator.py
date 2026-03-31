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
INDIGO = colors.HexColor("#4F46E5")
INDIGO_DARK = colors.HexColor("#3730A3")
INDIGO_LIGHT = colors.HexColor("#EEF2FF")
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
        story.extend(_build_profile_section(pa, styles))
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
    story.extend(_build_footer(styles))

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
        textColor=colors.HexColor("#C7D2FE"),
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
        textColor=INDIGO,
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
    profile_text = f"{n_profiles} Profile{'s' if n_profiles != 1 else ''} Analyzed"

    header_data = [[
        Paragraph("WISE DIGITAL PARTNERS", ParagraphStyle(
            "LogoText", fontName="Helvetica-Bold", fontSize=9,
            textColor=colors.HexColor("#A5B4FC"), spaceAfter=6,
        )),
    ], [
        Paragraph("Google Business Profile", styles["BrandTitle"]),
    ], [
        Paragraph("Review Analysis Report", ParagraphStyle(
            "TitleLine2", fontName="Helvetica-Bold", fontSize=18,
            textColor=WHITE, spaceAfter=8,
        )),
    ], [
        Paragraph(
            f"Prepared for <b>{result.business.name}</b> &nbsp;|&nbsp; "
            f"{report_date} &nbsp;|&nbsp; {profile_text}",
            styles["BrandSubtitle"],
        ),
    ]]

    header_table = Table(header_data, colWidths=[CONTENT_WIDTH])
    header_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), INDIGO_DARK),
        ("LEFTPADDING", (0, 0), (-1, -1), 20),
        ("RIGHTPADDING", (0, 0), (-1, -1), 20),
        ("TOPPADDING", (0, 0), (0, 0), 16),
        ("BOTTOMPADDING", (-1, -1), (-1, -1), 16),
        ("TOPPADDING", (0, 1), (-1, -1), 0),
        ("BOTTOMPADDING", (0, 0), (-1, -2), 2),
        ("ROUNDEDCORNERS", [8, 8, 8, 8]),
    ]))

    return [header_table]


def _build_executive_summary(result: AnalysisResult, styles):
    """Executive summary with stat cards."""
    elements = []
    elements.append(Paragraph("Executive Summary", styles["SectionTitle"]))
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
        (str(totals["total_reviews"]), "Total Reviews"),
        (str(totals["total_to_remove"]), "Reviews to Remove"),
        (
            f"{totals['profiles_needing_action']} of {totals['total_profiles']}",
            "Profiles Need Action",
        ),
        (f"+{totals['max_lift']:.2f}", "Max Rating Lift"),
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


def _build_profile_section(pa, styles):
    """Per-profile analysis: star bars, current vs projected, badges."""
    profile = pa.profile
    elements = []

    # Profile header
    name_text = f"<b>{profile.name}</b>"
    if profile.url:
        name_text += f" &nbsp;<font color='#64748B' size='8'>({profile.url})</font>"
    elements.append(Paragraph(name_text, styles["SubsectionTitle"]))

    # Star distribution bars + stats side by side
    dist = profile.distribution
    star_data = dist.as_dict()
    pcts = dist.percentages()

    # Build star bar rows
    bar_rows = []
    for star in ["5", "4", "3", "2", "1"]:
        count = star_data[star]
        pct = pcts[star]
        bar_width = max(2, pct * 1.5)  # Scale for display

        bar_cell = Table(
            [[""]], colWidths=[bar_width], rowHeights=[12],
        )
        bar_cell.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), STAR_COLORS[star]),
            ("ROUNDEDCORNERS", [3, 3, 3, 3]),
        ]))

        bar_rows.append([
            Paragraph(f"{star}\u2605", ParagraphStyle(
                f"Star{star}", fontName="Helvetica-Bold", fontSize=8,
                textColor=SLATE_700,
            )),
            bar_cell,
            Paragraph(f"{count}", ParagraphStyle(
                f"Count{star}", fontName="Helvetica", fontSize=8,
                textColor=SLATE_500, alignment=TA_RIGHT,
            )),
            Paragraph(f"{pct}%", ParagraphStyle(
                f"Pct{star}", fontName="Helvetica", fontSize=8,
                textColor=SLATE_500, alignment=TA_RIGHT,
            )),
        ])

    star_table = Table(
        bar_rows,
        colWidths=[30, 100, 35, 35],
        rowHeights=[16] * 5,
    )
    star_table.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 2),
        ("RIGHTPADDING", (0, 0), (-1, -1), 2),
        ("TOPPADDING", (0, 0), (-1, -1), 1),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 1),
    ]))

    # Rating comparison (current vs projected)
    current_color = SLATE_700
    projected_color = GREEN if pa.what_if.rating_lift > 0 else SLATE_700

    rating_rows = [
        [Paragraph("Current Rating", ParagraphStyle(
            "RLbl", fontName="Helvetica", fontSize=8, textColor=SLATE_500,
        )),
         Paragraph(f"<b>{profile.average_rating:.1f}</b>", ParagraphStyle(
             "RVal", fontName="Helvetica-Bold", fontSize=16, textColor=current_color,
         ))],
        [Paragraph("Projected Rating", ParagraphStyle(
            "PLbl", fontName="Helvetica", fontSize=8, textColor=SLATE_500,
        )),
         Paragraph(f"<b>{pa.what_if.new_average:.1f}</b>", ParagraphStyle(
             "PVal", fontName="Helvetica-Bold", fontSize=16, textColor=projected_color,
         ))],
    ]
    rating_table = Table(rating_rows, colWidths=[80, 50])
    rating_table.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))

    # Badges
    if pa.recommendation == "remove":
        badge_bg = RED_LIGHT
        badge_color = RED
        badge_text = f"\u2191 +{pa.what_if.rating_lift:.2f} lift"
        rec_bg = AMBER_LIGHT
        rec_color = AMBER
    else:
        badge_bg = GREEN_LIGHT
        badge_color = GREEN
        badge_text = "Excellent"
        rec_bg = GREEN_LIGHT
        rec_color = GREEN

    lift_badge = Table(
        [[Paragraph(badge_text, ParagraphStyle(
            "Badge", fontName="Helvetica-Bold", fontSize=9,
            textColor=badge_color, alignment=TA_CENTER,
        ))]],
        colWidths=[90],
    )
    lift_badge.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), badge_bg),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("ROUNDEDCORNERS", [4, 4, 4, 4]),
    ]))

    rec_badge = Table(
        [[Paragraph(pa.recommendation_detail, ParagraphStyle(
            "RecBadge", fontName="Helvetica", fontSize=8,
            textColor=rec_color, alignment=TA_CENTER,
        ))]],
        colWidths=[CONTENT_WIDTH / 2 - 20],
    )
    rec_badge.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), rec_bg),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("ROUNDEDCORNERS", [4, 4, 4, 4]),
    ]))

    # Right side column
    right_content = Table(
        [[rating_table], [lift_badge], [Spacer(1, 4)], [rec_badge]],
        colWidths=[CONTENT_WIDTH / 2 - 10],
    )
    right_content.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 10),
    ]))

    # Combine star bars (left) + ratings (right)
    combined = Table(
        [[star_table, right_content]],
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
    ]))

    elements.append(combined)

    # Remove breakdown text
    if pa.what_if.removed_count > 0:
        elements.append(Spacer(1, 4))
        elements.append(Paragraph(
            f"<i>Remove {pa.what_if.remove_breakdown} "
            f"({pa.what_if.removed_count} total) \u2192 "
            f"{pa.what_if.new_total} reviews remaining</i>",
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
        ("BACKGROUND", (0, 0), (-1, 0), INDIGO),
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
    elements.append(Paragraph("Why This Matters", styles["SectionTitle"]))

    prospect = result.terminology.get("prospect", "prospect")
    customers = result.terminology.get("customers", "customers")

    items = [
        ("Search Click-Through Rate",
         f"Businesses with 4.5+ stars see 35-40% of profile visitors take action. "
         f"A higher rating means more {customers} find and choose you from search results."),
        ("Inbound Calls & Leads",
         f"Research shows a half-star improvement can drive 5-9% more revenue. "
         f"Every {prospect} checking your rating becomes more likely to call."),
        ("Competitive Positioning",
         f"In the local 3-pack, star ratings are the first thing a {prospect} compares. "
         f"Even a 0.1-star edge over competitors shifts clicks your way."),
        ("Psychological Trust",
         f"87% of consumers use Google to evaluate local businesses. A single 1-star "
         f"review can drive away 22% of potential {customers}. Removing them rebuilds trust."),
        ("AI & Voice Search Visibility",
         f"AI assistants and voice search prioritize top-rated businesses. A higher "
         f"rating means more visibility as search continues to evolve."),
        ("Ad Performance",
         f"Google Ads with seller ratings above 4.5 stars see significantly higher "
         f"click-through rates. Your review rating directly impacts ad ROI."),
    ]

    # Build 2x3 grid
    grid_rows = []
    for i in range(0, len(items), 2):
        row_cells = []
        for j in range(2):
            if i + j < len(items):
                title, desc = items[i + j]
                cell = Table(
                    [[Paragraph(f"<b>{title}</b>", ParagraphStyle(
                        f"WM_T_{i}{j}", fontName="Helvetica-Bold", fontSize=9,
                        textColor=INDIGO_DARK, spaceAfter=3,
                    ))],
                     [Paragraph(desc, ParagraphStyle(
                         f"WM_D_{i}{j}", fontName="Helvetica", fontSize=8,
                         textColor=SLATE_700, leading=11,
                     ))]],
                    colWidths=[CONTENT_WIDTH / 2 - 16],
                )
                cell.setStyle(TableStyle([
                    ("BACKGROUND", (0, 0), (-1, -1), SLATE_50),
                    ("TOPPADDING", (0, 0), (-1, -1), 8),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
                    ("LEFTPADDING", (0, 0), (-1, -1), 8),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 8),
                    ("ROUNDEDCORNERS", [4, 4, 4, 4]),
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

    # Header with per-review price
    if pricing.original_per_review > 0:
        price_text = (
            f"Cost Per Review Removal: &nbsp;&nbsp;"
            f"<font color='#4F46E5'><b>${pricing.per_review}</b></font>"
            f" &nbsp;<strike><font color='#94A3B8'>${pricing.original_per_review}</font></strike>"
        )
    else:
        price_text = (
            f"Cost Per Review Removal: &nbsp;&nbsp;"
            f"<font color='#4F46E5'><b>${pricing.per_review}</b></font>"
        )

    price_header = Table(
        [[Paragraph(price_text, ParagraphStyle(
            "PriceHeader", fontName="Helvetica-Bold", fontSize=12,
            textColor=SLATE_900,
        ))]],
        colWidths=[CONTENT_WIDTH],
    )
    price_header.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), SLATE_100),
        ("TOPPADDING", (0, 0), (-1, -1), 12),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 12),
        ("LEFTPADDING", (0, 0), (-1, -1), 16),
        ("ROUNDEDCORNERS", [6, 6, 0, 0]),
    ]))
    elements.append(Paragraph("Investment & Pricing", styles["SectionTitle"]))
    elements.append(price_header)

    # Three stat cards
    standard_total = pricing.standard_total
    discounted_total = pricing.discounted_total
    savings = pricing.savings

    card_data = [
        (str(pricing.total_reviews), "Reviews to Remove", SLATE_50, SLATE_700),
        (f"${standard_total:,}", "Standard Total", SLATE_50, SLATE_700),
        (f"${discounted_total:,}", "Bulk Discount Total", INDIGO_LIGHT, INDIGO),
    ]

    card_cells = []
    for value, label, bg, text_color in card_data:
        cell = Table(
            [[Paragraph(value, ParagraphStyle(
                f"PC_{label}", fontName="Helvetica-Bold", fontSize=16,
                textColor=text_color, alignment=TA_CENTER,
            ))],
             [Paragraph(label, ParagraphStyle(
                 f"PL_{label}", fontName="Helvetica", fontSize=8,
                 textColor=SLATE_500, alignment=TA_CENTER,
             ))]],
            colWidths=[CONTENT_WIDTH / 3 - 12],
        )
        cell.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), bg),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("TOPPADDING", (0, 0), (-1, -1), 10),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
            ("ROUNDEDCORNERS", [6, 6, 6, 6]),
        ]))
        card_cells.append(cell)

    cards = Table([card_cells], colWidths=[CONTENT_WIDTH / 3] * 3)
    cards.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 4),
        ("RIGHTPADDING", (0, 0), (-1, -1), 4),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    elements.append(cards)

    # Discount banner
    if pricing.discount_pct > 0 and savings > 0:
        banner = Table(
            [[Paragraph(
                f"<b>{pricing.discount_pct}% Bulk Discount Applied</b> \u2014 "
                f"You save ${savings:,} on your total review removal package.",
                ParagraphStyle(
                    "DiscBanner", fontName="Helvetica", fontSize=9,
                    textColor=GREEN, alignment=TA_CENTER,
                ),
            )]],
            colWidths=[CONTENT_WIDTH],
        )
        banner.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), GREEN_LIGHT),
            ("TOPPADDING", (0, 0), (-1, -1), 8),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
            ("ROUNDEDCORNERS", [0, 0, 6, 6]),
        ]))
        elements.append(banner)

    return elements


def _build_next_steps(result: AnalysisResult, styles):
    """Dark-background CTA box with 4 numbered steps."""
    elements = []

    rows = []
    # Subtitle
    rows.append([Paragraph(
        "Recommended Next Steps",
        ParagraphStyle(
            "NSTitle", fontName="Helvetica-Bold", fontSize=14,
            textColor=WHITE, spaceAfter=4,
        ),
    )])
    rows.append([Paragraph(
        result.next_steps_subtitle,
        ParagraphStyle(
            "NSSub", fontName="Helvetica", fontSize=9,
            textColor=colors.HexColor("#CBD5E1"), leading=12, spaceAfter=10,
        ),
    )])

    for i, step in enumerate(result.next_steps, 1):
        step_content = Table(
            [[
                Paragraph(f"<b>{i}</b>", ParagraphStyle(
                    f"StepNum{i}", fontName="Helvetica-Bold", fontSize=11,
                    textColor=INDIGO_DARK, alignment=TA_CENTER,
                )),
                Table(
                    [[Paragraph(f"<b>{step['title']}</b>", ParagraphStyle(
                        f"StepT{i}", fontName="Helvetica-Bold", fontSize=10,
                        textColor=WHITE, spaceAfter=2,
                    ))],
                     [Paragraph(step["description"], ParagraphStyle(
                         f"StepD{i}", fontName="Helvetica", fontSize=8.5,
                         textColor=colors.HexColor("#CBD5E1"), leading=11,
                     ))]],
                    colWidths=[CONTENT_WIDTH - 60],
                ),
            ]],
            colWidths=[28, CONTENT_WIDTH - 52],
        )
        step_content.setStyle(TableStyle([
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("TOPPADDING", (0, 0), (0, 0), 2),
            ("BACKGROUND", (0, 0), (0, 0), colors.HexColor("#E0E7FF")),
            ("ROUNDEDCORNERS", [4, 4, 4, 4]),
        ]))
        rows.append([step_content])
        rows.append([Spacer(1, 6)])

    box = Table(rows, colWidths=[CONTENT_WIDTH - 32])
    box.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), SLATE_900),
        ("LEFTPADDING", (0, 0), (-1, -1), 16),
        ("RIGHTPADDING", (0, 0), (-1, -1), 16),
        ("TOPPADDING", (0, 0), (0, 0), 16),
        ("BOTTOMPADDING", (-1, -1), (-1, -1), 10),
        ("ROUNDEDCORNERS", [8, 8, 8, 8]),
    ]))

    elements.append(box)
    return elements


def _build_footer(styles):
    """Wise Digital Partners branding and confidentiality note."""
    elements = []
    elements.append(Spacer(1, 8))

    footer_table = Table(
        [[Paragraph(
            "<b>WISE DIGITAL PARTNERS</b> &nbsp;|&nbsp; "
            "This report is confidential and prepared exclusively for the intended recipient.",
            ParagraphStyle(
                "Footer", fontName="Helvetica", fontSize=7,
                textColor=SLATE_500, alignment=TA_CENTER,
            ),
        )]],
        colWidths=[CONTENT_WIDTH],
    )
    footer_table.setStyle(TableStyle([
        ("LINEABOVE", (0, 0), (-1, 0), 0.5, SLATE_200),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
    ]))

    elements.append(footer_table)
    return elements

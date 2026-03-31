import streamlit as st
from models.business import Business, GBPProfile, ReviewDistribution
from models.analysis import PricingInfo
from services.business_type import BUSINESS_TYPES, get_terminology, detect_business_type
from services.analyzer import analyze_business, estimate_distribution
from services.pdf_generator import generate_pdf
from services.google_places import has_api_key, search_places

# ---------- Page config ----------
st.set_page_config(
    page_title="GBP Review Analyzer | Wise Digital Partners",
    page_icon="\u2b50",
    layout="wide",
)

# ---------- Session state defaults ----------
if "step" not in st.session_state:
    st.session_state.step = 1
if "business_name" not in st.session_state:
    st.session_state.business_name = ""
if "business_type" not in st.session_state:
    st.session_state.business_type = "default"
if "profiles" not in st.session_state:
    st.session_state.profiles = []
if "analysis_result" not in st.session_state:
    st.session_state.analysis_result = None


def go_to(step: int):
    st.session_state.step = step


# ---------- Sidebar ----------
with st.sidebar:
    st.markdown("### Wise Digital Partners")
    st.markdown("**GBP Review Analyzer**")
    st.markdown("---")

    steps = {1: "Business Info", 2: "Add Profiles", 3: "Confirm Data", 4: "Results"}
    for num, label in steps.items():
        if num == st.session_state.step:
            st.markdown(f"**\u2192 Step {num}: {label}**")
        elif num < st.session_state.step:
            st.markdown(f"\u2705 Step {num}: {label}")
        else:
            st.markdown(f"\u25cb Step {num}: {label}")

    st.markdown("---")
    if st.button("Start Over"):
        for key in ["step", "business_name", "business_type", "profiles", "analysis_result"]:
            if key in st.session_state:
                del st.session_state[key]
        st.rerun()


# ==========================================================
# STEP 1: Business Info
# ==========================================================
if st.session_state.step == 1:
    st.title("GBP Review Analysis Report")
    st.markdown("Generate a branded review analysis report for your client.")
    st.markdown("---")

    st.subheader("Step 1: Business Information")

    business_name = st.text_input(
        "Business Name",
        value=st.session_state.business_name,
        placeholder="e.g., Smith Plumbing & HVAC",
    )

    # Auto-detect business type from name
    auto_type = detect_business_type(business_name) if business_name else "default"
    type_keys = list(BUSINESS_TYPES.keys())
    default_idx = type_keys.index(auto_type) if auto_type in type_keys else type_keys.index("default")

    business_type = st.selectbox(
        "Business Type",
        options=type_keys,
        format_func=lambda x: BUSINESS_TYPES[x],
        index=default_idx,
        help="Determines terminology in the report (e.g., 'patients' vs 'customers').",
    )

    if business_type:
        terminology = get_terminology(business_type)
        st.caption(
            f"Report will use: **{terminology['customers']}** (customers), "
            f"**{terminology['prospect']}** (prospect), "
            f"**{terminology['review_ask_audience']}** (review ask audience)"
        )

    col1, col2 = st.columns([1, 3])
    with col1:
        if st.button("Next \u2192", type="primary", disabled=not business_name.strip()):
            st.session_state.business_name = business_name.strip()
            st.session_state.business_type = business_type
            go_to(2)
            st.rerun()


# ==========================================================
# STEP 2: Add Profiles
# ==========================================================
elif st.session_state.step == 2:
    st.title("GBP Review Analysis Report")
    st.markdown("---")
    st.subheader(f"Step 2: Add GBP Profiles for {st.session_state.business_name}")

    # --- Google Places Search ---
    if has_api_key():
        with st.expander("\U0001f50d Search Google Places (auto-fill review data)", expanded=False):
            search_query = st.text_input(
                "Search for a business",
                placeholder=f"{st.session_state.business_name} [city, state]",
                key="places_search",
            )
            if search_query and st.button("Search", key="search_btn"):
                with st.spinner("Searching Google Places..."):
                    results = search_places(search_query)
                if results:
                    for r in results[:5]:
                        col1, col2 = st.columns([3, 1])
                        with col1:
                            st.markdown(f"**{r['name']}** — {r['address']}")
                            st.caption(f"Rating: {r['rating']} | Reviews: {r['total_reviews']}")
                        with col2:
                            if st.button("Add", key=f"add_{r['place_id']}"):
                                dist = estimate_distribution(r["total_reviews"], r["rating"])
                                new_profile = {
                                    "name": r["name"],
                                    "url": "",
                                    "total_reviews": r["total_reviews"],
                                    "average_rating": r["rating"],
                                    "five_star": dist.five_star,
                                    "four_star": dist.four_star,
                                    "three_star": dist.three_star,
                                    "two_star": dist.two_star,
                                    "one_star": dist.one_star,
                                    "estimated": True,
                                }
                                st.session_state.profiles.append(new_profile)
                                st.rerun()
                else:
                    st.info("No results found. Try a different search query.")
    else:
        st.info(
            "Google Places API not configured. Add your API key to "
            "`.streamlit/secrets.toml` to enable auto-search. "
            "You can still add profiles manually below."
        )

    st.markdown("---")

    # --- Manual Profile Entry ---
    st.markdown("#### Add a Profile Manually")

    with st.form("add_profile_form", clear_on_submit=True):
        p_name = st.text_input("Profile / Location Name", placeholder="e.g., Downtown Location")
        p_url = st.text_input("Google Maps URL (optional)", placeholder="https://maps.app.goo.gl/...")

        st.markdown("**Review Data**")
        input_mode = st.radio(
            "How would you like to enter review data?",
            ["Star breakdown (recommended)", "Total + average only (will estimate breakdown)"],
            horizontal=True,
        )

        if input_mode == "Star breakdown (recommended)":
            cols = st.columns(5)
            five = cols[0].number_input("5\u2605", min_value=0, value=0, key="f5")
            four = cols[1].number_input("4\u2605", min_value=0, value=0, key="f4")
            three = cols[2].number_input("3\u2605", min_value=0, value=0, key="f3")
            two = cols[3].number_input("2\u2605", min_value=0, value=0, key="f2")
            one = cols[4].number_input("1\u2605", min_value=0, value=0, key="f1")
            total = five + four + three + two + one
            if total > 0:
                avg = round((5*five + 4*four + 3*three + 2*two + 1*one) / total, 2)
            else:
                avg = 0.0
            estimated = False
        else:
            c1, c2 = st.columns(2)
            total = c1.number_input("Total Reviews", min_value=0, value=0)
            avg = c2.number_input("Average Rating", min_value=0.0, max_value=5.0, value=0.0, step=0.1)
            dist = estimate_distribution(total, avg)
            five, four, three, two, one = (
                dist.five_star, dist.four_star, dist.three_star, dist.two_star, dist.one_star,
            )
            estimated = True

        submitted = st.form_submit_button("Add Profile", type="primary")
        if submitted:
            if not p_name.strip():
                st.error("Please enter a profile name.")
            elif total == 0:
                st.error("Please enter review data (total must be > 0).")
            else:
                new_profile = {
                    "name": p_name.strip(),
                    "url": p_url.strip(),
                    "total_reviews": total,
                    "average_rating": avg,
                    "five_star": five,
                    "four_star": four,
                    "three_star": three,
                    "two_star": two,
                    "one_star": one,
                    "estimated": estimated,
                }
                st.session_state.profiles.append(new_profile)
                st.rerun()

    # --- Display Added Profiles ---
    if st.session_state.profiles:
        st.markdown("---")
        st.markdown(f"#### Added Profiles ({len(st.session_state.profiles)})")

        for i, p in enumerate(st.session_state.profiles):
            with st.container():
                col1, col2, col3 = st.columns([3, 2, 1])
                with col1:
                    st.markdown(f"**{p['name']}**")
                    if p.get("url"):
                        st.caption(p["url"])
                with col2:
                    st.markdown(
                        f"Total: **{p['total_reviews']}** | "
                        f"Avg: **{p['average_rating']:.1f}**\u2605"
                    )
                    st.caption(
                        f"5\u2605:{p['five_star']} 4\u2605:{p['four_star']} "
                        f"3\u2605:{p['three_star']} 2\u2605:{p['two_star']} "
                        f"1\u2605:{p['one_star']}"
                        + (" *(estimated)*" if p.get("estimated") else "")
                    )
                with col3:
                    if st.button("\u2716 Remove", key=f"remove_{i}"):
                        st.session_state.profiles.pop(i)
                        st.rerun()
                st.divider()

    # Navigation
    st.markdown("")
    col1, col2, col3 = st.columns([1, 1, 3])
    with col1:
        if st.button("\u2190 Back"):
            go_to(1)
            st.rerun()
    with col2:
        if st.button(
            "Next \u2192",
            type="primary",
            disabled=len(st.session_state.profiles) == 0,
        ):
            go_to(3)
            st.rerun()


# ==========================================================
# STEP 3: Confirm Data
# ==========================================================
elif st.session_state.step == 3:
    st.title("GBP Review Analysis Report")
    st.markdown("---")
    st.subheader("Step 3: Confirm Your Data")

    st.markdown(f"**Business:** {st.session_state.business_name}")
    st.markdown(f"**Type:** {BUSINESS_TYPES.get(st.session_state.business_type, 'Other')}")
    st.markdown("")

    for i, p in enumerate(st.session_state.profiles, 1):
        st.markdown(f"**Profile {i} \u2014 {p['name']}**")
        if p.get("url"):
            st.caption(p["url"])

        cols = st.columns(7)
        cols[0].metric("Total", p["total_reviews"])
        cols[1].metric("Average", f"{p['average_rating']:.1f}\u2605")
        cols[2].metric("5\u2605", p["five_star"])
        cols[3].metric("4\u2605", p["four_star"])
        cols[4].metric("3\u2605", p["three_star"])
        cols[5].metric("2\u2605", p["two_star"])
        cols[6].metric("1\u2605", p["one_star"])

        if p.get("estimated"):
            st.caption("*Star breakdown was estimated from total + average.*")
        st.divider()

    # Pricing config
    st.markdown("#### Pricing Configuration")
    pc1, pc2, pc3 = st.columns(3)
    per_review = pc1.number_input("Per Review Cost ($)", min_value=0, value=795, step=5)
    original_price = pc2.number_input("Original Price ($)", min_value=0, value=895, step=5,
                                       help="Shown as strikethrough. Set to 0 to hide.")
    discount_pct = pc3.number_input("Bulk Discount (%)", min_value=0, max_value=100, value=10)

    st.session_state.pricing_config = {
        "per_review": per_review,
        "original_per_review": original_price,
        "discount_pct": discount_pct,
    }

    st.markdown("")
    col1, col2, col3 = st.columns([1, 1, 3])
    with col1:
        if st.button("\u2190 Back"):
            go_to(2)
            st.rerun()
    with col2:
        if st.button("\u2705 Run Analysis", type="primary"):
            # Build business object
            profiles = []
            any_estimated = False
            for p in st.session_state.profiles:
                dist = ReviewDistribution(
                    five_star=p["five_star"],
                    four_star=p["four_star"],
                    three_star=p["three_star"],
                    two_star=p["two_star"],
                    one_star=p["one_star"],
                )
                profile = GBPProfile(
                    name=p["name"],
                    url=p.get("url", ""),
                    total_reviews=p["total_reviews"],
                    average_rating=p["average_rating"],
                    distribution=dist,
                )
                profiles.append(profile)
                if p.get("estimated"):
                    any_estimated = True

            business = Business(
                name=st.session_state.business_name,
                business_type=st.session_state.business_type,
                profiles=profiles,
            )

            result = analyze_business(business)

            # Apply pricing config
            pricing_cfg = st.session_state.get("pricing_config", {})
            result.pricing = PricingInfo(
                per_review=pricing_cfg.get("per_review", 795),
                original_per_review=pricing_cfg.get("original_per_review", 895),
                total_reviews=result.totals["total_to_remove"],
                discount_pct=pricing_cfg.get("discount_pct", 10),
            )
            result.data_is_estimated = any_estimated

            st.session_state.analysis_result = result
            go_to(4)
            st.rerun()


# ==========================================================
# STEP 4: Results & PDF Download
# ==========================================================
elif st.session_state.step == 4:
    result = st.session_state.analysis_result
    if result is None:
        st.error("No analysis results found. Please go back and run the analysis.")
        if st.button("\u2190 Back to Start"):
            go_to(1)
            st.rerun()
    else:
        st.title(f"Review Analysis: {result.business.name}")
        st.markdown("---")

        # Executive Summary
        st.subheader("Executive Summary")
        st.markdown(result.executive_summary)
        if result.executive_summary_2:
            st.markdown(result.executive_summary_2)

        if result.data_is_estimated:
            st.info(
                "Note: Some star distribution data was estimated from totals and "
                "averages. Actual distribution may vary."
            )

        # Stat cards
        totals = result.totals
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Total Reviews", totals["total_reviews"])
        c2.metric("Reviews to Remove", totals["total_to_remove"])
        c3.metric("Profiles Need Action", f"{totals['profiles_needing_action']} of {totals['total_profiles']}")
        c4.metric("Max Rating Lift", f"+{totals['max_lift']:.2f}")

        st.markdown("---")

        # Per-Profile Analysis
        st.subheader("Profile Analysis")
        for pa in result.profile_analyses:
            profile = pa.profile
            with st.container():
                st.markdown(f"#### {profile.name}")
                if profile.url:
                    st.caption(profile.url)

                col_left, col_right = st.columns([3, 2])

                with col_left:
                    # Star distribution bars
                    dist = profile.distribution
                    star_data = dist.as_dict()
                    pcts = dist.percentages()

                    for star in ["5", "4", "3", "2", "1"]:
                        count = star_data[star]
                        pct = pcts[star]
                        bar_colors = {"5": "#22C55E", "4": "#84CC16", "3": "#EAB308", "2": "#F97316", "1": "#EF4444"}
                        bar_html = (
                            f'<div style="display:flex;align-items:center;margin-bottom:4px;">'
                            f'<span style="width:30px;font-weight:bold;font-size:13px;">{star}\u2605</span>'
                            f'<div style="flex:1;background:#E2E8F0;border-radius:4px;height:16px;margin:0 8px;">'
                            f'<div style="width:{pct}%;background:{bar_colors[star]};border-radius:4px;height:100%;min-width:2px;"></div>'
                            f'</div>'
                            f'<span style="width:40px;text-align:right;font-size:12px;color:#64748B;">{count}</span>'
                            f'<span style="width:45px;text-align:right;font-size:12px;color:#94A3B8;">{pct}%</span>'
                            f'</div>'
                        )
                        st.markdown(bar_html, unsafe_allow_html=True)

                with col_right:
                    m1, m2 = st.columns(2)
                    m1.metric("Current Rating", f"{profile.average_rating:.1f}\u2605")
                    m2.metric("Projected Rating", f"{pa.what_if.new_average:.1f}\u2605")

                    if pa.what_if.rating_lift > 0:
                        st.success(f"\u2191 +{pa.what_if.rating_lift:.2f} rating lift")
                    else:
                        st.success("Excellent \u2014 No action needed")

                    if pa.recommendation == "remove":
                        st.warning(pa.recommendation_detail)
                        st.caption(
                            f"Remove {pa.what_if.remove_breakdown} "
                            f"({pa.what_if.removed_count} total) \u2192 "
                            f"{pa.what_if.new_total} reviews remaining"
                        )
                    else:
                        st.info(pa.recommendation_detail)

                st.divider()

        # Impact Summary Table
        st.subheader("Impact Summary")
        import pandas as pd
        impact_data = []
        for pa in result.profile_analyses:
            p = pa.profile
            impact_data.append({
                "Profile": p.name,
                "Total Reviews": p.distribution.total,
                "Current Rating": f"{p.average_rating:.1f}",
                "Reviews to Remove": pa.what_if.removed_count,
                "Projected Rating": f"{pa.what_if.new_average:.1f}",
                "Rating Lift": f"+{pa.what_if.rating_lift:.2f}" if pa.what_if.rating_lift > 0 else "\u2014",
            })
        impact_data.append({
            "Profile": "TOTALS",
            "Total Reviews": totals["total_reviews"],
            "Current Rating": "\u2014",
            "Reviews to Remove": totals["total_to_remove"],
            "Projected Rating": "\u2014",
            "Rating Lift": f"+{totals['max_lift']:.2f}" if totals["max_lift"] > 0 else "\u2014",
        })
        df = pd.DataFrame(impact_data)
        st.dataframe(df, use_container_width=True, hide_index=True)

        st.markdown("---")

        # Why This Matters
        st.subheader("Why This Matters")
        prospect = result.terminology.get("prospect", "prospect")
        customers = result.terminology.get("customers", "customers")

        items = [
            ("\U0001f50d Search Click-Through Rate",
             f"Businesses with 4.5+ stars see 35-40% of profile visitors take action. "
             f"A higher rating means more {customers} find and choose you from search results."),
            ("\U0001f4de Inbound Calls & Leads",
             f"Research shows a half-star improvement can drive 5-9% more revenue. "
             f"Every {prospect} checking your rating becomes more likely to call."),
            ("\U0001f3af Competitive Positioning",
             f"In the local 3-pack, star ratings are the first thing a {prospect} compares. "
             f"Even a 0.1-star edge over competitors shifts clicks your way."),
            ("\U0001f91d Psychological Trust",
             f"87% of consumers use Google to evaluate local businesses. A single 1-star "
             f"review can drive away 22% of potential {customers}. Removing them rebuilds trust."),
            ("\U0001f916 AI & Voice Search",
             f"AI assistants and voice search prioritize top-rated businesses. A higher "
             f"rating means more visibility as search continues to evolve."),
            ("\U0001f4c8 Ad Performance",
             f"Google Ads with seller ratings above 4.5 stars see significantly higher "
             f"click-through rates. Your review rating directly impacts ad ROI."),
        ]

        cols = st.columns(2)
        for i, (title, desc) in enumerate(items):
            with cols[i % 2]:
                st.markdown(f"**{title}**")
                st.markdown(f"<small>{desc}</small>", unsafe_allow_html=True)
                st.markdown("")

        st.markdown("---")

        # Pricing
        st.subheader("Investment & Pricing")
        pricing = result.pricing

        if pricing.original_per_review > 0:
            st.markdown(
                f"**Cost Per Review Removal:** "
                f"<span style='color:#4F46E5;font-size:1.3em;font-weight:bold;'>${pricing.per_review}</span> "
                f"<s style='color:#94A3B8;'>${pricing.original_per_review}</s>",
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                f"**Cost Per Review Removal:** "
                f"<span style='color:#4F46E5;font-size:1.3em;font-weight:bold;'>${pricing.per_review}</span>",
                unsafe_allow_html=True,
            )

        pc1, pc2, pc3 = st.columns(3)
        pc1.metric("Reviews to Remove", pricing.total_reviews)
        pc2.metric("Standard Total", f"${pricing.standard_total:,}")
        pc3.metric("Bulk Discount Total", f"${pricing.discounted_total:,}")

        if pricing.discount_pct > 0 and pricing.savings > 0:
            st.success(
                f"**{pricing.discount_pct}% Bulk Discount Applied** \u2014 "
                f"You save ${pricing.savings:,} on your total review removal package."
            )

        st.markdown("---")

        # Next Steps
        st.subheader("Recommended Next Steps")
        st.markdown(f"*{result.next_steps_subtitle}*")
        for i, step in enumerate(result.next_steps, 1):
            st.markdown(f"**{i}. {step['title']}**")
            st.markdown(step["description"])

        st.markdown("---")

        # PDF Download
        st.subheader("Download Report")
        st.markdown("Generate and download the branded PDF report for your client.")

        if st.button("Generate PDF", type="primary"):
            with st.spinner("Generating PDF report..."):
                pdf_bytes = generate_pdf(result)
            st.session_state.pdf_bytes = pdf_bytes
            st.rerun()

        if "pdf_bytes" in st.session_state:
            safe_name = result.business.name.replace(" ", "_").replace("/", "_")
            st.download_button(
                label="\u2b07 Download PDF Report",
                data=st.session_state.pdf_bytes,
                file_name=f"GBP_Review_Analysis_{safe_name}.pdf",
                mime="application/pdf",
                type="primary",
            )

        # Back button
        st.markdown("")
        if st.button("\u2190 Back to Confirm"):
            if "pdf_bytes" in st.session_state:
                del st.session_state["pdf_bytes"]
            go_to(3)
            st.rerun()

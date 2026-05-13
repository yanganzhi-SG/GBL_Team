# =========================================================
# REPLACE YOUR OLD show_move FUNCTION WITH THIS
# =========================================================

def show_move(move_name):

    original_move_name = str(move_name).strip()

    clean_move_name = clean_text(move_name)

    # =====================================================
    # FIND MOVE
    # =====================================================

    move_data = fast_moves_df[
        fast_moves_df["CleanMove"] == clean_move_name
    ]

    if move_data.empty:

        move_data = charged_moves_df[
            charged_moves_df["CleanMove"] == clean_move_name
        ]

    # =====================================================
    # MOVE NOT FOUND
    # =====================================================

    if move_data.empty:

        st.warning(f"Move not found: {original_move_name}")
        return

    row = move_data.iloc[0]

    move_type = str(row.get("Type", "Normal")).title().strip()

    category = str(row.get("Category", "Unknown")).strip()

    color = TYPE_COLORS.get(move_type, "#666666")

    # =====================================================
    # TYPE EFFECTIVENESS
    # =====================================================

    effectiveness = TYPE_EFFECTIVENESS.get(
        move_type,
        {
            "strong": [],
            "weak": [],
            "immune": []
        }
    )

    strong_against = effectiveness["strong"]
    weak_against = effectiveness["weak"]
    immune_against = effectiveness["immune"]

    # =====================================================
    # MAIN MOVE CARD
    # =====================================================

    st.markdown(
        f"""
        <div style="
            background-color:{color};
            padding:20px;
            border-radius:15px;
            color:white;
            margin-bottom:15px;
        ">
            <h2 style="margin:0;">
                {original_move_name}
            </h2>

            <p style="
                font-size:18px;
                margin-top:8px;
            ">
                {move_type} • {category}
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    # =====================================================
    # SUPER EFFECTIVE
    # =====================================================

    st.subheader("✅ Super Effective Against")

    if len(strong_against) > 0:

        cols = st.columns(len(strong_against))

        for i, t in enumerate(strong_against):

            c = TYPE_COLORS.get(t, "#666666")

            cols[i].markdown(
                f"""
                <div style="
                    background-color:{c};
                    color:white;
                    padding:10px;
                    border-radius:10px;
                    text-align:center;
                    font-weight:bold;
                    margin-bottom:10px;
                ">
                    {t}
                </div>
                """,
                unsafe_allow_html=True
            )

    else:

        st.write("None")

    # =====================================================
    # NOT VERY EFFECTIVE
    # =====================================================

    st.subheader("❌ Not Very Effective Against")

    if len(weak_against) > 0:

        cols = st.columns(len(weak_against))

        for i, t in enumerate(weak_against):

            c = TYPE_COLORS.get(t, "#666666")

            cols[i].markdown(
                f"""
                <div style="
                    background-color:{c};
                    color:white;
                    padding:10px;
                    border-radius:10px;
                    text-align:center;
                    font-weight:bold;
                    margin-bottom:10px;
                ">
                    {t}
                </div>
                """,
                unsafe_allow_html=True
            )

    else:

        st.write("None")

    # =====================================================
    # IMMUNE
    # =====================================================

    if len(immune_against) > 0:

        st.subheader("🚫 No Effect Against")

        cols = st.columns(len(immune_against))

        for i, t in enumerate(immune_against):

            c = TYPE_COLORS.get(t, "#666666")

            cols[i].markdown(
                f"""
                <div style="
                    background-color:{c};
                    color:white;
                    padding:10px;
                    border-radius:10px;
                    text-align:center;
                    font-weight:bold;
                    margin-bottom:10px;
                ">
                    {t}
                </div>
                """,
                unsafe_allow_html=True
            )

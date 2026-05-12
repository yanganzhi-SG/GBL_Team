# main.py

import streamlit as st
import pandas as pd
import itertools

st.set_page_config(
    page_title="GL Team Forge",
    layout="wide",
)

# =========================================================
# TYPE DATA
# =========================================================

TYPE_WEAKNESSES = {
    "Normal": ["Fighting"],
    "Fire": ["Water", "Ground", "Rock"],
    "Water": ["Electric", "Grass"],
    "Electric": ["Ground"],
    "Grass": ["Fire", "Ice", "Poison", "Flying", "Bug"],
    "Ice": ["Fire", "Fighting", "Rock", "Steel"],
    "Fighting": ["Flying", "Psychic", "Fairy"],
    "Poison": ["Ground", "Psychic"],
    "Ground": ["Water", "Grass", "Ice"],
    "Flying": ["Electric", "Ice", "Rock"],
    "Psychic": ["Bug", "Ghost", "Dark"],
    "Bug": ["Fire", "Flying", "Rock"],
    "Rock": ["Water", "Grass", "Fighting", "Ground", "Steel"],
    "Ghost": ["Ghost", "Dark"],
    "Dragon": ["Ice", "Dragon", "Fairy"],
    "Dark": ["Fighting", "Bug", "Fairy"],
    "Steel": ["Fire", "Fighting", "Ground"],
    "Fairy": ["Poison", "Steel"],
}

TOP_META_THREATS = [
    "Lanturn",
    "Registeel",
    "Medicham",
    "Gligar",
    "Azumarill",
    "Skarmory",
    "Annihilape",
    "Whiscash",
    "Carbink",
    "Bastiodon"
]

TYPE_COLORS = {
    "Normal": "#A8A77A",
    "Fire": "#EE8130",
    "Water": "#6390F0",
    "Electric": "#F7D02C",
    "Grass": "#7AC74C",
    "Ice": "#96D9D6",
    "Fighting": "#C22E28",
    "Poison": "#A33EA1",
    "Ground": "#E2BF65",
    "Flying": "#A98FF3",
    "Psychic": "#F95587",
    "Bug": "#A6B91A",
    "Rock": "#B6A136",
    "Ghost": "#735797",
    "Dragon": "#6F35FC",
    "Dark": "#705746",
    "Steel": "#B7B7CE",
    "Fairy": "#D685AD",
}

# =========================================================
# SESSION STATE
# =========================================================

if "squad" not in st.session_state:
    st.session_state.squad = []

if "data" not in st.session_state:
    st.session_state.data = None

# =========================================================
# HELPERS
# =========================================================

def get_weaknesses(pokemon):
    weak = []

    t1 = pokemon.get("type1", "")
    t2 = pokemon.get("type2", "")

    if t1 in TYPE_WEAKNESSES:
        weak.extend(TYPE_WEAKNESSES[t1])

    if t2 and t2 in TYPE_WEAKNESSES:
        weak.extend(TYPE_WEAKNESSES[t2])

    return list(set(weak))


def role_fit_lead(row):
    return round((row["leadScore"] * 0.6) + (row["consistencyScore"] * 0.4), 1)


def role_fit_switch(row):
    bulk = (row["consistencyScore"] + row["score"]) / 2
    return round((row["switchScore"] * 0.7) + (bulk * 0.3), 1)


def role_fit_closer(row):
    return round((row["closerScore"] * 0.8) + (row["attackerScore"] * 0.2), 1)


def assign_role(row):
    lead = role_fit_lead(row)
    switch = role_fit_switch(row)
    closer = role_fit_closer(row)

    best = max(lead, switch, closer)

    if best == lead:
        return "🟡 Lead"
    elif best == switch:
        return "🟢 Safe Switch"
    else:
        return "🔴 Closer"


def duo_core_score(a, b):
    score = 50

    weak_a = set(get_weaknesses(a))
    weak_b = set(get_weaknesses(b))

    shared = weak_a.intersection(weak_b)

    score -= len(shared) * 8

    cover_bonus = len((weak_a.union(weak_b))) * 2
    score += cover_bonus

    return max(0, min(100, score))


def trio_score(team):
    lead = role_fit_lead(team[0])
    switch = role_fit_switch(team[1])
    closer = role_fit_closer(team[2])

    role_score = (lead + switch + closer) / 3

    type_diversity = len(
        set([team[0]["type1"], team[1]["type1"], team[2]["type1"]])
    )

    diversity_score = type_diversity * 10

    consistency = (
        team[0]["consistencyScore"]
        + team[1]["consistencyScore"]
        + team[2]["consistencyScore"]
    ) / 3

    total = (
        role_score * 0.4
        + diversity_score * 0.3
        + consistency * 0.3
    )

    return round(min(total, 100), 1)


def get_line_structure(score):
    if score >= 82:
        return "⚡ Trio Core"
    elif score >= 70:
        return "🔄 Duo Core + Pivot"
    else:
        return "💥 Unbalanced / Carry Line"


def get_type_archetype(team):
    types = [p["type1"] for p in team]

    if len(set(types)) == 3:
        return "🔵 ABC"
    elif types[1] == types[2]:
        return "🟠 ABB"
    elif types[0] == types[2]:
        return "🟣 ABA"
    else:
        return "🔵 ABC"


def build_card(pokemon):
    role = assign_role(pokemon)

    weak = ", ".join(get_weaknesses(pokemon))

    st.markdown(
        f'''
        <div style="
            border:1px solid #333;
            padding:15px;
            border-radius:15px;
            margin-bottom:10px;
            background:#111;
        ">
            <h3>{pokemon["speciesName"]}</h3>
            <p><b>Score:</b> {pokemon["score"]}</p>
            <p><b>Role:</b> {role}</p>
            <p><b>Types:</b> {pokemon["type1"]} / {pokemon["type2"]}</p>
            <p><b>Fast Move:</b> {pokemon["fastMove"]}</p>
            <p><b>Charged Moves:</b> {pokemon["chargedMove1"]}, {pokemon["chargedMove2"]}</p>
            <p><b>Threatened By:</b> {weak}</p>
        </div>
        ''',
        unsafe_allow_html=True
    )


# =========================================================
# HEADER
# =========================================================

st.title("⚔️ GL Team Forge")
st.caption("Pokémon GO Great League Team Builder")

# =========================================================
# CSV UPLOAD
# =========================================================

uploaded = st.file_uploader(
    "Upload PvPoke CSV",
    type=["csv"]
)

if uploaded:
    df = pd.read_csv(uploaded)

    st.session_state.data = df

    st.success(f"Loaded {len(df)} Pokémon from CSV")

# =========================================================
# SEARCH + SQUAD BUILDER
# =========================================================

if st.session_state.data is not None:

    df = st.session_state.data

    st.subheader("🔍 Search Pokémon")

    current_names = [
        p["speciesName"] for p in st.session_state.squad
    ]

    search = st.text_input(
        "Search Pokémon",
        placeholder="Type Pokémon name..."
    )

    if search:

        filtered = df[
            df["speciesName"]
            .str.lower()
            .str.contains(search.lower(), na=False)
        ]

        filtered = filtered[
            ~filtered["speciesName"].isin(current_names)
        ]

        filtered = filtered.sort_values(
            by="score",
            ascending=False
        ).head(8)

        for _, row in filtered.iterrows():

            col1, col2 = st.columns([5, 1])

            with col1:
                st.markdown(
                    f"""
                    **{row['speciesName']}**
                    | {row['type1']} / {row['type2']}
                    | Score: {row['score']}
                    """
                )

            with col2:
                if st.button(
                    "Add",
                    key=f"add_{row['speciesName']}"
                ):

                    if len(st.session_state.squad) < 6:
                        st.session_state.squad.append(row.to_dict())
                        st.rerun()

    # =====================================================
    # SQUAD DISPLAY
    # =====================================================

    st.divider()

    st.subheader(
        f"👥 Your Squad ({len(st.session_state.squad)}/6)"
    )

    if len(st.session_state.squad) == 6:
        st.warning("Maximum squad size reached.")

    for i, pokemon in enumerate(st.session_state.squad):

        col1, col2 = st.columns([10, 1])

        with col1:
            build_card(pokemon)

        with col2:
            if st.button("❌", key=f"remove_{i}"):
                st.session_state.squad.pop(i)
                st.rerun()

    # =====================================================
    # ANALYSIS
    # =====================================================

    if len(st.session_state.squad) >= 3:

        st.divider()

        st.header("📊 Squad Analysis")

        squad_df = pd.DataFrame(st.session_state.squad)

        avg_score = squad_df["score"].mean()

        unique_types = len(
            set(squad_df["type1"])
        )

        type_diversity_score = unique_types * 10

        # Shared Weaknesses
        weakness_counter = {}

        for p in st.session_state.squad:
            for weak in get_weaknesses(p):
                weakness_counter[weak] = (
                    weakness_counter.get(weak, 0) + 1
                )

        shared = {
            k: v
            for k, v in weakness_counter.items()
            if v >= 3
        }

        # Steel Check
        steel_answer = False

        for p in st.session_state.squad:

            if (
                p["type1"] in ["Ground", "Fire", "Fighting"]
                or p["type2"] in ["Ground", "Fire", "Fighting"]
            ):
                steel_answer = True

        # Duo Cores
        duo_cores = []

        for a, b in itertools.combinations(
            st.session_state.squad, 2
        ):
            score = duo_core_score(a, b)

            if score >= 60:
                duo_cores.append(
                    (
                        a["speciesName"],
                        b["speciesName"],
                        score
                    )
                )

        # Squad Score
        squad_score = (
            avg_score * 0.3
            + len(duo_cores) * 5
            + type_diversity_score * 0.3
        )

        squad_score = round(min(squad_score, 100), 1)

        # =================================================
        # SUMMARY METRICS
        # =================================================

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("Overall Squad Score", squad_score)

        with col2:
            st.metric("Unique Primary Types", unique_types)

        with col3:
            st.metric("Strong Duo Cores", len(duo_cores))

        # =================================================
        # WARNINGS
        # =================================================

        st.subheader("⚠️ Warnings")

        if shared:
            for weak, amount in shared.items():
                st.error(
                    f"🔴 SHARED WEAKNESS — {amount} Pokémon weak to {weak}"
                )

        if not steel_answer:
            st.warning(
                "🟡 MISSING STEEL ANSWER"
            )

        if len(duo_cores) == 0:
            st.warning(
                "🟡 NO DUO CORES DETECTED"
            )

        # =================================================
        # DUO CORES
        # =================================================

        st.subheader("🤝 Duo Cores")

        if duo_cores:

            for a, b, score in duo_cores:

                st.success(
                    f"{a} + {b} — Core Score {score}"
                )

        else:
            st.info("No strong cores found.")

        # =================================================
        # BEST TEAM OF 3
        # =================================================

        st.divider()

        st.header("🏆 Recommended Battle Team")

        all_trios = list(
            itertools.combinations(
                st.session_state.squad,
                3
            )
        )

        scored = []

        for trio in all_trios:

            trio_list = list(trio)

            trio_list = sorted(
                trio_list,
                key=lambda x: role_fit_lead(x),
                reverse=True
            )

            score = trio_score(trio_list)

            scored.append((trio_list, score))

        scored = sorted(
            scored,
            key=lambda x: x[1],
            reverse=True
        )

        best_team, best_score = scored[0]

        lead = best_team[0]
        switch = best_team[1]
        closer = best_team[2]

        line_structure = get_line_structure(best_score)

        archetype = get_type_archetype(best_team)

        st.metric("Battle Trio Score", best_score)

        st.markdown(f"### {line_structure}")
        st.markdown(f"### {archetype}")

        col1, col2, col3 = st.columns(3)

        with col1:
            st.subheader("🟡 LEAD")
            build_card(lead)

        with col2:
            st.subheader("🟢 SAFE SWITCH")
            build_card(switch)

        with col3:
            st.subheader("🔴 CLOSER")
            build_card(closer)

        # =================================================
        # ALL TEAMS
        # =================================================

        st.divider()

        st.header("📋 All Team Combinations")

        for trio, score in scored:

            names = (
                f"{trio[0]['speciesName']} / "
                f"{trio[1]['speciesName']} / "
                f"{trio[2]['speciesName']}"
            )

            st.markdown(
                f"""
                **{names}**
                — Score: {score}
                """
            )

# =========================================================
# FOOTER
# =========================================================

st.divider()

st.caption(
    "GL Team Forge • Streamlit Edition"
)

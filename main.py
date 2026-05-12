import streamlit as st
import pandas as pd
import itertools
import requests

# =====================================================
# 🔑 GEMINI API KEYS (PUT YOUR KEYS HERE)
# =====================================================

GEMINI_KEYS = [
    "AIzaSyBgXQuKQsahIUbfJ2bJ0hewjxhCBThxgZo",
    "AIzaSyBluOzXVSItFulOip-APayR18w1jm1b8QE",
    "AIzaSyC5rnO3ASEVzGd8W-DSAFjgzTrfEA4XzFg",
    "AIzaSyARNFj-KwfpOvyrbqarm9_juitYg_ilb1w",
    "AIzaSyCRj9zqBpQXA3OO-7qrb5xD1GaSulk5bQ4"
]

# =====================================================
# PAGE SETUP
# =====================================================

st.set_page_config(
    page_title="GL AI Team Forge",
    layout="wide"
)

st.title("⚔️ GL AI Team Forge")
st.caption("AI-powered Pokémon GO Great League builder")

# =====================================================
# LOAD CSV
# =====================================================

@st.cache_data
def load_data():

    df = pd.read_csv("cp1500_all_overall_rankings.csv")

    df.columns = df.columns.str.strip()

    df["Pokemon"] = df["Pokemon"].astype(str).str.strip()

    return df


df = load_data()

pokemon_list = sorted(df["Pokemon"].dropna().unique())

# =====================================================
# SESSION STATE
# =====================================================

if "team" not in st.session_state:
    st.session_state.team = []

if "swap_index" not in st.session_state:
    st.session_state.swap_index = 0

# =====================================================
# GEMINI CALL (WITH FALLBACK KEYS)
# =====================================================

def call_gemini(prompt):

    for key in GEMINI_KEYS:

        try:

            url = f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent?key={key}"

            payload = {
                "contents": [
                    {
                        "parts": [
                            {"text": prompt}
                        ]
                    }
                ]
            }

            r = requests.post(url, json=payload, timeout=10)

            if r.status_code == 200:

                data = r.json()

                return data["candidates"][0]["content"]["parts"][0]["text"]

        except:
            continue

    return None

# =====================================================
# AI TEAMMATE SUGGESTION
# =====================================================

def ai_suggest(pokemon):

    prompt = f"""
You are a Pokémon GO Great League expert.

Given Pokémon: {pokemon}

Pick the BEST 2 teammates for a strong 3-Pokémon PvP team.

Rules:
- Must be real Pokémon GO meta picks
- Focus on type coverage + synergy
- Include common meta Pokémon (Lanturn, Skarmory, Galarian Stunfisk, Trevenant, Medicham, etc)

Return EXACT format:

1. <pokemon>
2. <pokemon>
"""

    response = call_gemini(prompt)

    if not response:
        return []

    lines = response.split("\n")

    results = []

    for line in lines:

        line = line.strip()

        if line.startswith(("1.", "2.")):

            name = line.split(".", 1)[1].strip()

            if name in pokemon_list:
                results.append(name)

    return results[:2]

# =====================================================
# FALLBACK SUGGESTION
# =====================================================

def suggest_teammates(pokemon):

    result = ai_suggest(pokemon)

    if len(result) == 2:
        return result

    return list(pd.Series(pokemon_list).sample(2))

# =====================================================
# GET ROW
# =====================================================

def get_row(name):
    return df[df["Pokemon"] == name].iloc[0]

# =====================================================
# SEARCH
# =====================================================

st.subheader("🔍 Search Pokémon")

search = st.text_input("Type Pokémon name")

if search:

    matches = [
        p for p in pokemon_list
        if search.lower() in p.lower()
    ][:10]

    for name in matches:

        row = get_row(name)

        col1, col2, col3 = st.columns([4, 4, 1])

        with col1:
            st.markdown(f"### {name}")
            st.caption(f"{row['Type 1']} / {row.get('Type 2','')}")

        with col2:
            st.write(f"⚡ Fast: {row['Fast Move']}")
            st.write(f"🔥 {row['Charged Move 1']}")
            st.write(f"💥 {row['Charged Move 2']}")

        with col3:

            if st.button("Add", key=f"add_{name}"):

                if len(st.session_state.team) < 6:

                    if name not in st.session_state.team:
                        st.session_state.team.append(name)
                        st.rerun()

# =====================================================
# TEAM DISPLAY + AI SUGGESTIONS
# =====================================================

st.divider()
st.subheader("🛡️ Your Team (AI Suggested Synergy)")

if not st.session_state.team:
    st.info("Add Pokémon to start building your team.")

for i, p in enumerate(st.session_state.team):

    row = get_row(p)

    col1, col2 = st.columns([4, 2])

    with col1:

        st.markdown(f"### {p}")

        st.write(f"⚡ Fast: {row['Fast Move']}")
        st.write(f"🔥 {row['Charged Move 1']}")
        st.write(f"💥 {row['Charged Move 2']}")

    with col2:

        st.markdown("### 🤖 AI Teammates")

        suggestions = suggest_teammates(p)

        if not suggestions:
            st.warning("AI failed, using fallback.")

        for j, s in enumerate(suggestions):

            if s in st.session_state.team:
                st.success(f"✔ {s} (Already in team)")
            else:
                st.info(s)

                if st.button(
                    f"Swap → {s}",
                    key=f"swap_{i}_{j}"
                ):

                    st.session_state.team[i] = s
                    st.rerun()

        if st.button("🔁 New Suggestions", key=f"new_{i}"):

            st.session_state.swap_index += 1
            st.rerun()

# =====================================================
# REMOVE
# =====================================================

for p in st.session_state.team:

    if st.button(f"❌ Remove {p}", key=f"rm_{p}"):

        st.session_state.team.remove(p)
        st.rerun()

# =====================================================
# TEAM POWER (simple)
# =====================================================

def team_power(team):

    return sum(
        float(get_row(p)["Attack"]) +
        float(get_row(p)["Defense"]) +
        float(get_row(p)["Stamina"])
        for p in team
    )

# =====================================================
# BEST TEAM OF 3
# =====================================================

if len(st.session_state.team) >= 3:

    st.divider()
    st.subheader("🏆 Best Team of 3")

    best = None
    best_score = 0

    for combo in itertools.combinations(st.session_state.team, 3):

        score = team_power(combo)

        if score > best_score:
            best_score = score
            best = combo

    if best:

        st.success(
            f"""
🔥 Best Trio:

1. {best[0]}
2. {best[1]}
3. {best[2]}

💪 Power: {best_score}
"""
        )

# =====================================================
# FULL TEAM
# =====================================================

if len(st.session_state.team) == 6:

    st.divider()
    st.subheader("🔥 Full Team Analysis")

    total = team_power(st.session_state.team)

    st.success(
        f"""
Total Power: {total}
Average: {round(total/6, 2)}
"""
    )

# =====================================================
# SIDEBAR
# =====================================================

with st.sidebar:

    st.header("📊 Stats")

    st.write(f"Pokémon loaded: {len(df)}")
    st.write(f"Team size: {len(st.session_state.team)}")

    if st.button("Clear Team"):
        st.session_state.team = []
        st.rerun()

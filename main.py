import streamlit as st
import pandas as pd
import itertools

# =====================================================
# PAGE SETUP
# =====================================================

st.set_page_config(
    page_title="GL Team Forge",
    layout="wide"
)

st.title("⚔️ GL Team Forge")
st.caption("Great League Team Builder (PvPoke CSV)")

# =====================================================
# LOAD CSV FROM GITHUB
# =====================================================

@st.cache_data
def load_data():
    df = pd.read_csv("cp1500_all_overall_rankings.csv")
    df.columns = df.columns.str.strip()
    df["Pokemon"] = df["Pokemon"].astype(str).str.strip()
    return df


df = load_data()
pokemon_list = sorted(df["Pokemon"].unique())

# =====================================================
# MOVE EFFECT DATABASE (PvP style approximations)
# =====================================================

MOVE_EFFECTS = {
    "Body Slam": "No buff/debuff (spam move)",
    "Surf": "No buff/debuff",
    "Hydro Pump": "High damage (no effect)",
    "Ice Beam": "No effect",
    "Thunderbolt": "No effect",
    "Shadow Ball": "No effect",
    "Psychic": "10% chance: -1 Defense",
    "Flamethrower": "10% chance: -1 Attack",
    "Dragon Claw": "No effect",
    "Stone Edge": "No effect",
    "Earthquake": "No effect",
    "Leaf Blade": "No effect",
    "Power-Up Punch": "100% chance: +1 Attack",
    "Psychic Fangs": "100% chance: -1 Defense",
    "Breaking Swipe": "100% chance: -1 Attack",
    "Bubble Beam": "100% chance: -1 Attack",
    "Icy Wind": "100% chance: -1 Attack",
    "Draco Meteor": "100% chance: -2 Attack",
    "Overheat": "100% chance: -2 Attack",
}

def move_effect(move):

    return MOVE_EFFECTS.get(move, "No effect / unknown")

# =====================================================
# SESSION STATE
# =====================================================

if "team" not in st.session_state:
    st.session_state.team = []

# =====================================================
# SEARCH
# =====================================================

st.subheader("🔍 Search Pokémon")

search = st.text_input(
    "Type Pokémon name",
    placeholder="Example: Quagsire"
)

def get_row(name):
    return df[df["Pokemon"] == name].iloc[0]

if search:

    matches = [
        p for p in pokemon_list
        if search.lower() in p.lower()
    ][:10]

    if not matches:
        st.warning("No Pokémon found.")
    else:
        for name in matches:

            row = get_row(name)

            col1, col2, col3 = st.columns([4, 4, 1])

            with col1:
                st.markdown(f"### {name}")
                st.caption(f"{row['Type 1']} / {row.get('Type 2','')}")

            with col2:
                st.write(f"⚡ Fast Move: {row['Fast Move']}")
                st.write(f"🔥 Charge 1: {row['Charged Move 1']}")
                st.write(f"💥 Effect: {move_effect(row['Charged Move 1'])}")

                st.write(f"🔥 Charge 2: {row['Charged Move 2']}")
                st.write(f"💥 Effect: {move_effect(row['Charged Move 2'])}")

            with col3:
                if st.button("Add", key=f"add_{name}"):

                    if len(st.session_state.team) < 6:
                        if name not in st.session_state.team:
                            st.session_state.team.append(name)
                            st.rerun()

# =====================================================
# TEAM DISPLAY
# =====================================================

st.divider()
st.subheader("🛡️ Your Team")

if not st.session_state.team:
    st.info("No Pokémon added yet.")

for p in st.session_state.team:

    row = get_row(p)

    col1, col2 = st.columns([5, 1])

    with col1:

        st.markdown(f"### {p}")

        st.write(f"⚡ Fast Move: {row['Fast Move']}")
        st.write(f"🔥 {row['Charged Move 1']} → {move_effect(row['Charged Move 1'])}")
        st.write(f"🔥 {row['Charged Move 2']} → {move_effect(row['Charged Move 2'])}")

    with col2:

        if st.button("❌", key=f"remove_{p}"):
            st.session_state.team.remove(p)
            st.rerun()

# =====================================================
# SIMPLE TEAM SCORING (based on stats instead of Score column)
# =====================================================

def team_power(team):

    total = 0

    for p in team:

        row = get_row(p)

        total += (
            float(row["Attack"]) +
            float(row["Defense"]) +
            float(row["Stamina"])
        )

    return total

# =====================================================
# BEST TEAM OF 3
# =====================================================

if len(st.session_state.team) >= 3:

    st.divider()
    st.subheader("🏆 Best Team of 3")

    combos = itertools.combinations(st.session_state.team, 3)

    best = None
    best_score = 0

    for c in combos:

        score = team_power(c)

        if score > best_score:
            best_score = score
            best = c

    if best:

        st.success(
            f"""
🔥 Best Trio:

1. {best[0]}
2. {best[1]}
3. {best[2]}

💪 Team Power: {best_score}
"""
        )

# =====================================================
# FULL TEAM
# =====================================================

if len(st.session_state.team) == 6:

    st.divider()
    st.subheader("🔥 Full Team Analysis")

    power = team_power(st.session_state.team)

    st.success(
        f"""
Total Team Power: {power}
Average: {round(power/6, 2)}
"""
    )

# =====================================================
# SIDEBAR
# =====================================================

with st.sidebar:

    st.header("📊 Info")

    st.write(f"Pokémon loaded: {len(df)}")
    st.write(f"Team size: {len(st.session_state.team)}")

    if st.button("Clear Team"):
        st.session_state.team = []
        st.rerun()

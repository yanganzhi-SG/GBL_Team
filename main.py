import streamlit as st
import pandas as pd

# =====================================================
# PAGE CONFIG
# =====================================================

st.set_page_config(
    page_title="Pokémon GO Search",
    layout="wide"
)

st.title("⚔️ Pokémon GO Search")

# =====================================================
# LOAD CSV
# =====================================================

@st.cache_data
def load_data():

    df = pd.read_csv("cp1500_all_overall_rankings.csv")

    df.columns = df.columns.str.strip()

    df["Pokemon"] = (
        df["Pokemon"]
        .astype(str)
        .str.strip()
    )

    return df


df = load_data()

pokemon_names = sorted(
    df["Pokemon"]
    .dropna()
    .unique()
    .tolist()
)

# =====================================================
# TYPE EFFECTIVENESS
# =====================================================

TYPE_EFFECTIVENESS = {
    "water": {
        "strong": ["fire", "ground", "rock"],
        "weak": ["water", "grass", "dragon"]
    },
    "ground": {
        "strong": ["fire", "electric", "poison", "rock", "steel"],
        "weak": ["grass", "bug"],
        "immune": ["flying"]
    },
    "rock": {
        "strong": ["fire", "ice", "flying", "bug"],
        "weak": ["fighting", "ground", "steel"]
    },
    "electric": {
        "strong": ["water", "flying"],
        "weak": ["electric", "grass", "dragon"],
        "immune": ["ground"]
    },
    "grass": {
        "strong": ["water", "ground", "rock"],
        "weak": ["fire", "grass", "poison", "flying", "bug", "dragon", "steel"]
    },
    "ice": {
        "strong": ["grass", "ground", "flying", "dragon"],
        "weak": ["fire", "water", "ice", "steel"]
    },
    "ghost": {
        "strong": ["psychic", "ghost"],
        "weak": ["dark"]
    },
    "dragon": {
        "strong": ["dragon"],
        "weak": ["steel"],
        "immune": ["fairy"]
    },
    "normal": {
        "strong": [],
        "weak": ["rock", "steel"],
        "immune": ["ghost"]
    },
    "fighting": {
        "strong": ["normal", "rock", "steel", "ice", "dark"],
        "weak": ["poison", "flying", "psychic", "bug", "fairy"],
        "immune": ["ghost"]
    },
    "flying": {
        "strong": ["grass", "fighting", "bug"],
        "weak": ["electric", "rock", "steel"]
    }
}

# =====================================================
# MOVE TYPES
# =====================================================

MOVE_TYPES = {
    "Mud Shot": "ground",
    "Mud Bomb": "ground",
    "Earthquake": "ground",
    "Stone Edge": "rock",
    "Body Slam": "normal",
    "Rollout": "rock",
    "Hydro Cannon": "water",
    "Surf": "water",
    "Ice Beam": "ice",
    "Thunderbolt": "electric",
    "Frenzy Plant": "grass",
    "Shadow Ball": "ghost",
    "Dragon Claw": "dragon",
    "Sky Attack": "flying",
    "Counter": "fighting",
    "Lick": "ghost",
    "Spark": "electric",
    "Wing Attack": "flying",
    "Volt Switch": "electric",
    "Water Gun": "water"
}

# =====================================================
# SESSION STATE
# =====================================================

if "selected_pokemon" not in st.session_state:
    st.session_state.selected_pokemon = None

# =====================================================
# SEARCH INPUT
# =====================================================

st.subheader("🔍 Search Pokémon")

search = st.text_input(
    "",
    placeholder="Type: qu"
)

# =====================================================
# LIVE STARTS-WITH SEARCH
# =====================================================

if search:

    search_lower = search.lower().strip()

    matches = [
        p for p in pokemon_names
        if p.lower().startswith(search_lower)
    ]

    if len(matches) > 0:

        st.write("### Pokémon Results")

        for pokemon in matches[:15]:

            # clickable result row
            if st.button(
                f"⚔️ {pokemon}",
                key=f"pokemon_{pokemon}",
                use_container_width=True
            ):
                st.session_state.selected_pokemon = pokemon

    else:
        st.warning("No Pokémon found")

# =====================================================
# SELECTED POKEMON
# =====================================================

selected_pokemon = st.session_state.selected_pokemon

# =====================================================
# DISPLAY POKEMON
# =====================================================

if selected_pokemon:

    pokemon_data = df[df["Pokemon"] == selected_pokemon]

    if not pokemon_data.empty:

        row = pokemon_data.iloc[0]

        st.divider()

        st.header(f"🛡️ {selected_pokemon}")

        type1 = str(row["Type 1"]).lower()

        type2 = ""

        if "Type 2" in row and pd.notna(row["Type 2"]):
            type2 = str(row["Type 2"]).lower()

        # =====================================================
        # TYPES + STATS
        # =====================================================

        col1, col2 = st.columns(2)

        with col1:

            st.subheader("Types")

            st.success(type1.capitalize())

            if type2 and type2 != "nan":
                st.success(type2.capitalize())

        with col2:

            st.subheader("Stats")

            st.write(f"⚔️ Attack: {row['Attack']}")
            st.write(f"🛡️ Defense: {row['Defense']}")
            st.write(f"❤️ Stamina: {row['Stamina']}")
            st.write(f"🔥 CP: {row['CP']}")

        st.divider()

        # =====================================================
        # MOVES
        # =====================================================

        st.subheader("⚔️ Moves")

        move_list = [
            str(row["Fast Move"]).strip(),
            str(row["Charged Move 1"]).strip(),
            str(row["Charged Move 2"]).strip()
        ]

        for move in move_list:

            move_type = MOVE_TYPES.get(move, "unknown")

            with st.container(border=True):

                st.markdown(f"### {move}")

                st.write(f"Type: **{move_type.capitalize()}**")

                if move_type in TYPE_EFFECTIVENESS:

                    data = TYPE_EFFECTIVENESS[move_type]

                    strong = data.get("strong", [])
                    weak = data.get("weak", [])
                    immune = data.get("immune", [])

                    if strong:
                        st.success(
                            "✅ Super Effective Against: "
                            + ", ".join([x.capitalize() for x in strong])
                        )

                    if weak:
                        st.error(
                            "❌ Not Very Effective Against: "
                            + ", ".join([x.capitalize() for x in weak])
                        )

                    if immune:
                        st.warning(
                            "🚫 No Effect Against: "
                            + ", ".join([x.capitalize() for x in immune])
                        )

# =====================================================
# SIDEBAR
# =====================================================

with st.sidebar:

    st.header("📊 Database")

    st.write(f"Pokémon Loaded: {len(pokemon_names)}")

    st.write("✅ Proper starts-with search")
    st.write("✅ Instant clickable list")
    st.write("✅ No dropdown needed")
    st.write("✅ Live filtering")

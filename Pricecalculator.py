import streamlit as st
import pandas as pd

# Pagina configuratie en kleurenschema
st.set_page_config(layout="wide", page_title="Skwirrel Prijsberekening", page_icon=":bar_chart:")

# Pas kleuren aan volgens Skwirrel branding
st.markdown(
    """
    <style>
    :root {
        --primary-color: #C1FF00; /* neon groen accent */
        --secondary-color: #263238; /* donkergrijs voor tekst en headers */
        --bg-color: #F5F7FA; /* lichte achtergrond */
        --sidebar-bg: #E8ECEF; /* iets donkere sidebar */
        --button-bg: #263238;
        --button-text: #FFFFFF;
    }
    /* Body achtergrond */
    .stApp {
        background-color: var(--bg-color) !important;
    }
    /* Titel */
    .css-1d391kg h1, .css-1d391kg h2 {
        color: var(--secondary-color) !important;
    }
    /* Sidebar achtergrond en tekst */
    section[data-testid="stSidebar"] {
        background-color: var(--sidebar-bg) !important;
        color: var(--secondary-color) !important;
    }
    /* Knoppen */
    button {
        background-color: var(--button-bg) !important;
        color: var(--button-text) !important;
    }
    /* Sliders en progress bars accentkleur */
    .stSlider > div > div > div:nth-child(2) {
        background-color: var(--primary-color) !important;
    }
    /* Checkbox en radio accentkleur */
    .stRadio > div[data-baseweb="radio"] input:checked + div > div {
        border-color: var(--primary-color) !important;
        background-color: var(--primary-color) !important;
    }
    .stCheckbox > div[data-baseweb="checkbox"] input:checked + div {
        background-color: var(--primary-color) !important;
        border-color: var(--primary-color) !important;
    }
    /* Zorg sidebar vult 33vw en componenten 100% breedte */
    section[data-testid="stSidebar"] {
        flex: 0 0 33vw !important;
        max-width: 33vw !important;
    }
    div[data-testid="stSidebar"] {
        flex: 0 0 33vw !important;
        max-width: 33vw !important;
    }
    section[data-testid="stSidebar"] .block-container,
    div[data-testid="stSidebar"] .block-container {
        width: 100% !important;
    }
    div[data-testid="stAppViewContainer"] > .main {
        margin-left: 33vw !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Hoofdcode Streamlit app

def main():
    st.title("Skwirrel Prijsberekening Concept")

    # --- Sidebar: Inkoopgegevens fabrikanten ---
    st.sidebar.header("Inkoopgegevens fabrikanten")
    price_per_m2 = st.sidebar.number_input(
        "Inkoopprijs per m² (EUR)", min_value=0.0, value=10.0, format="%.2f"
    )

    # --- Sidebar: Doosinhoud beheren (editable) ---
    st.sidebar.subheader("Doosinhoud beheren")
    default_boxes = [
        {"Doos": "Doos 1", "Opmerking": "Standaard", "Stuks": 10, "m2 per doos": 2.0, "Actief": True, "Introductiedatum": "2025-01-01"},
        {"Doos": "Doos 2", "Opmerking": "opmerking x", "Stuks": 10, "m2 per doos": 2.5, "Actief": True, "Introductiedatum": "2025-02-15"},
        {"Doos": "Doos 3", "Opmerking": "opmerking y", "Stuks": 10, "m2 per doos": 3.0, "Actief": True, "Introductiedatum": "2025-03-10"},
    ]
    df_boxes = pd.DataFrame(default_boxes)
    df_boxes['Introductiedatum'] = pd.to_datetime(df_boxes['Introductiedatum'])
    edited_df = st.sidebar.data_editor(
        df_boxes,
        column_config={
            "Introductiedatum": st.column_config.DateColumn(
                "Introductiedatum",
                help="Datum waarop deze doosinhoud is ingevoerd",
            )
        },
        num_rows="dynamic",
        use_container_width=True,
        key="boxes_editor"
    )

    cleaned = edited_df.dropna(subset=["Doos"])
    active_boxes = cleaned[cleaned["Actief"] == True]
    box_options = active_boxes.to_dict(orient='records')

    if box_options:
        primary_doos = st.sidebar.radio(
            "Selecteer primaire doos", [b["Doos"] for b in box_options]
        )
        cleaned['Primair'] = cleaned['Doos'] == primary_doos
        st.sidebar.write("**Overzicht doosinhoud**")
        st.sidebar.table(cleaned)
    else:
        st.sidebar.error("Voeg eerst minimaal één actieve doos toe in de editor.")
        st.stop()

    # --- Main: Berekening stuksprijs ---
    st.header("Bereken stuksprijs")
    box_data = next(b for b in box_options if b["Doos"] == primary_doos)
    st.write(f"**Geselecteerde doos:** {primary_doos} - {int(box_data['Stuks'])} stuks per doos ({box_data['m2 per doos']} m²)")
    st.write(f"**Introductiedatum:** {box_data['Introductiedatum']} ")

    m2_per_piece = box_data['m2 per doos'] / box_data['Stuks']
    price_per_piece = price_per_m2 * m2_per_piece

    freight_in = st.number_input("Vrachtinkoop per stuk (EUR)", min_value=0.0, value=0.5, format="%.2f")
    markup_percent = st.slider("Opslagpercentage (%)", min_value=0, max_value=100, value=20)
    freight_out = st.number_input("Vrachtverkoop per stuk (EUR)", min_value=0.0, value=0.3, format="%.2f")
    extra_costs = st.number_input("Overige kosten per stuk (EUR)", min_value=0.0, value=0.1, format="%.2f")

    rekenprijs = (
        price_per_piece
        + freight_in
        + (price_per_piece * markup_percent / 100)
        + freight_out
        + extra_costs
    )

    st.subheader("Resultaten")
    st.write(f"- **Prijs per stuk (basis):** €{price_per_piece:.2f}")
    st.write(f"- **Rekenprijs per stuk (vast):** €{rekenprijs:.2f}")

    dealer_price_per_m2 = rekenprijs / m2_per_piece if m2_per_piece else 0
    st.write(f"- **Dealerprijs per m²:** €{dealer_price_per_m2:.2f}")

        # --- Export functionaliteit (placeholder) ---
    if st.button("Exporteer naar ERP/PIM"):
        st.success("Exporteerfunctionaliteit nog in ontwikkeling...")

if __name__ == "__main__":
    main()

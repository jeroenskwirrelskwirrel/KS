import streamlit as st
import pandas as pd

# Zet de layout naar breed viewport
st.set_page_config(layout="wide")

# Streamlit concept voor prijsberekening flow in Skwirrel (standaard styling)

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
        {"Doos": "Doos 1", "Opmerking": "Standaard formaat", "Stuks": 10, "m2 per doos": 2.0, "Actief": True, "Introductiedatum": "2025-01-01"},
        {"Doos": "Doos 2", "Opmerking": "Medium formaat",   "Stuks": 10, "m2 per doos": 2.5, "Actief": True, "Introductiedatum": "2025-02-15"},
        {"Doos": "Doos 3", "Opmerking": "Groot formaat",     "Stuks": 10, "m2 per doos": 3.0, "Actief": True, "Introductiedatum": "2025-03-10"},
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

    # Filter out lege regels en alleen actieve dozen
    cleaned = edited_df.dropna(subset=["Doos"])
    active_boxes = cleaned[cleaned["Actief"] == True].copy()

    if active_boxes.empty:
        st.sidebar.error("Voeg eerst minimaal één actieve doos toe in de editor.")
        st.stop()

    # Kies primaire doos (optioneel, voor detailweergave)
    primary_doos = st.sidebar.radio(
        "Selecteer primaire doos", active_boxes["Doos"].tolist()
    )
    cleaned['Primair'] = cleaned['Doos'] == primary_doos
    st.sidebar.write("**Overzicht doosinhoud**")
    st.sidebar.table(cleaned)

    # --- Main: Berekening voor álle actieve dozen ---
    st.header("Overzicht calculaties per doos")

    # Extra inputwaarden
    freight_in     = st.number_input("Vrachtinkoop per stuk (EUR)",          min_value=0.0, value=0.5, format="%.2f")
    markup_percent = st.slider("Opslagpercentage (%)",                      min_value=0,   max_value=100, value=20)
    freight_out    = st.number_input("Vrachtverkoop per stuk (EUR)",         min_value=0.0, value=0.3, format="%.2f")
    extra_costs    = st.number_input("Overige kosten per stuk (EUR)",        min_value=0.0, value=0.1, format="%.2f")

    # Bereken voor elke doos
    df_calc = active_boxes.copy()
    df_calc['m2_per_piece']      = df_calc['m2 per doos'] / df_calc['Stuks']
    df_calc['price_per_piece']   = price_per_m2 * df_calc['m2_per_piece']
    df_calc['rekenprijs']        = (
        df_calc['price_per_piece']
        + freight_in
        + (df_calc['price_per_piece'] * markup_percent / 100)
        + freight_out
        + extra_costs
    )
    df_calc['dealer_price_per_m2'] = df_calc['rekenprijs'] / df_calc['m2_per_piece']

    # Toon overzichtstabel met maximale breedte
    st.dataframe(
        df_calc[[
            'Doos', 'Opmerking', 'Stuks', 'm2 per doos', 'm2_per_piece',
            'price_per_piece', 'rekenprijs', 'dealer_price_per_m2'
        ]].rename(columns={
            'm2 per doos': 'm2 per doos',
            'm2_per_piece': 'm² per stuk',
            'price_per_piece': '€ basis/stuk',
            'rekenprijs': '€ rekenprijs/stuk',
            'dealer_price_per_m2': '€ dealer/m²'
        }),
        width=1200,
        use_container_width=True
    )

    # --- Optioneel: detailweergave primaire doos ---
    st.subheader(f"Detailberekening voor {primary_doos}")
    detail = df_calc[df_calc['Doos'] == primary_doos].iloc[0]
    st.write(f"- **m² per stuk:** {detail['m2_per_piece']:.3f}")
    st.write(f"- **Prijs per stuk (basis):** €{detail['price_per_piece']:.2f}")
    st.write(f"- **Rekenprijs per stuk (vast):** €{detail['rekenprijs']:.2f}")
    st.write(f"- **Dealerprijs per m²:** €{detail['dealer_price_per_m2']:.2f}")

    # --- Export functionaliteit (placeholder) ---
    if st.button("Exporteer naar ERP/PIM"):
        st.success("Exporteerfunctionaliteit nog in ontwikkeling...")

if __name__ == "__main__":
    main()

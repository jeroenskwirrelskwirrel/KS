import streamlit as st
import pandas as pd

# Zet de layout naar breed viewport
st.set_page_config(layout="wide")

def main():
    st.title("Skwirrel Prijsberekening Concept")

    # --- Sidebar: Dynamische selectie ---
    st.sidebar.header("Dynamische selectie")
    fabrikantenlijst = ["Fabrikant A", "Fabrikant B", "Fabrikant C", "Fabrikant D"]
    assortimentenlijst = ["Basis", "Premium", "Eco"]
    kenmerkenlijst = ["Mozaiek", "Standaardformaat", "Grootformaat"]

    geselecteerde_fabrikanten = st.sidebar.multiselect("Selecteer fabrikant(en)", fabrikantenlijst)
    geselecteerd_assortiment = st.sidebar.selectbox("Selecteer subassortiment", assortimentenlijst)
    geselecteerde_kenmerken = st.sidebar.multiselect("Selecteer kenmerken", kenmerkenlijst)

    # --- Sidebar: Debiteuren ---
    st.sidebar.header("Toepassen op debiteuren")
    debiteurenlijst = [
        "Bouwbedrijf Janssen", "Installatiebedrijf De Groot",
        "Techniek BV", "Partner X", "Demo Klant"
    ]
    geselecteerde_debiteuren = st.sidebar.multiselect("Selecteer één of meerdere debiteuren", debiteurenlijst)

    # --- Artikelcodes ---
    st.sidebar.header("Specifieke artikelcodes (optioneel)")
    artikelcodes_input = st.sidebar.text_area("Geef artikelcodes op (één per regel)", placeholder="123456\n789012\nABCDEF")
    artikelcodes = [code.strip() for code in artikelcodes_input.splitlines() if code.strip()]

    # --- Overzicht selectie ---
    st.info(
        f"**Fabrikanten:** {', '.join(geselecteerde_fabrikanten) if geselecteerde_fabrikanten else 'Geen'} | "
        f"**Assortiment:** {geselecteerd_assortiment} | "
        f"**Kenmerken:** {', '.join(geselecteerde_kenmerken) if geselecteerde_kenmerken else 'Geen'} | "
        f"**Debiteuren:** {', '.join(geselecteerde_debiteuren) if geselecteerde_debiteuren else 'Geen'} | "
        f"**Artikelcodes:** {', '.join(artikelcodes) if artikelcodes else 'Geen'}"
    )

    # --- Inkoopgegevens ---
    st.sidebar.header("Inkoopgegevens fabrikanten")
    price_per_m2 = st.sidebar.number_input("Inkoopprijs per m² (EUR)", min_value=0.0, value=10.0, format="%.2f")

    # --- Kosteninstellingen ---
    st.sidebar.header("Kostenparameters")
    factor = st.sidebar.number_input("Factor", min_value=0.0, value=1.0, format="%.2f")
    markup_percent = st.sidebar.number_input("Opslagpercentage (%)", min_value=0.0, value=20.0, format="%.2f")
    freight_in = st.sidebar.number_input("Vrachtinkoop per stuk (EUR)", min_value=0.0, value=0.5, format="%.2f")
    extra_costs = st.sidebar.number_input("Commissie / overige kosten per stuk (EUR)", min_value=0.0, value=0.1, format="%.2f")
    freight_out = st.sidebar.number_input("Vrachtverkoop per stuk (EUR) (optioneel)", min_value=0.0, value=0.3, format="%.2f")
    round_step = st.sidebar.number_input("Afronden op (EUR)", min_value=0.01, value=0.05, step=0.01, format="%.2f")

    # --- Doosinhoud ---
    st.sidebar.subheader("Doosinhoud beheren")
    default_boxes = [
        {"Doos": "Doos 1", "Opmerking": "Standaard formaat", "Stuks": 10, "m2 per doos": 1.08, "Actief": True, "Introductiedatum": "2025-01-01"},
        {"Doos": "Doos 2", "Opmerking": "Medium formaat", "Stuks": 10, "m2 per doos": 1.078, "Actief": True, "Introductiedatum": "2025-02-15"},
        {"Doos": "Doos 3", "Opmerking": "Groot formaat", "Stuks": 10, "m2 per doos": 1.07, "Actief": True, "Introductiedatum": "2025-03-10"},
    ]
    df_boxes = pd.DataFrame(default_boxes)
    df_boxes['Introductiedatum'] = pd.to_datetime(df_boxes['Introductiedatum'])

    edited_df = st.sidebar.data_editor(
        df_boxes,
        column_config={
            "Introductiedatum": st.column_config.DateColumn("Introductiedatum", help="Datum waarop deze doosinhoud is ingevoerd"),
        },
        num_rows="dynamic",
        use_container_width=True,
        key="boxes_editor"
    )

    # Filter actieve dozen
    cleaned = edited_df.dropna(subset=["Doos"])
    active_boxes = cleaned[cleaned["Actief"] == True].copy()

    if active_boxes.empty:
        st.sidebar.error("Voeg eerst minimaal één actieve doos toe in de editor.")
        st.stop()

    # Kies primaire doos
    primary_doos = st.sidebar.radio("Selecteer primaire doos", active_boxes["Doos"].tolist())
    cleaned['Primair'] = cleaned['Doos'] == primary_doos
    st.sidebar.write("**Overzicht doosinhoud**")
    st.sidebar.table(cleaned)

    # --- Hoofdscherm: Berekening ---
    st.header("Overzicht calculaties per doos")

    df_calc = active_boxes.copy()
    df_calc['m2_per_piece'] = df_calc['m2 per doos'] / df_calc['Stuks']
    df_calc['price_per_piece'] = price_per_m2 * df_calc['m2_per_piece']

    # Berekening met instelbare afronding
    df_calc['tussentotaal'] = df_calc['price_per_piece'] + freight_in + extra_costs
    df_calc['rekenprijs'] = (
        df_calc['tussentotaal'] * factor * (1 + markup_percent / 100)
    ).apply(lambda x: round(x / round_step) * round_step)

    df_calc['dealer_price_per_m2'] = df_calc['rekenprijs'] / df_calc['m2_per_piece']

    st.dataframe(
        df_calc[[
            'Doos', 'Opmerking', 'Stuks', 'm2 per doos', 'm2_per_piece',
            'price_per_piece', 'rekenprijs', 'dealer_price_per_m2'
        ]].rename(columns={
            'm2 per doos': 'm2 per doos',
            'm2_per_piece': 'm² per stuk',
            'price_per_piece': '€ basis/stuk',
            'rekenprijs': '€ rekenprijs/stuk (afgerond)',
            'dealer_price_per_m2': '€ dealer/m²'
        }),
        width=1200,
        use_container_width=True
    )

    # --- Detailweergave ---
    st.subheader(f"Detailberekening voor {primary_doos}")
    detail = df_calc[df_calc['Doos'] == primary_doos].iloc[0]
    st.write(f"- **m² per stuk:** {detail['m2_per_piece']:.3f}")
    st.write(f"- **Prijs per stuk (basis):** €{detail['price_per_piece']:.2f}")
    st.write(f"- **Tussentotaal (basis + vracht + commissie):** €{detail['tussentotaal']:.2f}")
    st.write(f"- **Rekenprijs per stuk (afgerond op €{round_step:.2f}):** €{detail['rekenprijs']:.2f}")
    st.write(f"- **Dealerprijs per m²:** €{detail['dealer_price_per_m2']:.2f}")

    # --- Exportknop ---
    if st.button("Exporteer naar ERP/PIM"):
        st.success("Exporteerfunctionaliteit nog in ontwikkeling...")

if __name__ == "__main__":
    main()

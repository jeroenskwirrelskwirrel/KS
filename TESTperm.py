import streamlit as st
import itertools
import pandas as pd

st.title("Artikelcode Generator met vrije rubrieken")

# Prefix
prefix = st.text_input("Prefix (bijv. AX)", value="AX")

# Aantal rubrieken instellen
num_fields = st.number_input("Aantal rubrieken", min_value=1, value=2, step=1)

# Rubrieken dynamisch invullen
rubrieken = []
for i in range(num_fields):
    st.markdown(f"### Rubriek {i+1}")
    rubriek_naam = st.text_input(f"Naam rubriek {i+1}", key=f"rubriek_naam_{i}")
    aantal_opties = st.number_input(f"Aantal opties voor '{rubriek_naam}'", min_value=1, value=2, step=1, key=f"aantal_opties_{i}")
    
    opties = []
    for j in range(aantal_opties):
        col1, col2 = st.columns(2)
        with col1:
            waarde = st.text_input(f"Waarde {j+1} voor {rubriek_naam}", key=f"{i}_{j}_waarde")
        with col2:
            code = st.text_input(f"Code {j+1} voor {rubriek_naam}", key=f"{i}_{j}_code")
        if waarde and code:
            opties.append((waarde, code))
    
    if rubriek_naam and opties:
        rubrieken.append((rubriek_naam, opties))

# Genereer permutaties
if st.button("Genereer artikelcodes"):
    if not prefix:
        st.warning("Voer een prefix in.")
    elif not rubrieken:
        st.warning("Voeg minstens één rubriek met opties toe.")
    else:
        # Maak alle combinaties van opties over alle rubrieken
        alle_optie_combinaties = list(itertools.product(*[r[1] for r in rubrieken]))
        
        data = []
        for combinatie in alle_optie_combinaties:
            artikelcode = prefix + ''.join([code for _, code in combinatie])
            rij = {"Artikelcode": artikelcode}
            for idx, (rubriek_naam, _) in enumerate(rubrieken):
                waarde, code = combinatie[idx]
                rij[f"{rubriek_naam}"] = waarde
                rij[f"{rubriek_naam}_code"] = code
            data.append(rij)
        
        df = pd.DataFrame(data)
        st.success(f"{len(df)} artikelcodes gegenereerd.")
        st.dataframe(df)
        st.download_button("Download als CSV", df.to_csv(index=False), "artikels.csv", "text/csv")

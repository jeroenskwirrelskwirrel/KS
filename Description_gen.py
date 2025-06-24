import streamlit as st
import pandas as pd
from streamlit_sortables import sort_items

# 🔹 Geïntegreerde productdata
products = [
    {"group": "Selection A", "name": "Solid White Matt 50x120", "code": "KS025905", "shortcode": "A6BF", "ean": "0788845741066", "kleur": "White", "afmeting": "50x120", "afwerking": "Matt"},
    {"group": "Selection A", "name": "Marvel Calacatta Extra 60x60", "code": "KS011096", "shortcode": "7N3A", "ean": "0788845238481", "kleur": "", "afmeting": "60x60", "afwerking": ""},
    {"group": "Selection A", "name": "Marvel Moon Onyx 60x60", "code": "KS015150", "shortcode": "7N3B", "ean": "0788845238498", "kleur": "", "afmeting": "60x60", "afwerking": ""},
    {"group": "Selection A", "name": "Marvel Champagne Onyx 60x60", "code": "KS013893", "shortcode": "7N3C", "ean": "0788845238504", "kleur": "", "afmeting": "60x60", "afwerking": ""},
    {"group": "Selection A", "name": "Marvel Grey Stone 60x60", "code": "KS014193", "shortcode": "7N3F", "ean": "0788845238535", "kleur": "Grey", "afmeting": "60x60", "afwerking": ""},
    {"group": "Selection A", "name": "Marvel Calacatta Extra 60x60 Lapp.", "code": "KS011097", "shortcode": "7N3O", "ean": "0788845241665", "kleur": "", "afmeting": "60x60", "afwerking": "Lapp."},
    {"group": "Selection A", "name": "Marvel Moon Onyx 60x60 Lapp.", "code": "KS007305", "shortcode": "7N3P", "ean": "0788845241672", "kleur": "", "afmeting": "60x60", "afwerking": "Lapp."},
    {"group": "Selection A", "name": "Marvel Champagne Onyx 60x60 Lapp.", "code": "KS011974", "shortcode": "7N3Q", "ean": "0788845241689", "kleur": "", "afmeting": "60x60", "afwerking": "Lapp."},
    {"group": "Selection A", "name": "Marvel Grey Stone 60x60 Lapp.", "code": "KS011976", "shortcode": "7N3T", "ean": "0788845241719", "kleur": "Grey", "afmeting": "60x60", "afwerking": "Lapp."},
    {"group": "Selection A", "name": "Arty 3D Sugar Wave 40x80", "code": "KS019371", "shortcode": "8AWS", "ean": "0788845401793", "kleur": "", "afmeting": "40x80", "afwerking": ""},
    {"group": "Selection A", "name": "Boost Pro Powder Blue 40x80", "code": "KS018342", "shortcode": "8B8B", "ean": "0788845677662", "kleur": "Blue", "afmeting": "40x80", "afwerking": ""},
    {"group": "Selection A", "name": "Boost Pro Clay 40x80", "code": "KS018299", "shortcode": "8B8C", "ean": "0788845677648", "kleur": "Clay", "afmeting": "40x80", "afwerking": ""},
    {"group": "Selection A", "name": "Boost Pro Cream 40x80", "code": "KS018315", "shortcode": "8B8E", "ean": "0788845677631", "kleur": "Cream", "afmeting": "40x80", "afwerking": ""},
    {"group": "Selection A", "name": "Boost Grey 40x80", "code": "KS014975", "shortcode": "8B8G", "ean": "0788845591807", "kleur": "Grey", "afmeting": "40x80", "afwerking": ""},
    {"group": "Selection A", "name": "Boost Pro Ivory 40x80", "code": "KS018331", "shortcode": "8B8I", "ean": "0788845677624", "kleur": "Ivory", "afmeting": "40x80", "afwerking": ""},
]

if "format_parts" not in st.session_state:
    st.session_state.format_parts = []

st.set_page_config(page_title="Productomschrijving Generator", layout="wide")
st.title("🛠️ Productomschrijving Generator")

groups = sorted(set(p["group"] for p in products))
selected_group = st.selectbox("Select Product Group", groups)
selected_products = [p for p in products if p["group"] == selected_group]

st.subheader("✏️ Build Description Format")
with st.form("add_part_form"):
    part_type = st.selectbox("Type", ["Field", "Static"])
    if part_type == "Field":
        field_options = ["name", "kleur", "afmeting", "afwerking", "shortcode"]
        field = st.selectbox("Field", field_options)
        label = field
    else:
        field = st.text_input("Static Text")
        label = field
    submitted = st.form_submit_button("Add to Format")
    if submitted and field:
        st.session_state.format_parts.append({"type": part_type, "value": field, "label": label})

st.subheader("📦 Reorder Format Parts")
if st.session_state.format_parts:
    labels = [f"↕︎ {p['label']}" for p in st.session_state.format_parts]
    sorted_labels = sort_items(labels, direction="vertical")
    new_order = [labels.index(lbl) for lbl in sorted_labels]
    st.session_state.format_parts = [st.session_state.format_parts[i] for i in new_order]

st.subheader("🔍 Preview")
def build_description(product):
    parts = []
    for p in st.session_state.format_parts:
        if p["type"] == "Field":
            parts.append(str(product.get(p["value"], "")))
        else:
            parts.append(p["value"])
    return " - ".join([part for part in parts if part])

preview_data = [{"Product": p["name"], "Description": build_description(p)} for p in selected_products]
st.dataframe(pd.DataFrame(preview_data), use_container_width=True)

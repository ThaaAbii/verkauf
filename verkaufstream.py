import streamlit as st
import json
from datetime import datetime

# Datei für gespeicherte Daten
DATA_FILE = "verkauf_data.json"

# Daten laden und speichern
def load_data():
    with open(DATA_FILE, "r") as file:
        return json.load(file)

def save_data(data):
    with open(DATA_FILE, "w") as file:
        json.dump(data, file, indent=4)

data = load_data()

# Streamlit Layout
st.set_page_config(page_title="Verkaufstool", layout="wide", initial_sidebar_state="expanded")

# Navigation
menu = st.sidebar.radio("Menü", ["Dashboard", "Verkauf hinzufügen", "Kategorien verwalten", "Benutzer"])

# Dashboard
if menu == "Dashboard":
    st.title("📊 Dashboard Übersicht")
    
    total_sales = len(data["sales"])
    total_revenue = sum(sale["amount"] for sale in data["sales"])
    
    st.metric("Gesamtumsatz (€)", f"{total_revenue:.2f}")
    st.metric("Anzahl Verkäufe", total_sales)

    for sale in data["sales"]:
        st.write(f"- {sale['category']}: {sale['amount']} € (Käufer: {sale['buyer']}, Datum: {sale['date']})")

# Verkauf hinzufügen
elif menu == "Verkauf hinzufügen":
    st.title("➕ Verkauf hinzufügen")
    
    parent_category = st.selectbox("Überkategorie", list(data["categories"].keys()))
    if parent_category:
        subcategories = list(data["categories"][parent_category]["subcategories"].keys())
        subcategory = st.selectbox("Unterkategorie", subcategories)
    else:
        subcategory = None
    
    amount = st.number_input("Betrag (€)", min_value=0.0, step=0.01)
    buyer = st.text_input("Käufer")
    description = st.text_area("Beschreibung")
    date = st.date_input("Datum", datetime.now())

    if st.button("Verkauf hinzufügen"):
        new_sale = {
            "id": len(data["sales"]) + 1,
            "user": "admin",  # Ersetze dies durch den aktuellen Benutzer
            "category": f"{parent_category} > {subcategory}",
            "date": str(date),
            "amount": amount,
            "description": description,
            "buyer": buyer
        }
        data["sales"].append(new_sale)
        save_data(data)
        st.success("Verkauf hinzugefügt!")

# Kategorien verwalten
elif menu == "Kategorien verwalten":
    st.title("📂 Kategorien verwalten")
    
    st.subheader("Vorhandene Kategorien")
    for category, details in data["categories"].items():
        st.write(f"**{category}**")
        for subcat, subdetails in details.get("subcategories", {}).items():
            st.write(f"- {subcat}: {subdetails['price']} €")
    
    new_category = st.text_input("Neue Überkategorie")
    if st.button("Überkategorie hinzufügen"):
        if new_category in data["categories"]:
            st.error("Kategorie existiert bereits.")
        else:
            data["categories"][new_category] = {"subcategories": {}}
            save_data(data)
            st.success("Überkategorie hinzugefügt!")

    st.subheader("Neue Unterkategorie hinzufügen")
    parent_category = st.selectbox("Überkategorie auswählen", list(data["categories"].keys()))
    new_subcategory = st.text_input("Neue Unterkategorie")
    price = st.number_input("Preis (€)", min_value=0.0, step=0.01)

    if st.button("Unterkategorie hinzufügen"):
        if parent_category:
            if new_subcategory in data["categories"][parent_category]["subcategories"]:
                st.error("Unterkategorie existiert bereits.")
            else:
                data["categories"][parent_category]["subcategories"][new_subcategory] = {"price": price}
                save_data(data)
                st.success("Unterkategorie hinzugefügt!")
        else:
            st.error("Bitte Überkategorie auswählen.")

# Benutzer
elif menu == "Benutzer":
    st.title("👤 Benutzerverwaltung")
    st.write("Hier können Benutzer verwaltet werden.")

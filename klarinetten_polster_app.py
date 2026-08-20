import streamlit as st
import pandas as pd
import os
from datetime import date

# Set page configuration for mobile devices
st.set_page_config(
    page_title="Klarinetten-Polster Designer",
    page_icon="🎷",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# File path to save the data
DATA_FILE = "klarinetten_polster_daten.csv"

# Load data helper
def load_data():
    if os.path.exists(DATA_FILE):
        try:
            df = pd.read_csv(DATA_FILE)
            # Ensure proper date formatting
            if "Einbaudatum" in df.columns:
                df["Einbaudatum"] = pd.to_datetime(df["Einbaudatum"]).dt.date
            return df
        except Exception as e:
            st.error(f"Fehler beim Laden der Daten: {e}")
            return create_empty_df()
    else:
        return create_empty_df()

# Create empty dataframe with correct structure
def create_empty_df():
    return pd.DataFrame(columns=[
        "Einbaudatum",
        "Kunde_Besitzer",
        "Hersteller_Modell",
        "Instrumenten_Typ",
        "System",
        "Top_Layer_Soll_mm",
        "Backplate_Soll_mm",
        "Kerf_mm",
        "Top_Layer_Laser_mm",
        "Backplate_Laser_mm",
        "Dicke_mm",
        "Material_Top",
        "Material_Back"
    ])

# Save data helper
def save_data(df):
    try:
        df.to_csv(DATA_FILE, index=False)
    except Exception as e:
        st.error(f"Fehler beim Speichern der Daten: {e}")

# Main App Title
st.title("🎷 Klarinetten-Polster App")
st.markdown("Erfasse, berechne und verwalte die Abmessungen deiner Polster – optimiert für dein Smartphone.")

# --- SECTION 1: ADD NEW ENTRY ---
with st.expander("➕ Neues Polster erfassen", expanded=True):
    st.subheader("1. Kundendaten & Instrument")
    
    col1, col2 = st.columns(2)
    with col1:
        kunde = st.text_input("Kunde / Besitzer", placeholder="z. B. Max Mustermann")
        instrument = st.selectbox(
            "Instrumenten-Typ",
            ["Bb/A-Klarinette", "Es-Klarinette", "Bass-Klarinette"]
        )
    with col2:
        hersteller_modell = st.text_input("Hersteller & Modell", placeholder="z. B. Buffet R13")
        system = st.selectbox("System", ["Boehm (Französisch)", "Oehler (Deutsch)"])

    st.divider()
    st.subheader("2. Polster-Abmessungen & Laser-Kerf")
    
    col3, col4, col5 = st.columns(3)
    with col3:
        # Standard values for quick input or free manual input
        top_soll = st.number_input(
            "Top Layer Ø (Soll in mm)", 
            min_value=0.0, 
            max_value=30.0, 
            value=12.0, 
            step=0.1,
            help="Der gewünschte Fertig-Durchmesser der oberen Schicht"
        )
    with col4:
        back_soll = st.number_input(
            "Backplate Ø (Soll in mm)", 
            min_value=0.0, 
            max_value=30.0, 
            value=11.8, 
            step=0.1,
            help="Der gewünschte Fertig-Durchmesser der Rückplatte"
        )
    with col5:
        kerf = st.number_input(
            "Laser-Kerf (Schwund in mm)", 
            min_value=0.00, 
            max_value=2.00, 
            value=0.15, 
            step=0.01,
            help="Die Breite des Laserstrahls (Schnittverlust). Wird zum Soll-Durchmesser addiert."
        )

    # Kerf calculations
    top_laser = round(top_soll + kerf, 2) if top_soll > 0 else 0.0
    back_laser = round(back_soll + kerf, 2) if back_soll > 0 else 0.0

    # Display calculated laser dimensions
    st.info(
        f"📐 **Berechnete Laser-Schnittmaße (Soll + Kerf):**\n"
        f"*   **Top Layer Laser-Durchmesser:** `{top_laser} mm`\n"
        f"*   **Backplate Laser-Durchmesser:** `{back_laser} mm`"
    )

    st.divider()
    st.subheader("3. Material & Stärke")
    
    col6, col7, col8 = st.columns(3)
    with col6:
        dicke = st.selectbox("Dicke / Stärke (mm)", ["2.0", "2.5", "3.0", "3.5"])
    with col7:
        material_top = st.selectbox("Material Top Layer", ["EVA Foam", "Whiteboard", "Andere"])
    with col8:
        material_back = st.selectbox("Material Backplate", ["Whiteboard", "EVA Foam", "Andere"])

    # Optional Custom Materials
    if material_top == "Andere":
        material_top = st.text_input("Anderes Top-Material", placeholder="z. B. Leder")
    if material_back == "Andere":
        material_back = st.text_input("Anderes Backplate-Material", placeholder="z. B. Kork")

    # Date
    einbaudatum = st.date_input("Einbaudatum", date.today())

    # Add button
    if st.button("💾 Polster-Daten speichern", type="primary", use_container_width=True):
        df_current = load_data()
        
        # New record dictionary
        new_record = {
            "Einbaudatum": einbaudatum,
            "Kunde_Besitzer": kunde if kunde else "Unbekannt",
            "Hersteller_Modell": hersteller_modell if hersteller_modell else "Unbekannt",
            "Instrumenten_Typ": instrument,
            "System": system,
            "Top_Layer_Soll_mm": top_soll,
            "Backplate_Soll_mm": back_soll,
            "Kerf_mm": kerf,
            "Top_Layer_Laser_mm": top_laser,
            "Backplate_Laser_mm": back_laser,
            "Dicke_mm": float(dicke),
            "Material_Top": material_top,
            "Material_Back": material_back
        }
        
        # Append and save
        df_new = pd.concat([df_current, pd.DataFrame([new_record])], ignore_index=True)
        save_data(df_new)
        st.success("✅ Daten erfolgreich gespeichert!")
        st.rerun()

# --- SECTION 2: VIEW AND EDIT DATA ---
st.header("📋 Gespeicherte Polster-Daten")

df_data = load_data()

if df_data.empty:
    st.info("Noch keine Daten vorhanden. Nutze das obige Formular, um deinen ersten Eintrag hinzuzufügen.")
else:
    # Sidebar Search and Filter options for mobile
    st.markdown("### 🔍 Filtern & Suchen")
    filter_col1, filter_col2 = st.columns(2)
    with filter_col1:
        search_query = st.text_input("Nach Kunde oder Modell suchen", "").strip()
    with filter_col2:
        instrument_filter = st.multiselect(
            "Nach Instrument filtern", 
            options=df_data["Instrumenten_Typ"].unique(),
            default=df_data["Instrumenten_Typ"].unique()
        )
        
    # Apply filters
    filtered_df = df_data.copy()
    if search_query:
        filtered_df = filtered_df[
            filtered_df["Kunde_Besitzer"].str.contains(search_query, case=False, na=False) |
            filtered_df["Hersteller_Modell"].str.contains(search_query, case=False, na=False)
        ]
    if instrument_filter:
        filtered_df = filtered_df[filtered_df["Instrumenten_Typ"].isin(instrument_filter)]

    # Dynamic Data Editor (directly edit and delete rows!)
    st.markdown("💡 *Du kannst Werte direkt in der Tabelle antippen, um sie zu editieren. Um eine Zeile zu löschen, markiere sie links und drücke 'Entf' (oder nutze das Mülleimer-Symbol).*")
    
    edited_df = st.data_editor(
        filtered_df,
        num_rows="dynamic",
        use_container_width=True,
        key="data_editor_widget"
    )

    # Save edits button
    if st.button("🔄 Änderungen in Tabelle speichern", use_container_width=True):
        # Merge edited data back to original in case filters were active
        if len(filtered_df) == len(df_data):
            save_data(edited_df)
        else:
            # Update only filtered/edited rows
            non_filtered_df = df_data[~df_data.index.isin(filtered_df.index)]
            final_df = pd.concat([non_filtered_df, edited_df], ignore_index=True)
            save_data(final_df)
            
        st.success("🎉 Änderungen erfolgreich übernommen!")
        st.rerun()

    # --- CSV Export ---
    st.divider()
    csv = df_data.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Alle Daten als CSV herunterladen (Backup)",
        data=csv,
        file_name="klarinetten_polster_backup.csv",
        mime="text/csv",
        use_container_width=True
    )

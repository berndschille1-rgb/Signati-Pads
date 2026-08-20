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
            # Ensure Anzahl column exists
            if "Anzahl" not in df.columns:
                df["Anzahl"] = 1
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
        "Material_Back",
        "Anzahl"
    ])

# Save data helper
def save_data(df):
    try:
        df.to_csv(DATA_FILE, index=False)
    except Exception as e:
        st.error(f"Fehler beim Speichern der Daten: {e}")

# Main App Title
st.title("🎷 Klarinetten-Polster App v4")
st.markdown("Erfasse beliebig viele Polster nacheinander mit Stückzahl für einen Kunden – optimiert für einfache Smartphone-Bedienung.")

# Initialize session state for current order list if not present
if "current_order_pads" not in st.session_state:
    st.session_state.current_order_pads = []

# --- SECTION 1: ADD NEW ENTRY (ULTRA MOBILE FRIENDLY) ---
with st.expander("➕ Neuen Auftrag (mehrere Polster) erfassen", expanded=True):
    st.subheader("1. Kundendaten & Globaler Laser-Kerf")
    
    col1, col2 = st.columns(2)
    with col1:
        kunde = st.text_input("Kunde / Besitzer", placeholder="z. B. Max Mustermann")
        instrument = st.selectbox(
            "Instrumenten-Typ",
            ["Bb/A-Klarinette", "Es-Klarinette", "Bass-Klarinette"]
        )
        einbaudatum = st.date_input("Einbaudatum", date.today())
    with col2:
        hersteller_modell = st.text_input("Hersteller & Modell", placeholder="z. B. Buffet R13")
        system = st.selectbox("System", ["Boehm (Französisch)", "Oehler (Deutsch)"])
        
        # Kerf input is now global and extremely easy to set once for the whole order!
        kerf = st.number_input(
            "Laser-Kerf (Schwund in mm)", 
            min_value=0.00, 
            max_value=2.00, 
            value=0.15, 
            step=0.01,
            help="Der Schnittverlust deines Lasers. Wird automatisch zu allen Polster-Durchmessern dieses Auftrags addiert."
        )

    st.divider()
    st.subheader("2. Polster nacheinander hinzufügen")
    st.markdown("Gib die Maße, Stärke und die **Stückzahl** des Polsters ein.")
    
    # Simple form inputs for one pad at a time (extremely reliable on mobile!)
    col3, col4, col5 = st.columns(3)
    with col3:
        top_soll = st.number_input(
            "Top Layer Ø (Soll in mm)", 
            min_value=0.0, 
            max_value=30.0, 
            value=12.0, 
            step=0.1,
            key="input_top_soll"
        )
    with col4:
        back_soll = st.number_input(
            "Backplate Ø (Soll in mm)", 
            min_value=0.0, 
            max_value=30.0, 
            value=11.8, 
            step=0.1,
            key="input_back_soll"
        )
    with col5:
        dicke = st.selectbox(
            "Dicke / Stärke (mm)", 
            [2.0, 2.5, 3.0, 3.5], 
            index=1,
            key="input_dicke"
        )

    col6, col7, col8 = st.columns(3)
    with col6:
        material_top = st.selectbox(
            "Material Top Layer", 
            ["EVA Foam", "Whiteboard", "Leder", "Kork", "Andere"],
            key="input_material_top"
        )
        if material_top == "Andere":
            material_top = st.text_input("Anderes Top-Material", placeholder="z. B. Filz", key="custom_material_top")
    with col7:
        material_back = st.selectbox(
            "Material Backplate", 
            ["Whiteboard", "EVA Foam", "Kork", "Leder", "Andere"],
            key="input_material_back"
        )
        if material_back == "Andere":
            material_back = st.text_input("Anderes Back-Material", placeholder="z. B. Holz", key="custom_material_back")
    with col8:
        anzahl = st.number_input(
            "Anzahl (Stück)",
            min_value=1,
            max_value=100,
            value=1,
            step=1,
            key="input_anzahl",
            help="Wie viele Polster mit diesen exakten Maßen werden benötigt?"
        )

    # Real-time calculation preview for the single pad
    top_laser = round(top_soll + kerf, 2) if top_soll > 0 else 0.0
    back_laser = round(back_soll + kerf, 2) if back_soll > 0 else 0.0

    st.markdown(
        f"📐 **Vorschau für dieses Polster:** "
        f"Laser Top: **`{top_laser} mm`** | Laser Backplate: **`{back_laser} mm`** | Stückzahl: **`{anzahl}x`**"
    )

    # Button to add this single pad to the list
    if st.button("➕ Polster zur Liste hinzufügen", use_container_width=True):
        if top_soll <= 0 or back_soll <= 0:
            st.error("Bitte gib gültige Durchmesser für Top Layer und Backplate an.")
        else:
            new_pad = {
                "Top_Soll_mm": top_soll,
                "Back_Soll_mm": back_soll,
                "Dicke_mm": float(dicke),
                "Material_Top": material_top,
                "Material_Back": material_back,
                "Top_Laser_mm": top_laser,
                "Back_Laser_mm": back_laser,
                "Anzahl": int(anzahl)
            }
            st.session_state.current_order_pads.append(new_pad)
            st.toast(f"{anzahl}x Polster {top_soll}mm / {back_soll}mm hinzugefügt!", icon="✅")

    # --- SECTION 1B: CURRENT ORDER LIST ---
    if st.session_state.current_order_pads:
        st.divider()
        st.subheader(f"📋 Hinzugefügte Polster für diesen Auftrag ({sum(pad['Anzahl'] for pad in st.session_state.current_order_pads)} Polster gesamt)")
        
        # Display as a clean, read-only table for review
        order_df = pd.DataFrame(st.session_state.current_order_pads)
        # Rename columns for user-friendly preview
        display_order_df = order_df.rename(columns={
            "Top_Soll_mm": "Top Ø Soll (mm)",
            "Back_Soll_mm": "Backplate Ø Soll (mm)",
            "Dicke_mm": "Dicke (mm)",
            "Material_Top": "Material Top",
            "Material_Back": "Material Back",
            "Top_Laser_mm": "📐 Top Laser (mm)",
            "Back_Laser_mm": "📐 Backplate Laser (mm)",
            "Anzahl": "Anzahl (Stück)"
        })
        st.dataframe(display_order_df, use_container_width=True)

        col_btn1, col_btn2 = st.columns(2)
        with col_btn1:
            if st.button("🗑️ Liste leeren", type="secondary", use_container_width=True):
                st.session_state.current_order_pads = []
                st.rerun()
        with col_btn2:
            if st.button("💾 Gesamten Auftrag speichern", type="primary", use_container_width=True):
                df_current = load_data()
                
                records_to_add = []
                for pad in st.session_state.current_order_pads:
                    records_to_add.append({
                        "Einbaudatum": einbaudatum,
                        "Kunde_Besitzer": kunde if kunde else "Unbekannt",
                        "Hersteller_Modell": hersteller_modell if hersteller_modell else "Unbekannt",
                        "Instrumenten_Typ": instrument,
                        "System": system,
                        "Top_Layer_Soll_mm": pad["Top_Soll_mm"],
                        "Backplate_Soll_mm": pad["Back_Soll_mm"],
                        "Kerf_mm": kerf,
                        "Top_Layer_Laser_mm": pad["Top_Laser_mm"],
                        "Backplate_Laser_mm": pad["Back_Laser_mm"],
                        "Dicke_mm": pad["Dicke_mm"],
                        "Material_Top": pad["Material_Top"],
                        "Material_Back": pad["Material_Back"],
                        "Anzahl": int(pad["Anzahl"])
                    })
                
                df_new = pd.concat([df_current, pd.DataFrame(records_to_add)], ignore_index=True)
                save_data(df_new)
                
                # Clear order list
                st.session_state.current_order_pads = []
                st.success(f"🎉 Erfolgreich {len(records_to_add)} Polstertypen mit insgesamt {sum(r['Anzahl'] for r in records_to_add)} Stück für {kunde if kunde else 'Unbekannt'} gespeichert!")
                st.rerun()

# --- SECTION 2: VIEW AND EDIT DATABASE ---
st.header("🗄️ Gesamte Polster-Datenbank")

df_data = load_data()

if df_data.empty:
    st.info("Noch keine Daten in der Datenbank vorhanden. Nutze das Formular oben, um deinen ersten Auftrag zu speichern.")
else:
    # Search and Filter options
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

    # Dynamic Data Editor for managing historical data
    st.markdown("💡 *Du kannst Werte in der Datenbank-Tabelle direkt antippen, um sie nachträglich zu editieren. Um eine Zeile zu löschen, markiere sie links und drücke 'Entf' (oder nutze das Mülleimer-Symbol). Vergiss nicht, danach auf 'Änderungen in Tabelle speichern' zu klicken.*")
    
    # Configure columns for database data editor
    edited_df = st.data_editor(
        filtered_df,
        num_rows="dynamic",
        use_container_width=True,
        column_config={
            "Anzahl": st.column_config.NumberColumn("Anzahl", min_value=1, max_value=500, step=1, format="%d")
        },
        key="database_editor_widget"
    )

    # Save edits button
    if st.button("🔄 Änderungen in Tabelle speichern", use_container_width=True):
        if len(filtered_df) == len(df_data):
            save_data(edited_df)
        else:
            # Update only filtered/edited rows
            non_filtered_df = df_data[~df_data.index.isin(filtered_df.index)]
            final_df = pd.concat([non_filtered_df, edited_df], ignore_index=True)
            save_data(final_df)
            
        st.success("🎉 Änderungen erfolgreich in der Datenbank übernommen!")
        st.rerun()

    # --- CSV Export ---
    st.divider()
    csv = df_data.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Gesamte Datenbank als CSV herunterladen (Backup)",
        data=csv,
        file_name="klarinetten_polster_backup.csv",
        mime="text/csv",
        use_container_width=True
    )

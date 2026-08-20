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
st.title("🎷 Klarinetten-Polster App v2")
st.markdown("Erfasse mehrere Polster-Größen gleichzeitig für einen Kunden – optimiert für dein Smartphone.")

# --- SECTION 1: ADD NEW ENTRY (MULTIPLE PADS) ---
with st.expander("➕ Neuen Auftrag (mehrere Polster) erfassen", expanded=True):
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

    einbaudatum = st.date_input("Einbaudatum", date.today())

    st.divider()
    st.subheader("2. Polster-Liste für diesen Kunden")
    st.markdown("Trage hier alle Polstergrößen für diesen Auftrag ein. Du kannst über das `+` Symbol unten links neue Zeilen hinzufügen.")

    # Initialize temporary pads dataframe in session state if not present
    if "temp_pads" not in st.session_state:
        st.session_state.temp_pads = pd.DataFrame([
            {
                "Top_Soll_mm": 12.0,
                "Back_Soll_mm": 11.8,
                "Dicke_mm": 2.5,
                "Material_Top": "EVA Foam",
                "Material_Back": "Whiteboard",
                "Kerf_mm": 0.15
            }
        ])

    # Display the interactive data editor for the pad list
    edited_temp_df = st.data_editor(
        st.session_state.temp_pads,
        num_rows="dynamic",
        use_container_width=True,
        column_config={
            "Top_Soll_mm": st.column_config.NumberColumn("Top Ø Soll (mm)", min_value=0.0, max_value=30.0, step=0.1, format="%.1f", required=True),
            "Back_Soll_mm": st.column_config.NumberColumn("Backplate Ø Soll (mm)", min_value=0.0, max_value=30.0, step=0.1, format="%.1f", required=True),
            "Dicke_mm": st.column_config.SelectboxColumn("Dicke (mm)", options=[2.0, 2.5, 3.0, 3.5], required=True),
            "Material_Top": st.column_config.SelectboxColumn("Material Top", options=["EVA Foam", "Whiteboard", "Leder", "Kork", "Andere"], required=True),
            "Material_Back": st.column_config.SelectboxColumn("Material Back", options=["Whiteboard", "EVA Foam", "Kork", "Leder", "Andere"], required=True),
            "Kerf_mm": st.column_config.NumberColumn("Kerf (mm)", min_value=0.0, max_value=2.0, step=0.01, format="%.2f", required=True)
        },
        key="temp_pads_editor"
    )

    # Calculate real-time preview of laser dimensions
    if not edited_temp_df.empty:
        preview_df = edited_temp_df.copy()
        preview_df["Top_Soll_mm"] = pd.to_numeric(preview_df["Top_Soll_mm"], errors="coerce").fillna(0.0)
        preview_df["Back_Soll_mm"] = pd.to_numeric(preview_df["Back_Soll_mm"], errors="coerce").fillna(0.0)
        preview_df["Kerf_mm"] = pd.to_numeric(preview_df["Kerf_mm"], errors="coerce").fillna(0.0)
        
        preview_df["Top_Laser_mm"] = (preview_df["Top_Soll_mm"] + preview_df["Kerf_mm"]).round(2)
        preview_df["Back_Laser_mm"] = (preview_df["Back_Soll_mm"] + preview_df["Kerf_mm"]).round(2)
        
        # Format preview columns for beautiful display
        st.markdown("🔍 **Vorschau der berechneten Laser-Schnittmaße:**")
        display_preview = preview_df.copy()
        display_preview.columns = [
            "Top Soll (mm)", "Backplate Soll (mm)", "Dicke (mm)", 
            "Material Top", "Material Back", "Kerf (mm)", 
            "📐 Top Laser (mm)", "📐 Backplate Laser (mm)"
        ]
        st.dataframe(display_preview[["Top Soll (mm)", "📐 Top Laser (mm)", "Backplate Soll (mm)", "📐 Backplate Laser (mm)", "Dicke (mm)"]], use_container_width=True)

    # Save button for the entire list
    if st.button("💾 Gesamten Auftrag (alle Polster) speichern", type="primary", use_container_width=True):
        if edited_temp_df.empty:
            st.error("Bitte füge mindestens ein Polster hinzu.")
        else:
            df_current = load_data()
            
            records_to_add = []
            for _, row in preview_df.iterrows():
                records_to_add.append({
                    "Einbaudatum": einbaudatum,
                    "Kunde_Besitzer": kunde if kunde else "Unbekannt",
                    "Hersteller_Modell": hersteller_modell if hersteller_modell else "Unbekannt",
                    "Instrumenten_Typ": instrument,
                    "System": system,
                    "Top_Layer_Soll_mm": row["Top_Soll_mm"],
                    "Backplate_Soll_mm": row["Back_Soll_mm"],
                    "Kerf_mm": row["Kerf_mm"],
                    "Top_Layer_Laser_mm": row["Top_Laser_mm"],
                    "Backplate_Laser_mm": row["Back_Laser_mm"],
                    "Dicke_mm": float(row["Dicke_mm"]),
                    "Material_Top": row["Material_Top"],
                    "Material_Back": row["Material_Back"]
                })
            
            df_new = pd.concat([df_current, pd.DataFrame(records_to_add)], ignore_index=True)
            save_data(df_new)
            
            # Clear temporary state so next order is fresh
            st.session_state.temp_pads = pd.DataFrame([
                {
                    "Top_Soll_mm": 12.0,
                    "Back_Soll_mm": 11.8,
                    "Dicke_mm": 2.5,
                    "Material_Top": "EVA Foam",
                    "Material_Back": "Whiteboard",
                    "Kerf_mm": 0.15
                }
            ])
            
            st.success(f"✅ {len(records_to_add)} Polster erfolgreich für {kunde if kunde else 'Unbekannt'} gespeichert!")
            st.rerun()

# --- SECTION 2: VIEW AND EDIT DATA ---
st.header("📋 Gespeicherte Polster-Daten")

df_data = load_data()

if df_data.empty:
    st.info("Noch keine Daten vorhanden. Nutze das obige Formular, um deinen ersten Eintrag hinzuzufügen.")
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

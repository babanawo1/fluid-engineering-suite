import pathlib
import streamlit as st
import pandas as pd
from utils.validation import validate_csv_dataset
from utils.plotting import create_porosity_histogram, create_poro_perm_crossplot

st.set_page_config(
    page_title="Rock & Fluid Dashboard | Engineering Suite",
    page_icon="🪨",
    layout="wide"
)

st.title("🪨 Module C: Rock & Fluid Data Dashboard")
st.markdown(
    """
    Perform petrophysical data analysis and core sample characterization.
    Upload your custom CSV dataset or explore the built-in synthetic reservoir core dataset.
    """
)

# -----------------------------------------------------------------------------
# Data Loading Strategy (Upload or Sample Data)
# -----------------------------------------------------------------------------
st.sidebar.header("📁 Data Source Selection")
data_source = st.sidebar.radio(
    "Choose Dataset Source",
    options=["Use Synthetic Sample Dataset (40 Core Samples)", "Upload Custom CSV File"],
    help="Select whether to use the included benchmark dataset or upload your own experimental data."
)

raw_df: pd.DataFrame = pd.DataFrame()
data_label = ""

if data_source == "Upload Custom CSV File":
    uploaded_file = st.sidebar.file_uploader(
        "Upload CSV File",
        type=["csv"],
        help="Upload a comma-separated values (CSV) file containing petrophysical core measurements."
    )
    if uploaded_file is not None:
        try:
            raw_df = pd.read_csv(uploaded_file)
            data_label = uploaded_file.name
        except Exception as e:
            st.error(f"❌ Failed to parse uploaded CSV file: {e}")
            st.stop()
    else:
        st.info("👆 Please upload a CSV file in the sidebar to begin data analysis.")
        st.stop()
else:
    sample_path = pathlib.Path(__file__).parent.parent / "data" / "sample_rock_data.csv"
    try:
        raw_df = pd.read_csv(sample_path)
        data_label = "Synthetic demonstration dataset (40 Sandstone Core Samples)"
        st.caption("ℹ️ *Displaying synthetic demonstration dataset. Values reflect typical sandstone trends but are not from an active reservoir.*")
    except Exception as e:
        st.error(f"❌ Error loading sample dataset at '{sample_path}': {e}")
        st.stop()

# -----------------------------------------------------------------------------
# Dataset Validation & Column Detection
# -----------------------------------------------------------------------------
is_valid, err_msg, detected_cols = validate_csv_dataset(raw_df)

if not is_valid:
    st.error(f"❌ **Invalid Dataset:** {err_msg}")
    st.stop()

# -----------------------------------------------------------------------------
# Dataset Preview & Metrics
# -----------------------------------------------------------------------------
st.subheader(f"📋 Dataset Overview: {data_label}")

total_rows, total_cols = raw_df.shape
numeric_cols = raw_df.select_dtypes(include=["number"]).columns.tolist()

# -----------------------------------------------------------------------------
# Porosity Column Mapping & Dynamic Filtering
# -----------------------------------------------------------------------------
st.sidebar.markdown("---")
st.sidebar.header("🔍 Engineering Data Filter")

poro_col = detected_cols.get("porosity")
if poro_col is None:
    # Allow manual selection if auto-heuristic did not trigger
    st.sidebar.warning("⚠️ Could not automatically detect a Porosity column.")
    poro_col = st.sidebar.selectbox("Select Porosity Column manually", options=["None"] + raw_df.columns.tolist())
    if poro_col == "None":
        poro_col = None

perm_col = detected_cols.get("permeability")
if perm_col is None:
    st.sidebar.warning("⚠️ Could not automatically detect a Permeability column.")
    perm_col = st.sidebar.selectbox("Select Permeability Column manually", options=["None"] + raw_df.columns.tolist())
    if perm_col == "None":
        perm_col = None

# Filter execution
filtered_df = raw_df.copy()
min_poro_val = 0.0

if poro_col:
    min_val_in_data = float(raw_df[poro_col].min())
    max_val_in_data = float(raw_df[poro_col].max())
    
    min_poro_val = st.sidebar.slider(
        f"Minimum Cut-off Porosity ({poro_col})",
        min_value=float(min_val_in_data),
        max_value=float(max_val_in_data),
        value=float(min_val_in_data),
        step=0.5,
        help="Filter the core dataset to retain only reservoir samples with porosity strictly greater than or equal to this threshold."
    )
    filtered_df = raw_df[raw_df[poro_col] >= min_poro_val].copy()

filtered_rows = len(filtered_df)
retained_pct = (filtered_rows / total_rows * 100.0) if total_rows > 0 else 0.0

# Display High-Level Dataset Metric Cards
m1, m2, m3, m4 = st.columns(4)
m1.metric("Total Core Samples", f"{total_rows}")
m2.metric("Filtered Samples Retained", f"{filtered_rows}", delta=f"{retained_pct:.1f}% kept")
m3.metric("Numeric Variables", f"{len(numeric_cols)}")
m4.metric("Porosity Cut-Off", f"≥ {min_poro_val:.1f}%" if poro_col else "N/A")

# Data Table Previews
with st.expander("🔍 View Raw & Filtered Data Tables", expanded=False):
    tab_raw, tab_filt = st.tabs(["Filtered Dataset Preview", "Complete Unfiltered Dataset"])
    with tab_raw:
        st.dataframe(filtered_df, use_container_width=True)
    with tab_filt:
        st.dataframe(raw_df, use_container_width=True)

# -----------------------------------------------------------------------------
# Statistical Summary
# -----------------------------------------------------------------------------
st.subheader("📊 Descriptive Engineering Statistics")
st.dataframe(filtered_df.describe().T.style.format("{:.2f}"), use_container_width=True)

# -----------------------------------------------------------------------------
# Interactive Visualizations
# -----------------------------------------------------------------------------
st.markdown("---")
st.subheader("📈 Petrophysical Visualizations")

col_chart1, col_chart2 = st.columns(2)

with col_chart1:
    if poro_col and not filtered_df.empty:
        fig_hist = create_porosity_histogram(filtered_df, poro_col)
        st.plotly_chart(fig_hist, use_container_width=True)
    else:
        st.warning("Select or provide a valid Porosity column to render the distribution histogram.")

with col_chart2:
    if poro_col and perm_col and not filtered_df.empty:
        fig_cross = create_poro_perm_crossplot(filtered_df, poro_col, perm_col)
        st.plotly_chart(fig_cross, use_container_width=True)
        st.caption(
            "📌 **Engineering Insight (Logarithmic Permeability Axis):** Permeability varies across several orders of magnitude "
            "(e.g., 0.1 mD to 1,000 mD) due to pore throat size distribution. A semi-log scale linearizes the typical Kozeny-Carman relationship."
        )
    else:
        st.warning("Both Porosity and Permeability columns are required to generate the reservoir crossplot.")

# -----------------------------------------------------------------------------
# Filtered CSV Export
# -----------------------------------------------------------------------------
st.markdown("---")
st.subheader("📥 Export Filtered Petrophysical Dataset")

filtered_csv_bytes = filtered_df.to_csv(index=False).encode('utf-8')

st.download_button(
    label=f"📥 Download Filtered Core Data ({filtered_rows} rows, CSV)",
    data=filtered_csv_bytes,
    file_name=f"filtered_rock_data_poro_ge_{min_poro_val:.1f}.csv",
    mime="text/csv",
    help="Export only the subset of core samples that satisfy the current filtering criteria."
)

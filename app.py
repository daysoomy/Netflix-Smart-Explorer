import streamlit as st
import pandas as pd
import plotly.express as px
from algo import linear_search, merge_sort

# 1. KONFIGURASI HALAMAN
st.set_page_config(page_title="Netflix Smart Explorer", layout="wide", page_icon="🍿")

# CSS untuk Card Netflix Style (DITAMBAH WARNA PUTIH)
st.markdown("""
    <style>
    .movie-card {
        background-color: #262730; 
        border-radius: 10px; 
        padding: 15px;
        border-left: 5px solid #E50914; 
        margin-bottom: 20px; 
        height: 250px;
        color: white;                    /* Semua teks default jadi putih */
    }
    .movie-title { 
        color: #E50914; 
        font-weight: bold; 
        font-size: 18px; 
    }
    .movie-card p {
        color: #FFFFFF !important;       /* Paksa paragraf jadi putih */
        margin: 6px 0;
    }
    .movie-card b {
        color: #FFFFFF !important;       /* Tahun & rating juga putih */
    }
    </style>
""", unsafe_allow_html=True)

# 2. LOAD DATA
@st.cache_data
def load_data():
    df = pd.read_csv("netflix.csv")
    df = df.fillna({'director': 'Unknown', 'cast': 'Unknown', 'country': 'Unknown', 'rating': 'UR'})
    return df

df = load_data()

# 3. SIDEBAR (REMOTE CONTROL)
st.sidebar.image("https://upload.wikimedia.org/wikipedia/commons/0/08/Netflix_2015_logo.svg", width=150)
st.sidebar.title("Filter Control")

type_filter = st.sidebar.multiselect("Pilih Tipe:", options=df['type'].unique(), default=df['type'].unique())
year_range = st.sidebar.slider("Rentang Tahun:", int(df['release_year'].min()), int(df['release_year'].max()), (2010, 2021))

# Terapkan filter sidebar ke dataframe
filtered_df = df[(df['type'].isin(type_filter)) & (df['release_year'].between(year_range[0], year_range[1]))]

# 4. MAIN LAYOUT DENGAN TABS
tab1, tab2, tab3 = st.tabs(["🏠 Discovery", "📈 Global Insights", "🔬 Deep-Dive Analysis"])

# --- TAB 1: DISCOVERY ---
with tab1:
    st.title("Find Your Next Story")
    
    # KPI Row
    c1, c2, c3 = st.columns(3)
    c1.metric("Total Matches", len(filtered_df))
    c2.metric("Movies", len(filtered_df[filtered_df['type'] == 'Movie']))
    c3.metric("TV Shows", len(filtered_df[filtered_df['type'] == 'TV Show']))

    # Search Box
    col_search, col_cat = st.columns([3, 1])
    with col_search:
        query = st.text_input("Search by Title, Actor, or Mood (Description):")
    with col_cat:
        cat = st.selectbox("Category:", ["title", "cast", "description"])

    # Sorting
    col_sort, col_btn = st.columns([3, 1])
    with col_sort:
        sort_key = st.selectbox("Sort By:", ["release_year", "title"])
    with col_btn:
        order = st.radio("Order:", ["Newest/A-Z", "Oldest/Z-A"], horizontal=True)

    # Process DSA
    data_to_process = filtered_df.to_dict('records')
    if query:
        data_to_process = linear_search(data_to_process, cat, query)
    
    if st.button("🔥 Run Algorithm"):
        is_rev = True if order == "Newest/A-Z" else False
        final_data = merge_sort(data_to_process, sort_key, reverse=is_rev)
    else:
        final_data = data_to_process[:12] # Tampilkan 12 saja dulu

    # Display Movie Cards (Grid 3 Kolom)
    st.write("---")
    rows = [final_data[i:i + 3] for i in range(0, len(final_data), 3)]
    for row in rows[:4]: # Batasi 4 baris kartu agar tidak berat
        cols = st.columns(3)
        for i, item in enumerate(row):
            with cols[i]:
                st.markdown(f"""
                    <div class="movie-card">
                        <div class="movie-title">{item['title']}</div>
                        <p style="font-size:12px; color: white;"><b>{item['release_year']}</b> | {item['rating']}</p>
                        <p style="font-size:11px; color: white;">{item['description'][:120]}...</p>
                    </div>
                """, unsafe_allow_html=True)

# --- TAB 2: INSIGHTS ---
with tab2:
    st.title("Netflix Global Trends")
    col_a, col_b = st.columns(2)
    with col_a:
        fig_pie = px.pie(filtered_df, names='type', hole=0.4, title="Content Type Distribution")
        st.plotly_chart(fig_pie)
    with col_b:
        top_countries = filtered_df['country'].value_counts().head(10).reset_index()
        fig_bar = px.bar(top_countries, x='count', y='country', orientation='h', title="Top 10 Countries")
        st.plotly_chart(fig_bar)

# --- TAB 3: DEEP-DIVE ---
with tab3:
    st.title("Heatmap & Pivot Analysis")
    st.write("Hubungan antara Rating Konten dan Tahun Rilis")
    
    # Pivot Table
    pivot = filtered_df.pivot_table(index='rating', columns='type', values='show_id', aggfunc='count').fillna(0)
    st.dataframe(pivot, use_container_width=True)
    
    # Heatmap
    fig_heat = px.imshow(pivot, text_auto=True, color_continuous_scale='Reds', title="Pivot Heatmap: Rating vs Type")
    st.plotly_chart(fig_heat, use_container_width=True)
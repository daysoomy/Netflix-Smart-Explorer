import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from algo import linear_search, merge_sort

# 1. KONFIGURASI HALAMAN
st.set_page_config(page_title="Netflix Smart Explorer", layout="wide", page_icon="🍿")

# CSS untuk Card Netflix Style
st.markdown("""
    <style>
    .movie-card {
        background-color: #262730; 
        border-radius: 10px; 
        padding: 15px;
        border-left: 5px solid #E50914; 
        margin-bottom: 20px; 
        height: 250px;
        color: white;               
    }
    .movie-title { 
        color: #E50914; 
        font-weight: bold; 
        font-size: 18px; 
    }
    .movie-card p {
        color: #FFFFFF !important;       
        margin: 6px 0;
    }
    .movie-card b {
        color: #FFFFFF !important;       
    }
    .metric-card {
        background: linear-gradient(135deg, #E50914 0%, #831010 100%);
        padding: 20px;
        border-radius: 10px;
        color: white;
        text-align: center;
    }
    </style>
""", unsafe_allow_html=True)

# 2. LOAD DATA
@st.cache_data
def load_data():
    df = pd.read_csv("netflix.csv")
    df = df.fillna({
        'director': 'Unknown', 
        'cast': 'Unknown', 
        'country': 'Unknown', 
        'rating': 'UR',
        'duration': 'Unknown'
    })
    return df

df = load_data()

# Fungsi untuk ekstrak genre dari kolom listed_in
def extract_genres(df):
    all_genres = []
    for genres_str in df['listed_in'].dropna():
        genres = [g.strip() for g in str(genres_str).split(',')]
        all_genres.extend(genres)
    return pd.Series(all_genres).value_counts()

# 3. SIDEBAR (REMOTE CONTROL)
st.sidebar.image("https://upload.wikimedia.org/wikipedia/commons/0/08/Netflix_2015_logo.svg", width=150)
st.sidebar.title("🎮 Filter Control")

type_filter = st.sidebar.multiselect(
    "Pilih Tipe:", 
    options=df['type'].unique(), 
    default=df['type'].unique()
)
year_range = st.sidebar.slider(
    "Rentang Tahun:", 
    int(df['release_year'].min()), 
    int(df['release_year'].max()), 
    (2010, 2021)
)

# Terapkan filter sidebar ke dataframe
filtered_df = df[
    (df['type'].isin(type_filter)) & 
    (df['release_year'].between(year_range[0], year_range[1]))
]

# 4. MAIN LAYOUT DENGAN TABS
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🏠 Overview", 
    "🎬 Genre Analysis", 
    "🌍 Country Analysis",
    "⏱️ Duration Analysis",
    "🔍 Search & Sort"
])

# --- TAB 1: OVERVIEW ---
with tab1:
    st.title("📊 Netflix Content Overview")
    
    # KPI Row dengan styling lebih baik
    col1, col2, col3, col4 = st.columns(4)
    
    total_content = len(filtered_df)
    total_movies = len(filtered_df[filtered_df['type'] == 'Movie'])
    total_tv = len(filtered_df[filtered_df['type'] == 'TV Show'])
    
    with col1:
        st.metric("📺 Total Content", f"{total_content:,}")
    with col2:
        st.metric("🎬 Movies", f"{total_movies:,}")
    with col3:
        st.metric("📺 TV Shows", f"{total_tv:,}")
    with col4:
        movie_percentage = (total_movies / total_content * 100) if total_content > 0 else 0
        st.metric("🎯 Movie %", f"{movie_percentage:.1f}%")
    
    st.write("---")
    
    # Row untuk visualisasi
    col_left, col_right = st.columns(2)
    
    with col_left:
        st.subheader("📊 Proporsi Movie vs TV Show")
        fig_pie = px.pie(
            filtered_df, 
            names='type', 
            hole=0.4,
            color_discrete_sequence=['#E50914', '#831010']
        )
        fig_pie.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig_pie, use_container_width=True)
    
    with col_right:
        st.subheader("📈 Tren Rilis Per Tahun")
        yearly_data = filtered_df.groupby(['release_year', 'type']).size().reset_index(name='count')
        fig_line = px.line(
            yearly_data, 
            x='release_year', 
            y='count', 
            color='type',
            markers=True,
            color_discrete_sequence=['#E50914', '#831010']
        )
        fig_line.update_layout(xaxis_title="Tahun", yaxis_title="Jumlah Konten")
        st.plotly_chart(fig_line, use_container_width=True)
    
    # Konten ditambahkan per tahun
    st.subheader("➕ Jumlah Konten Ditambahkan Per Tahun")
    if 'date_added' in filtered_df.columns:
        filtered_df['year_added'] = pd.to_datetime(filtered_df['date_added'], errors='coerce').dt.year
        added_by_year = filtered_df['year_added'].value_counts().sort_index()
        fig_bar_added = px.bar(
            x=added_by_year.index, 
            y=added_by_year.values,
            labels={'x': 'Tahun Ditambahkan', 'y': 'Jumlah'},
            color_discrete_sequence=['#E50914']
        )
        st.plotly_chart(fig_bar_added, use_container_width=True)

# --- TAB 2: GENRE ANALYSIS ---
with tab2:
    st.title("🎬 Genre Analysis")
    
    # Filter berdasarkan Movie atau TV Show
    genre_type = st.radio("Filter berdasarkan:", ["Semua", "Movie", "TV Show"], horizontal=True)
    
    if genre_type == "Movie":
        genre_df = filtered_df[filtered_df['type'] == 'Movie']
    elif genre_type == "TV Show":
        genre_df = filtered_df[filtered_df['type'] == 'TV Show']
    else:
        genre_df = filtered_df
    
    # Ekstrak dan hitung genre
    genre_counts = extract_genres(genre_df)
    top_genres = genre_counts.head(15)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("📊 Top 15 Genre Terbanyak")
        fig_genre = px.bar(
            x=top_genres.values, 
            y=top_genres.index,
            orientation='h',
            labels={'x': 'Jumlah', 'y': 'Genre'},
            color=top_genres.values,
            color_continuous_scale='Reds'
        )
        fig_genre.update_layout(showlegend=False, yaxis={'categoryorder':'total ascending'})
        st.plotly_chart(fig_genre, use_container_width=True)
    
    with col2:
        st.subheader("🔝 Top 5 Genre")
        for i, (genre, count) in enumerate(top_genres.head(5).items(), 1):
            st.metric(f"{i}. {genre}", f"{count} konten")
    
    # Treemap untuk visualisasi hierarki genre
    st.subheader("🗺️ Treemap Genre Distribution")
    treemap_data = pd.DataFrame({
        'Genre': top_genres.index[:10],
        'Count': top_genres.values[:10]
    })
    fig_treemap = px.treemap(
        treemap_data,
        path=['Genre'],
        values='Count',
        color='Count',
        color_continuous_scale='Reds'
    )
    st.plotly_chart(fig_treemap, use_container_width=True)

# --- TAB 3: COUNTRY ANALYSIS ---
with tab3:
    st.title("🌍 Country Analysis")
    
    # Ekstrak negara pertama (negara utama)
    filtered_df['main_country'] = filtered_df['country'].apply(
        lambda x: str(x).split(',')[0].strip() if pd.notna(x) else 'Unknown'
    )
    
    country_counts = filtered_df['main_country'].value_counts().head(15)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("🌏 Top 15 Negara Produksi")
        fig_country = px.bar(
            x=country_counts.values,
            y=country_counts.index,
            orientation='h',
            labels={'x': 'Jumlah Konten', 'y': 'Negara'},
            color=country_counts.values,
            color_continuous_scale='Reds'
        )
        fig_country.update_layout(showlegend=False, yaxis={'categoryorder':'total ascending'})
        st.plotly_chart(fig_country, use_container_width=True)
    
    with col2:
        st.subheader("🎯 Pilih Negara")
        selected_country = st.selectbox(
            "Lihat konten dari:",
            options=['All'] + list(country_counts.index[:20])
        )
    
    # List judul berdasarkan negara
    if selected_country != 'All':
        st.subheader(f"📋 Konten dari {selected_country}")
        country_content = filtered_df[filtered_df['main_country'] == selected_country]
        
        # Tampilkan dalam tabel
        display_df = country_content[['title', 'type', 'release_year', 'rating', 'listed_in']].head(20)
        st.dataframe(display_df, use_container_width=True)
        
        st.info(f"Total: {len(country_content)} konten dari {selected_country}")

# --- TAB 4: DURATION ANALYSIS ---
with tab4:
    st.title("⏱️ Duration Analysis")
    
    # Pisahkan Movies dan TV Shows
    movies_df = filtered_df[filtered_df['type'] == 'Movie'].copy()
    tv_df = filtered_df[filtered_df['type'] == 'TV Show'].copy()
    
    # Extract durasi untuk Movies (dalam menit)
    movies_df['duration_min'] = movies_df['duration'].str.extract('(\d+)').astype(float)
    
    # Extract jumlah season untuk TV Shows
    tv_df['seasons'] = tv_df['duration'].str.extract('(\d+)').astype(float)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🎬 Distribusi Durasi Film (Menit)")
        fig_movie_duration = px.histogram(
            movies_df,
            x='duration_min',
            nbins=30,
            labels={'duration_min': 'Durasi (menit)', 'count': 'Jumlah Film'},
            color_discrete_sequence=['#E50914']
        )
        st.plotly_chart(fig_movie_duration, use_container_width=True)
        
        # Stats
        if not movies_df['duration_min'].empty:
            avg_duration = movies_df['duration_min'].mean()
            median_duration = movies_df['duration_min'].median()
            st.metric("⏱️ Durasi Rata-rata", f"{avg_duration:.0f} menit")
            st.metric("📊 Durasi Median", f"{median_duration:.0f} menit")
    
    with col2:
        st.subheader("📺 Distribusi Jumlah Season (TV Show)")
        season_counts = tv_df['seasons'].value_counts().sort_index()
        fig_tv_seasons = px.bar(
            x=season_counts.index,
            y=season_counts.values,
            labels={'x': 'Jumlah Season', 'y': 'Jumlah TV Show'},
            color_discrete_sequence=['#831010']
        )
        st.plotly_chart(fig_tv_seasons, use_container_width=True)
        
        # Stats
        if not tv_df['seasons'].empty:
            avg_seasons = tv_df['seasons'].mean()
            max_seasons = tv_df['seasons'].max()
            st.metric("📊 Rata-rata Season", f"{avg_seasons:.1f}")
            st.metric("🏆 Maksimal Season", f"{int(max_seasons)}")
    
    # Box plot untuk perbandingan
    st.subheader("📦 Box Plot Perbandingan")
    fig_box = go.Figure()
    fig_box.add_trace(go.Box(y=movies_df['duration_min'], name='Movie Duration (min)', marker_color='#E50914'))
    fig_box.add_trace(go.Box(y=tv_df['seasons'], name='TV Show Seasons', marker_color='#831010'))
    st.plotly_chart(fig_box, use_container_width=True)

# --- TAB 5: SEARCH & SORT ---
with tab5:
    st.title("🔍 Search & Sort Engine")
    st.write("Implementasi Linear Search & Merge Sort")

    # KPI Row
    c1, c2, c3 = st.columns(3)
    c1.metric("Total Matches", len(filtered_df))
    c2.metric("Movies", len(filtered_df[filtered_df['type'] == 'Movie']))
    c3.metric("TV Shows", len(filtered_df[filtered_df['type'] == 'TV Show']))

    # Search Box
    col_search, col_cat = st.columns([3, 1])
    with col_search:
        query = st.text_input("🔎 Search by Title, Actor, or Description:")
    with col_cat:
        cat = st.selectbox("Category:", ["title", "cast", "description"])

    # Sorting
    col_sort, col_order = st.columns([3, 1])
    with col_sort:
        sort_key = st.selectbox("Sort By:", ["release_year", "title", "rating"])
    with col_order:
        order = st.radio("Order:", ["Newest/A-Z", "Oldest/Z-A"], horizontal=True)

    # =========================
    # DATA PROCESSING (DSA)
    # =========================
    data_to_process = filtered_df.to_dict("records")

    # Pastikan release_year numeric
    for item in data_to_process:
        if item.get("release_year"):
            item["release_year"] = int(item["release_year"])

    # Linear Search
    if query:
        st.info(f"🔍 Menggunakan **Linear Search** untuk mencari: '{query}'")
        data_to_process = linear_search(data_to_process, cat, query)
        st.success(f"✅ Ditemukan {len(data_to_process)} hasil")

    # Merge Sort (AUTO / REACTIVE)
    is_reverse = True if order == "Newest/A-Z" else False
    st.info(f"🔄 Menjalankan **Merge Sort** berdasarkan: {sort_key}")

    final_data = merge_sort(
        data_to_process,
        key=sort_key,
        reverse=is_reverse
    )

    st.success("✅ Sorting selesai!")

    # =========================
    # DISPLAY RESULT
    # =========================
    st.write("---")
    st.subheader("🎬 Hasil Pencarian")

    if len(final_data) == 0:
        st.warning("⚠️ Tidak ada hasil yang ditemukan")
    else:
        rows = [final_data[i:i + 3] for i in range(0, len(final_data), 3)]
        for row in rows[:4]:
            cols = st.columns(3)
            for i, item in enumerate(row):
                with cols[i]:
                    desc = str(item.get('description', ''))[:120]
                    st.markdown(f"""
                        <div class="movie-card">
                            <div class="movie-title">{item['title']}</div>
                            <p style="font-size:12px;"><b>Type:</b> {item['type']}</p>
                            <p style="font-size:12px;">
                                <b>Year:</b> {item['release_year']} |
                                <b>Rating:</b> {item['rating']}
                            </p>
                            <p style="font-size:11px;">{desc}...</p>
                        </div>
                    """, unsafe_allow_html=True)

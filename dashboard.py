import streamlit as st
import pandas as pd
import sqlite3
import os
import plotly.express as px
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

# Configuration
st.set_page_config(page_title="Cyber Arcade Analytics", page_icon="🎮", layout="wide")

DB_PATH = os.path.join(os.path.dirname(__file__), "game_data.db")

@st.cache_data
def load_data():
    if not os.path.exists(DB_PATH):
        return pd.DataFrame()
    
    conn = sqlite3.connect(DB_PATH)
    query = "SELECT * FROM game_sessions"
    df = pd.read_sql(query, conn)
    conn.close()
    
    if not df.empty:
        # Convert times to datetime objects
        df["start_time"] = pd.to_datetime(df["start_time"])
        df["end_time"] = pd.to_datetime(df["end_time"])
        # Add a date column for grouping
        df["play_date"] = df["start_time"].dt.date
    return df

# Header
st.title("🎮 Cyber Arcade Analytics")
st.markdown("### Player Telemetry & Performance Dashboard")
st.markdown("---")

df = load_data()

if df.empty:
    st.warning("⚠️ No game data found! Please play some games first, or run `python generate_mock_data.py` to populate test data.")
else:
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["📊 Global Overview", "🧪 Product A/B Testing", "🗺️ Spatial Heatmaps", "🤖 Predictive ML", "📄 Export Reports"])
    
    with tab1:
        # ── KPI Row ──────────────────────────────────────────────────
        col1, col2, col3, col4 = st.columns(4)
        
        total_games = len(df)
        total_time_min = df["duration_seconds"].sum() / 60
        fav_game = df["game_name"].mode()[0]
        avg_score = df["score"].mean()
        
        col1.metric("Total Games Played", f"{total_games:,}")
        col2.metric("Total Play Time", f"{total_time_min:,.0f} mins")
        col3.metric("Most Played Game", fav_game)
        col4.metric("Avg Global Score", f"{avg_score:.1f}")
        
        st.markdown("---")
        
        # ── Visualizations ───────────────────────────────────────────
        row1_c1, row1_c2 = st.columns(2)
        
        with row1_c1:
            st.subheader("Games Played Distribution")
            game_counts = df["game_name"].value_counts().reset_index()
            game_counts.columns = ["game_name", "count"]
            
            fig = px.pie(
                game_counts, 
                values='count', 
                names='game_name', 
                hole=0.4,
                color_discrete_sequence=px.colors.qualitative.Pastel
            )
            fig.update_layout(template="plotly_dark", margin=dict(t=0, b=0, l=0, r=0))
            st.plotly_chart(fig, use_container_width=True)
            
        with row1_c2:
            st.subheader("Playtime by Game (Minutes)")
            playtime = df.groupby("game_name")["duration_seconds"].sum().reset_index()
            playtime["duration_minutes"] = playtime["duration_seconds"] / 60
            playtime = playtime.sort_values("duration_minutes", ascending=False)
            
            fig2 = px.bar(
                playtime, 
                x='game_name', 
                y='duration_minutes',
                color='game_name',
                color_discrete_sequence=px.colors.qualitative.Pastel
            )
            fig2.update_layout(template="plotly_dark", showlegend=False, xaxis_title="Game", yaxis_title="Total Minutes")
            st.plotly_chart(fig2, use_container_width=True)
            
        st.markdown("---")
        
        # ── Time Series Analysis ─────────────────────────────────────
        st.subheader("Player Performance Over Time")
        
        # Filter by game
        game_filter = st.selectbox("Select game to view progression:", df["game_name"].unique())
        game_df = df[df["game_name"] == game_filter].sort_values("start_time")
        
        if not game_df.empty:
            # Calculate a 5-game rolling average
            game_df["rolling_avg_score"] = game_df["score"].rolling(window=5, min_periods=1).mean()
            
            fig3 = px.line(
                game_df, 
                x='start_time', 
                y=['score', 'rolling_avg_score'],
                labels={'value': 'Score', 'start_time': 'Date Played', 'variable': 'Metric'},
                color_discrete_sequence=["rgba(255,100,100,0.5)", "#00ffcc"]
            )
            # Rename legends
            newnames = {'score': 'Individual Score', 'rolling_avg_score': '5-Game Rolling Avg'}
            fig3.for_each_trace(lambda t: t.update(name = newnames[t.name]))
            
            fig3.update_layout(template="plotly_dark", hovermode="x unified")
            st.plotly_chart(fig3, use_container_width=True)
        
        st.markdown("---")
        
        # ── Raw Data Table ───────────────────────────────────────────
        st.subheader("Raw Telemetry Data")
        with st.expander("View / Export Data"):
            display_df = df.drop(columns=["play_date"]).sort_values("start_time", ascending=False)
            st.dataframe(display_df, use_container_width=True)
            
    with tab2:
        st.subheader("🧪 Active A/B Experiments")
        st.markdown("Evaluating engine variants on user progression and scores.")
        
        # Filter dataframe for games that have actual alternate variants logging
        experiment_games = df[df['ab_variant'] != 'Control']['game_name'].unique()
        
        if len(experiment_games) == 0:
            st.info("No experiment variants recorded yet! Play Cyber Dash or Cyber Reaction.")
        else:
            exp_game = st.selectbox("Select Experiment Context:", experiment_games)
            exp_df = df[df['game_name'] == exp_game]
            
            st.markdown(f"**Experimentizing**: `{exp_game}`")
            
            # Simple aggregations
            stats = exp_df.groupby('ab_variant').agg(
                Plays=('session_id', 'count'),
                Avg_Score=('score', 'mean'),
                Max_Score=('score', 'max')
            ).reset_index()
            
            st.dataframe(stats, use_container_width=True)
            
            # Box plot to show distribution of scores across variants
            fig_ab = px.box(
                exp_df, 
                x="ab_variant", 
                y="score", 
                color="ab_variant",
                title=f"Score Distribution by Variant in {exp_game}",
                points="all" # show underlying data points
            )
            fig_ab.update_layout(template="plotly_dark")
            st.plotly_chart(fig_ab, use_container_width=True)

    with tab3:
        st.subheader("🗺️ Player Spatial Analytics")
        st.markdown("Analyze where players most frequently meet their demise in-game.")
        
        # Filter for data that has spatial tracking
        if 'event_x' not in df.columns or 'event_y' not in df.columns:
            st.info("No spatial data columns found in the database yet. Run generate_mock_data.py or play a game to initialize them!")
        else:
            spatial_df = df.dropna(subset=['event_x', 'event_y'])
            if spatial_df.empty:
                st.info("No spatial data recorded yet! Play a game of Snake to generate death coordinates.")
            else:
                spatial_game = st.selectbox("Select Game for Heatmap:", spatial_df["game_name"].unique())
                plot_df = spatial_df[spatial_df["game_name"] == spatial_game]
                
                fig_heat = px.density_heatmap(
                    plot_df, 
                    x="event_x", 
                    y="event_y", 
                    title=f"Death Heatmap for {spatial_game}",
                    nbinsx=20, nbinsy=20,
                    color_continuous_scale="Viridis"
                )
                fig_heat.update_layout(template="plotly_dark")
                st.plotly_chart(fig_heat, use_container_width=True)
            
    with tab4:
        st.subheader("🤖 Player Clustering Model (K-Means)")
        st.markdown("Using Unsupervised Machine Learning to group play sessions based on Score and Duration.")
        
        if len(df) < 10:
            st.warning("Not enough data to run ML models reliably. Need at least 10 sessions.")
        else:
            ml_game = st.selectbox("Select Game for Clustering:", df["game_name"].unique())
            ml_df = df[df["game_name"] == ml_game].copy()
            
            if len(ml_df) < 5:
                st.warning("Need more sessions for this specific game.")
            else:
                num_clusters = st.slider("Select Number of Player Segments (K)", min_value=2, max_value=5, value=3)
                
                features = ml_df[['duration_seconds', 'score']]
                scaler = StandardScaler()
                scaled_features = scaler.fit_transform(features)
                
                kmeans = KMeans(n_clusters=num_clusters, random_state=42, n_init='auto')
                ml_df['cluster'] = kmeans.fit_predict(scaled_features)
                ml_df['cluster'] = ml_df['cluster'].astype(str)
                
                fig_ml = px.scatter(
                    ml_df, 
                    x="duration_seconds", 
                    y="score", 
                    color="cluster",
                    title=f"Player Segmentation for {ml_game}",
                    hover_data=['start_time']
                )
                fig_ml.update_layout(template="plotly_dark")
                st.plotly_chart(fig_ml, use_container_width=True)

    with tab5:
        st.subheader("📄 Export Automated Reports")
        st.markdown("Download the raw telemetry or a summarized weekly report.")
        
        csv_data = df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="Download Full Telemetry (CSV)",
            data=csv_data,
            file_name="cyber_arcade_telemetry.csv",
            mime="text/csv",
        )
        
        report_df = df.groupby('game_name').agg(
            total_plays=('session_id', 'count'),
            avg_score=('score', 'mean'),
            max_score=('score', 'max'),
            total_play_time_mins=('duration_seconds', lambda x: x.sum() / 60)
        ).reset_index()
        
        report_csv = report_df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="Download Aggregated Summary Report (CSV)",
            data=report_csv,
            file_name="cyber_arcade_summary_report.csv",
            mime="text/csv",
        )

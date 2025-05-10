import countries
import streamlit as st
import pandas as pd
import preprocessor
import helper
import plotly.express as px
import plotly.figure_factory as ff
import seaborn as sns
import matplotlib.pyplot as plt
from helper import weight_v_height,men_vs_women


st.set_page_config(layout="wide")

df = pd.read_csv(r'athlete_events.csv')
region_df = pd.read_csv(r'noc_regions.csv')

df = preprocessor.preprocess(df, region_df)

# Sidebar configuration
st.sidebar.title("Olympics Analysis")
st.sidebar.image(
    'https://e7.pngegg.com/pngimages/1020/402/png-clipart-2024-summer-olympics-brand-circle-area-olympic-rings-olympics-logo-text-sport.png')
user_menu = st.sidebar.radio(
    'Select an Option',
    ('Medal Tally', 'Overall Analysis', 'Country-wise Analysis', 'Athlete-wise Analysis',
     'Top Athletes', 'Olympic Games Locations', 'Olympics Trivia', 'Predictions')
)

# Medal Tally Section
if user_menu == 'Medal Tally':
    try:
        with st.spinner("Loading Medal Data... Please wait!"):
            years, countries = helper.country_year_list(df)

        # Sidebar Filters with Modern Design
        with st.sidebar:
            st.header("🏅 Medal Filters", anchor="filters")
            selected_year = st.selectbox("📅 Select Year", years, key='year_select')
            selected_country = st.selectbox("🌍 Select Country", countries, key='country_select')

        medal_tally = helper.fetch_medal_tally(df, selected_year, selected_country)

        if 'Total' not in medal_tally.columns:
            medal_tally['Total'] = medal_tally[['Gold', 'Silver', 'Bronze']].sum(axis=1)

        # Dynamic title based on selection
        title_map = {
            ('Overall', 'Overall'): "🌍 Global Medal Standings",
            ('Non-Overall', 'Overall'): f"📅 {selected_year} Olympic Tally",
            ('Overall', 'Non-Overall'): f"🏴 {selected_country}'s History",
            ('Non-Overall', 'Non-Overall'): f"🏆 {selected_country} in {selected_year}"
        }

        key = ('Overall' if selected_year == 'Overall' else 'Non-Overall',
               'Overall' if selected_country == 'Overall' else 'Non-Overall')

        # Modern header with gradient background
        st.markdown(f"""
        <div style='text-align: center; padding: 50px; background: linear-gradient(45deg, #1a237e, #6a1b9a); border-radius: 15px; margin-bottom: 30px;'>
            <h1 style='color:white; font-size: 3rem; font-weight: bold; font-family: "Arial", sans-serif;'>
                {title_map[key]}
            </h1>
        </div>
        """, unsafe_allow_html=True)

        # Responsive Layout with Enhanced Card Design and Hover Effects
        cols = st.columns(4)

        metrics = [
            ("🏳️ Countries", len(medal_tally), "#4CAF50"),
            ("🥇 Gold", medal_tally['Gold'].sum(), "#FFD700"),
            ("🥈 Silver", medal_tally['Silver'].sum(), "#C0C0C0"),
            ("🥉 Bronze", medal_tally['Bronze'].sum(), "#CD7F32")
        ]

        for col, (label, value, color) in zip(cols, metrics):
            with col:
                st.markdown(f"""
                <div style="
                    background: #ffffff;
                    padding: 3rem;
                    border-radius: 15px;
                    border-left: 8px solid {color};
                    box-shadow: 0 6px 12px rgba(0,0,0,0.1);
                    text-align: center;
                    margin-top: 2rem;
                    transition: transform 0.3s ease, box-shadow 0.3s ease;
                    cursor: pointer;
                " onmouseover="this.style.transform='scale(1.1)'; this.style.boxShadow='0px 8px 20px rgba(0,0,0,0.2)';" 
                onmouseout="this.style.transform='scale(1)'; this.style.boxShadow='0px 6px 12px rgba(0,0,0,0.1)';">
                    <div style="color: #555; font-size: 1.2rem; font-weight: 600;" title="Total number of {label.lower()}">{label}</div>
                    <div style="color: {color}; font-size: 2.5rem; font-weight: bold;" title="Total {label.lower()} medals earned">{value}</div>
                </div>
                """, unsafe_allow_html=True)

        # Medal Tally Table with modern hover effect
        st.markdown("<hr style='border: 1px solid #ddd;'>", unsafe_allow_html=True)

        # Stylish Medal Table with Hover Effects
        styled_df = medal_tally.style \
            .format({'Gold': '🥇 {}', 'Silver': '🥈 {}', 'Bronze': '🥉 {}', 'Total': '🏅 {}'}) \
            .background_gradient(cmap='Blues', subset=['Total']) \
            .set_properties(**{
                'background-color': '#f8f8f8',
                'color': '#1a237e',
                'border-radius': '8px',
                'font-size': '1.2rem',
                'text-align': 'center',
                'transition': 'all 0.3s ease',
                'box-shadow': '0px 4px 8px rgba(0,0,0,0.1)',
                'padding': '15px'
            }) \
            .set_table_styles([{
                'selector': 'thead th',
                'props': [('background-color', '#1a237e'), ('color', 'white'), ('font-size', '1.2rem'), ('padding', '15px'), ('font-weight', 'bold')]
            }, {
                'selector': 'tbody td',
                'props': [('padding', '12px'), ('font-size', '1rem')]
            }, {
                'selector': 'tbody tr:hover',
                'props': [('background-color', '#f1f8ff'), ('transform', 'scale(1.05)'), ('box-shadow', '0px 4px 8px rgba(0,0,0,0.2)')]
            }])

        st.dataframe(styled_df, height=450)

        # Medal Distribution Graph (Simple Pie Chart)
        st.markdown("<hr style='border: 1px solid #ddd;'>", unsafe_allow_html=True)
        medal_data = medal_tally[['Gold', 'Silver', 'Bronze']].sum().reset_index()
        medal_data.columns = ['Medal', 'Count']

        color_map = {
            "Gold": "#FFD700",
            "Silver": "#C0C0C0",
            "Bronze": "#CD7F32"
        }

        fig = px.pie(medal_data, names='Medal', values='Count', title='Medal Distribution', color='Medal', color_discrete_map=color_map)
        fig.update_traces(textinfo='percent+label', pull=[0.1, 0.1, 0.1], hoverinfo='label+percent', opacity=0.8)

        # Add Hover Effect to Pie Chart Segments
        fig.update_traces(
            hoverinfo="label+percent",
            hovertemplate="<b>%{label}</b><br>Count: %{value}<br>%{percent}",
            marker=dict(line=dict(color="white", width=2)),
            opacity=0.85
        )

        fig.update_layout(
            margin=dict(t=20, b=20, l=20, r=20),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            hovermode="closest"
        )
        st.plotly_chart(fig, use_container_width=True)

        # Footer at the Bottom
        st.markdown("""
            <footer style="position: relative; bottom: 0; width: 100%; background-color: #1a237e; color: white; padding: 20px 0; text-align: center; box-shadow: 0 4px 10px rgba(0, 0, 0, 0.2); border-top: 3px solid #6a1b9a;">
                <div style="background: linear-gradient(135deg, #1a237e, #6a1b9a); padding: 20px 0; border-radius: 12px; text-align: center;">
                    <p style="font-size: 1.2rem; font-weight: bold; color: white; margin: 0;">
                        Developed by Umesh Pathak | 🌍 Olympic Medal Data
                    </p>
                    <p style="font-size: 1rem; color: white; margin: 5px 0;">&copy; 2025 All rights reserved.</p>
                </div>
            </footer>
        """, unsafe_allow_html=True)

    except Exception as e:
        st.error(f"Error loading medal data: {str(e)}")
        st.stop()

# Overall Analysis
st.markdown("""
    <style>
        /* Body and overall page styling */
        body {
            font-family: 'Arial', sans-serif;
            background-color: #f4f6f9;
            color: #333;
        }

        /* Title Styling */
        h1, h2 {
            color: #1a237e;
            font-weight: bold;
            font-family: 'Arial Rounded MT Bold', sans-serif;
        }
        h3 {
            color: #333;
        }

        /* Metric Card Styling */
        .metric-card {
            background: white;
            border-radius: 12px;
            padding: 1.5rem;
            margin: 0.8rem;
            box-shadow: 0 4px 6px rgba(0,0,0,0.15);
            border-left: 5px solid #1a237e;
            transition: transform 0.3s, box-shadow 0.3s;
        }
        .metric-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 8px 16px rgba(0,0,0,0.2);
        }

        /* Footer styling */
        .footer {
            text-align: center;
            margin-top: 3rem;
            color: #fff;
            background-color: #1a237e;  /* Matching the top color */
            font-size: 0.9rem;
            padding: 1.5rem 0;
            box-shadow: 0 -4px 6px rgba(0, 0, 0, 0.1);
        }
        .footer a {
            text-decoration: none;
            color: #f8f9fa;
        }
        .footer a:hover {
            color: #00bfa5;  /* A matching accent color */
        }

        /* Custom selectbox and input styling */
        .stSelectbox select {
            background-color: #f4f6f9;
            border-radius: 8px;
            border: 1px solid #ccc;
            padding: 8px 12px;
            font-size: 1rem;
            color: #333;
        }
        .stSelectbox select:hover {
            border-color: #2196F3;
        }

    </style>
""", unsafe_allow_html=True)

# --- Top Statistics Section ---
if user_menu == 'Overall Analysis':
    # Page title
    st.markdown(
        "<h1 style='text-align: center;'>📊 Olympic Evolution Overview</h1>",
        unsafe_allow_html=True)

    # Metric Cards
    metrics = [
        ("📅 Editions", df['Year'].unique().shape[0] - 1, "#4CAF50"),
        ("🏙️ Host Cities", df['City'].unique().shape[0], "#2196F3"),
        ("⚽ Sports", df['Sport'].unique().shape[0], "#FF5722"),
        ("🎯 Events", df['Event'].unique().shape[0], "#9C27B0"),
        ("🌍 Nations", df['region'].unique().shape[0], "#E91E63"),
        ("🏃 Athletes", df['Name'].unique().shape[0], "#009688")
    ]

    # Metric Cards Styling and Layout
    cols = st.columns(3)
    for col, (label, value, color) in zip(cols, metrics[:3]):
        with col:
            st.markdown(f"""
            <div class="metric-card" style="border-left-color: {color};">
                <h3 style="color: {color}; margin:0; font-size: 1.2rem;">{label}</h3>
                <h1 style="color: #1a237e; margin:0; font-size: 2.5rem;">{value}</h1>
            </div>
            """, unsafe_allow_html=True)

    cols = st.columns(3)
    for col, (label, value, color) in zip(cols, metrics[3:]):
        with col:
            st.markdown(f"""
            <div class="metric-card" style="border-left-color: {color};">
                <h3 style="color: {color}; margin:0; font-size: 1.2rem;">{label}</h3>
                <h1 style="color: #1a237e; margin:0; font-size: 2.5rem;">{value}</h1>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("---")

    # --- Participation Analysis ---
    st.markdown(
        "<h2 style='color: #1a237e; border-bottom: 2px solid #0d47a1; padding-bottom: 0.5rem;'>🌐 Global Participation Trends</h2>",
        unsafe_allow_html=True)

    nations_over_time = helper.participating_nations_over_time(df)

    col1, col2 = st.columns([2, 1])
    with col1:
        # Animated participation chart
        fig = px.scatter(nations_over_time,
                         x="Edition", y="Nations",
                         animation_frame="Edition",
                         size="Nations",
                         color="Nations",
                         color_continuous_scale=px.colors.sequential.Rainbow,
                         range_y=[0, nations_over_time['Nations'].max() + 10],
                         template="plotly_white+presentation",
                         labels={'Nations': 'Participating Countries'},
                         height=500)
        fig.update_layout(
            title="Animated Participation Growth",
            xaxis_title="Olympic Edition",
            yaxis_title="Number of Nations",
            hovermode="x unified"
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        # Current participation metrics
        st.markdown(""" 
        <div style='background: #f8f9fa; border-radius: 15px; padding: 2rem; margin-top: 2rem;'>
            <h3 style='color: #1a237e;'>Current Participation</h3>
            <h1 style='color: #0d47a1; font-size: 3rem;'>{}</h1>
            <p style='color: #666;'>Nations in latest edition</p>
        </div>
        """.format(nations_over_time['Nations'].iloc[-1]), unsafe_allow_html=True)

        # Cumulative growth chart
        cumulative_df = nations_over_time.copy()
        cumulative_df['Cumulative Nations'] = cumulative_df['Nations'].cumsum()
        fig = px.area(cumulative_df, x="Edition", y="Cumulative Nations",
                      template="plotly_white",
                      color_discrete_sequence=["#00bfa5"],
                      labels={'Cumulative Nations': 'Total Nations'},
                      height=300)
        fig.update_layout(
            title="Cumulative Participation",
            margin=dict(t=40, b=20),
            showlegend=False
        )
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

    # --- Event Distribution Analysis ---
    st.markdown(
        "<h2 style='color: #1a237e; border-bottom: 2px solid #0d47a1; padding-bottom: 0.5rem;'>📈 Sport Evolution Matrix</h2>",
        unsafe_allow_html=True)

    with st.spinner('Generating sports evolution matrix...'):
        fig, ax = plt.subplots(figsize=(20, 15))
        pivot_data = df.drop_duplicates(['Year', 'Sport', 'Event']) \
            .pivot_table(index='Sport', columns='Year', values='Event', aggfunc='count') \
            .fillna(0).astype(int)

        sns.heatmap(pivot_data, cmap="YlGnBu", annot=True, fmt="d",
                    linewidths=.5, ax=ax, cbar_kws={'label': 'Number of Events'})
        ax.set_title("Sport-Specific Event Growth Over Time", pad=20, fontsize=16)
        ax.set_xlabel("Olympic Year", labelpad=15, fontsize=12)
        ax.set_ylabel("Sports Category", labelpad=15, fontsize=12)
        ax.tick_params(axis='x', rotation=45, labelsize=10)
        ax.tick_params(axis='y', labelsize=10)
        st.pyplot(fig)

    st.markdown("---")

    # --- Athlete Performance Analysis ---
    st.markdown(
        "<h2 style='color: #1a237e; border-bottom: 2px solid #0d47a1; padding-bottom: 0.5rem;'>🏅 Elite Athletes Spotlight</h2>",
        unsafe_allow_html=True)

    sport_list = ['Overall'] + sorted(df['Sport'].unique().tolist())
    selected_sport = st.selectbox('Select Sport Discipline:', sport_list, key='athlete_sport')

    with st.spinner(f'Analyzing top performers in {selected_sport}...'):
        top_athletes = helper.most_successful(df, selected_sport)

        # Styled dataframe with medals
        st.dataframe(
            top_athletes.style
            .background_gradient(subset=['Medals'], cmap='Blues')
            .format({'Medals': "{} 🏅"}), use_container_width=True, height=500, hide_index=True
        )

    # Footer visible at the bottom only in "Overall Analysis"
    st.markdown("""
        <footer class="footer">
            <div style="background: linear-gradient(90deg, #1a237e, #6a1b9a); padding: 20px 0; border-radius: 10px;">
                <p style="font-size: 1.2rem; font-weight: bold; margin: 0;">
                    Developed by Umesh Pathak | 🌍 Olympic Medal Data
                </p>
                <p style="font-size: 1rem; margin: 5px 0;">&copy; 2025 All rights reserved.</p>
            </div>
        </footer>
    """, unsafe_allow_html=True)

# Country-wise Analysis
if user_menu == 'Country-wise Analysis':
    try:
        # Sidebar Configuration
        with st.sidebar:
            st.title('🌍 Country Analysis')
            country_list = sorted(df['region'].dropna().unique().tolist())
            selected_country = st.selectbox(
                'Select a Country',
                country_list,
                help="Choose a country to analyze its Olympic performance"
            )

        # Country Medal Tally
        st.markdown(
            f"<div style='text-align: center; padding: 40px; background: linear-gradient(45deg, #1a237e, #6a1b9a); border-radius: 15px;'>"
            f"<h1 style='color:white; font-size: 3rem; font-weight: bold; font-family: 'Arial', sans-serif;'>"
            f"{selected_country}'s Olympic Journey</h1></div>",
            unsafe_allow_html=True)

        country_df = helper.yearwise_medal_tally(df, selected_country)

        # Ensure medal columns exist
        for medal in ['Gold', 'Silver', 'Bronze']:
            if medal not in country_df.columns:
                country_df[medal] = 0  # Initialize missing columns

        col1, col2 = st.columns([3, 1])
        with col1:
            fig = px.line(
                country_df,
                x="Year",
                y="Medal",
                markers=True,
                color_discrete_sequence=["#1E88E5"],
                template="plotly_white",
                labels={'Medal': 'Total Medals'},
                title=f"{selected_country}'s Medal Progression"
            )
            fig.update_layout(hovermode="x unified", title_font=dict(size=22), title_x=0.5)
            fig.update_traces(marker=dict(size=8), line=dict(width=3))
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            st.markdown(f"""
                <div style="
                    background: #ffffff;
                    padding: 3rem;
                    border-radius: 15px;
                    box-shadow: 0 6px 12px rgba(0,0,0,0.1);
                    text-align: center;
                    margin-top: 2rem;
                    transition: transform 0.3s ease, box-shadow 0.3s ease;
                    cursor: pointer;
                " onmouseover="this.style.transform='scale(1.1)'; this.style.boxShadow='0px 8px 20px rgba(0,0,0,0.2)';" 
                onmouseout="this.style.transform='scale(1)'; this.style.boxShadow='0px 6px 12px rgba(0,0,0,0.1);'">
                    <h3>🥇 Total Gold: {country_df['Gold'].sum()}</h3>
                    <h3>🥈 Total Silver: {country_df['Silver'].sum()}</h3>
                    <h3>🥉 Total Bronze: {country_df['Bronze'].sum()}</h3>
                </div>
            """, unsafe_allow_html=True)

        # Sport Dominance Heatmap
        st.markdown(f"<h2 style='color:#1a237e;'>🏅 {selected_country}'s Sport Specialization</h2>",
                    unsafe_allow_html=True)

        with st.spinner('Analyzing sport performance...'):
            heatmap_data = helper.country_event_heatmap(df, selected_country)
            fig, ax = plt.subplots(figsize=(18, 12))
            sns.heatmap(
                heatmap_data,
                annot=True,
                cmap="YlGnBu",
                fmt="g",
                linewidths=.5,
                ax=ax
            )
            ax.set_title(f"{selected_country}'s Medal Distribution by Sport and Year", pad=20)
            ax.set_xlabel("Olympic Year", labelpad=15)
            ax.set_ylabel("Sports Discipline", labelpad=15)
            st.pyplot(fig)

        # Top Athletes Section
        st.markdown(f"<h2 style='color:#1a237e;'>🌟 {selected_country}'s Olympic Legends</h2>",
                    unsafe_allow_html=True)

        top_athletes = helper.most_successful_countrywise(df, selected_country)

        st.markdown("""
            <div style="background: linear-gradient(135deg, #1a237e, #6a1b9a); padding: 20px 0; border-radius: 12px; text-align: center;">
                <p style="font-size: 1.2rem; font-weight: bold; color: white; margin: 0;">Top Athletes</p>
            </div>
        """, unsafe_allow_html=True)

        st.dataframe(
            top_athletes.style
            .background_gradient(subset=['Medals'], cmap='Blues')
            .format({'Medals': "{} 🏅"}),
            column_config={
                "Name": "Athlete Name",
                "Sport": "Sport Discipline",
                "Medals": st.column_config.NumberColumn(
                    "Total Medals",
                    help="Number of medals won",
                    format="%d 🏅"
                )
            },
            use_container_width=True,
            hide_index=True
        )

        # Footer at the Bottom
        st.markdown("""
            <footer style="position: relative; bottom: 0; width: 100%; background-color: #1a237e; color: white; padding: 20px 0; text-align: center; box-shadow: 0 4px 10px rgba(0, 0, 0, 0.2); border-top: 3px solid #6a1b9a;">
                <div style="background: linear-gradient(135deg, #1a237e, #6a1b9a); padding: 20px 0; border-radius: 12px; text-align: center;">
                    <p style="font-size: 1.2rem; font-weight: bold; color: white; margin: 0;">
                        Developed by Umesh Pathak | 🌍 Olympic Medal Data
                    </p>
                    <p style="font-size: 1rem; color: white; margin: 5px 0;">&copy; 2025 All rights reserved.</p>
                </div>
            </footer>
        """, unsafe_allow_html=True)

    except Exception as e:
        st.error(f"Error loading country data: {str(e)}")
        st.stop()

# Athlete-wise Analysis
if user_menu == 'Athlete-wise Analysis':
    athlete_df = df.drop_duplicates(subset=['Name', 'region'])

    # Header with modern styling and background
    st.markdown("""
    <div style="text-align: center; margin-bottom: 3rem; background-color: #1a237e; padding: 30px; border-radius: 12px;">
        <img src="https://upload.wikimedia.org/wikipedia/commons/thumb/5/5c/Olympic_rings_without_rims.svg/1200px-Olympic_rings_without_rims.svg.png" 
             width="200" style="margin-bottom: 1rem;">
        <h1 style="color: white; font-size: 2.5rem; font-weight: bold; text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.5);">🏅 Athlete Performance Analysis</h1>
    </div>
    """, unsafe_allow_html=True)

    # Age Distribution with modern card styling
    st.markdown("""
    <div style="background: linear-gradient(135deg, #1a237e, #6a1b9a); padding: 2rem; border-radius: 15px; margin-bottom: 3rem;">
        <h2 style="color: white; font-size: 1.75rem; text-align: center;">📊 Age Distribution Patterns</h2>
    </div>
    """, unsafe_allow_html=True)

    age_data = {
        '🏃 Overall': athlete_df['Age'].dropna(),
        '🥇 Gold Medalists': athlete_df[athlete_df['Medal'] == 'Gold']['Age'].dropna(),
        '🥈 Silver Medalists': athlete_df[athlete_df['Medal'] == 'Silver']['Age'].dropna(),
        '🥉 Bronze Medalists': athlete_df[athlete_df['Medal'] == 'Bronze']['Age'].dropna()
    }

    fig = ff.create_distplot(
        list(age_data.values()),
        list(age_data.keys()),
        colors=["#1E88E5", "#FFD700", "#C0C0C0", "#CD7F32"],
        show_hist=False,
        show_rug=False
    )
    fig.update_layout(
        template="plotly_dark",  # Dark theme for modern look
        plot_bgcolor="rgba(0,0,0,0)",
        height=500,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        title="Age Distribution of Athletes by Medal Type"
    )
    st.plotly_chart(fig, use_container_width=True)

    # Sport-specific age distribution with modern image styling
    st.markdown("""
    <div style="background: #f8f9fa; padding: 2rem; border-radius: 15px; margin-bottom: 3rem;">
        <h2 style="color: #1a237e; font-size: 1.75rem;">🏋️ Age Trends by Sport (Gold Medalists)</h2>
        <img src="https://www.pngall.com/wp-content/uploads/4/Olympic-Gold-Medal-PNG.png" 
             width="100" style="float: right; margin-top: -60px;">
    </div>
    """, unsafe_allow_html=True)

    sports = ['Basketball', 'Judo', 'Football', 'Tug-Of-War', 'Athletics',
              'Swimming', 'Badminton', 'Sailing', 'Gymnastics', 'Art Competitions',
              'Handball', 'Weightlifting', 'Wrestling', 'Water Polo', 'Hockey',
              'Rowing', 'Fencing', 'Shooting', 'Boxing', 'Taekwondo', 'Cycling',
              'Diving', 'Canoeing', 'Tennis', 'Golf', 'Softball', 'Archery',
              'Volleyball', 'Synchronized Swimming', 'Table Tennis', 'Baseball',
              'Rhythmic Gymnastics', 'Rugby Sevens', 'Beach Volleyball',
              'Triathlon', 'Rugby', 'Polo', 'Ice Hockey']

    gold_ages = [athlete_df[(athlete_df['Sport'] == sport) &
                            (athlete_df['Medal'] == 'Gold')]['Age'].dropna()
                 for sport in sports]

    fig = ff.create_distplot(gold_ages, sports,
                             colors=["#FFD700"] * len(sports),
                             show_hist=False,
                             show_rug=False)
    fig.update_layout(
        template="plotly_dark",
        height=600,
        showlegend=False,
        xaxis_title="Age",
        yaxis_title="Density",
        title="Age Distribution of Gold Medalists by Sport"
    )
    st.plotly_chart(fig, use_container_width=True)

    # Height vs Weight analysis with more polished visuals
    st.markdown("""
    <div style="background: linear-gradient(135deg, #1a237e, #6a1b9a); padding: 2rem; border-radius: 15px; margin-bottom: 3rem;">
        <h2 style="color: white; font-size: 1.75rem;">🏋️ Athlete Physique Analysis</h2>
        <img src="https://www.freeiconspng.com/uploads/olympic-weightlifting-icon-4.png" 
             width="80" style="float: right; margin-top: -50px;">
    </div>
    """, unsafe_allow_html=True)

    sport_list = ['Overall'] + sorted(df['Sport'].unique().tolist())
    selected_sport = st.selectbox('Select Sport Discipline', sport_list, key='sport_select')
    analysis_df = weight_v_height(df, selected_sport)

    fig, ax = plt.subplots(figsize=(10, 6))
    sns.scatterplot(
        data=analysis_df,
        x='Weight',
        y='Height',
        hue='Medal',
        style='Sex',
        palette={'Gold': '#FFD700', 'Silver': '#C0C0C0', 'Bronze': '#CD7F32', 'No Medal': '#757575'},
        s=120,
        ax=ax
    )
    ax.set_title(f"Height vs Weight Distribution ({selected_sport})", pad=20, fontsize=16, color='#1a237e', fontweight='bold')
    ax.set_xlabel("Weight (kg)", labelpad=15, fontsize=14, color='#1a237e')
    ax.set_ylabel("Height (cm)", labelpad=15, fontsize=14, color='#1a237e')
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    st.pyplot(fig)

    # Gender participation with enhanced visual style
    st.markdown("""
    <div style="background: #f8f9fa; padding: 2rem; border-radius: 15px; margin-bottom: 3rem;">
        <h2 style="color: #1a237e; font-size: 1.75rem;">🚻 Gender Participation Evolution</h2>
        <img src="https://www.pngall.com/wp-content/uploads/12/Olympics-Logo-PNG-Clipart.png" 
             width="120" style="float: right; margin-top: -60px;">
    </div>
    """, unsafe_allow_html=True)

    gender_data = men_vs_women(df)
    fig = px.line(
        gender_data.melt(id_vars='Year', var_name='Gender', value_name='Count'),
        x='Year',
        y='Count',
        color='Gender',
        color_discrete_map={'Male': '#1E88E5', 'Female': '#D81B60'},
        markers=True,
        template="plotly_dark"
    )
    fig.update_layout(
        height=400,
        xaxis_title="Olympic Year",
        yaxis_title="Number of Athletes",
        legend_title="Gender",
        plot_bgcolor="rgba(0,0,0,0)",
        title="Gender Participation Over the Years"
    )
    st.plotly_chart(fig, use_container_width=True)

    # Footer at the Bottom
    st.markdown("""
        <footer style="position: relative; bottom: 0; width: 100%; background-color: #1a237e; color: white; padding: 20px 0; text-align: center; box-shadow: 0 4px 10px rgba(0, 0, 0, 0.2); border-top: 3px solid #6a1b9a;">
            <div style="background: linear-gradient(135deg, #1a237e, #6a1b9a); padding: 20px 0; border-radius: 12px; text-align: center;">
                <p style="font-size: 1.2rem; font-weight: bold; color: white; margin: 0;">
                    Developed by Umesh Pathak | 🌍 Olympic Medal Data
                </p>
                <p style="font-size: 1rem; color: white; margin: 5px 0;">&copy; 2025 All rights reserved.</p>
            </div>
        </footer>
    """, unsafe_allow_html=True)

# Top Athletes
if user_menu == 'Top Athletes':
    st.markdown("""
    <div style="text-align: center; margin-bottom: 3rem; background-color: #1a237e; padding: 30px; border-radius: 12px;">
        <img src="https://upload.wikimedia.org/wikipedia/commons/thumb/5/5c/Olympic_rings_without_rims.svg/1200px-Olympic_rings_without_rims.svg.png" 
             width="200" style="margin-bottom: 1rem;">
        <h1 style="color: white; font-size: 2.5rem; font-weight: bold; text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.5);">🏅 Top Athletes</h1>
    </div>
    """, unsafe_allow_html=True)

    # Example - Display top athletes with the highest medal counts
    top_athletes = df.groupby('Name')['Medal'].value_counts().unstack(fill_value=0)
    top_athletes['Total Medals'] = top_athletes.sum(axis=1)
    top_athletes_sorted = top_athletes.sort_values('Total Medals', ascending=False).head(10)
    st.write(top_athletes_sorted[['Total Medals']])

    # Footer for this section
    st.markdown("""
        <footer style="position: relative; bottom: 0; width: 100%; background-color: #1a237e; color: white; padding: 20px 0; text-align: center; box-shadow: 0 4px 10px rgba(0, 0, 0, 0.2); border-top: 3px solid #6a1b9a;">
            <div style="background: linear-gradient(135deg, #1a237e, #6a1b9a); padding: 20px 0; border-radius: 12px; text-align: center;">
                <p style="font-size: 1.2rem; font-weight: bold; color: white; margin: 0;">
                    Developed by Umesh Pathak | 🌍 Olympic Medal Data
                </p>
                <p style="font-size: 1rem; color: white; margin: 5px 0;">&copy; 2025 All rights reserved.</p>
            </div>
        </footer>
    """, unsafe_allow_html=True)

# Olympic Games Locations
if user_menu == 'Olympic Games Locations':
    st.markdown("""
    <div style="text-align: center; margin-bottom: 3rem; background-color: #1a237e; padding: 30px; border-radius: 12px;">
        <img src="https://upload.wikimedia.org/wikipedia/commons/thumb/5/5c/Olympic_rings_without_rims.svg/1200px-Olympic_rings_without_rims.svg.png" 
             width="200" style="margin-bottom: 1rem;">
        <h1 style="color: white; font-size: 2.5rem; font-weight: bold; text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.5);">🌍 Olympic Games Locations</h1>
    </div>
    """, unsafe_allow_html=True)

    # Display Olympic locations (example)
    locations = df[['City', 'Year']].drop_duplicates().sort_values('Year')
    st.write(locations)

    # Footer for this section
    st.markdown("""
        <footer style="position: relative; bottom: 0; width: 100%; background-color: #1a237e; color: white; padding: 20px 0; text-align: center; box-shadow: 0 4px 10px rgba(0, 0, 0, 0.2); border-top: 3px solid #6a1b9a;">
            <div style="background: linear-gradient(135deg, #1a237e, #6a1b9a); padding: 20px 0; border-radius: 12px; text-align: center;">
                <p style="font-size: 1.2rem; font-weight: bold; color: white; margin: 0;">
                    Developed by Umesh Pathak | 🌍 Olympic Medal Data
                </p>
                <p style="font-size: 1rem; color: white; margin: 5px 0;">&copy; 2025 All rights reserved.</p>
            </div>
        </footer>
    """, unsafe_allow_html=True)

# Olympics Trivia
if user_menu == 'Olympics Trivia':
    st.markdown("""
    <div style="text-align: center; margin-bottom: 3rem; background-color: #1a237e; padding: 30px; border-radius: 12px;">
        <img src="https://upload.wikimedia.org/wikipedia/commons/thumb/5/5c/Olympic_rings_without_rims.svg/1200px-Olympic_rings_without_rims.svg.png" 
             width="200" style="margin-bottom: 1rem;">
        <h1 style="color: white; font-size: 2.5rem; font-weight: bold; text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.5);">🏆 Olympics Trivia</h1>
    </div>
    """, unsafe_allow_html=True)

    # Example - Random trivia facts about Olympics
    trivia_facts = [
        "The first modern Olympic Games were held in 1896 in Athens, Greece.",
        "The Olympic Games were originally a religious festival in honor of Zeus.",
        "The Olympic motto is 'Citius, Altius, Fortius' - Faster, Higher, Stronger."
    ]
    for fact in trivia_facts:
        st.markdown(f"- {fact}")

    # Footer for this section
    st.markdown("""
        <footer style="position: relative; bottom: 0; width: 100%; background-color: #1a237e; color: white; padding: 20px 0; text-align: center; box-shadow: 0 4px 10px rgba(0, 0, 0, 0.2); border-top: 3px solid #6a1b9a;">
            <div style="background: linear-gradient(135deg, #1a237e, #6a1b9a); padding: 20px 0; border-radius: 12px; text-align: center;">
                <p style="font-size: 1.2rem; font-weight: bold; color: white; margin: 0;">
                    Developed by Umesh Pathak | 🌍 Olympic Medal Data
                </p>
                <p style="font-size: 1rem; color: white; margin: 5px 0;">&copy; 2025 All rights reserved.</p>
            </div>
        </footer>
    """, unsafe_allow_html=True)

# Predictions
if user_menu == 'Predictions':
    st.markdown("""
    <div style="text-align: center; margin-bottom: 3rem; background-color: #1a237e; padding: 30px; border-radius: 12px;">
        <img src="https://upload.wikimedia.org/wikipedia/commons/thumb/5/5c/Olympic_rings_without_rims.svg/1200px-Olympic_rings_without_rims.svg.png" 
             width="200" style="margin-bottom: 1rem;">
        <h1 style="color: white; font-size: 2.5rem; font-weight: bold; text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.5);">🔮 Predictions</h1>
    </div>
    """, unsafe_allow_html=True)

    # Example - Predicting future Olympic medal trends (mock data)
    st.markdown("""
    The predictions are based on current trends and data. These include analysis of past performance, regional trends, and potential top-performing countries in future Olympics.
    """)

    # For illustration: Create a simple line chart with predicted medal trends (mock data)
    predicted_years = [2028, 2032, 2036, 2040]
    predicted_medals = [100, 110, 120, 130]
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(predicted_years, predicted_medals, marker='o', color='#FFD700', label='Predicted Gold Medals')
    ax.set_title("Predicted Gold Medal Trends", fontsize=16)
    ax.set_xlabel("Year", fontsize=14)
    ax.set_ylabel("Number of Gold Medals", fontsize=14)
    st.pyplot(fig)

    # Footer for this section
    st.markdown("""
        <footer style="position: relative; bottom: 0; width: 100%; background-color: #1a237e; color: white; padding: 20px 0; text-align: center; box-shadow: 0 4px 10px rgba(0, 0, 0, 0.2); border-top: 3px solid #6a1b9a;">
            <div style="background: linear-gradient(135deg, #1a237e, #6a1b9a); padding: 20px 0; border-radius: 12px; text-align: center;">
                <p style="font-size: 1.2rem; font-weight: bold; color: white; margin: 0;">
                    Developed by Umesh Pathak | 🌍 Olympic Medal Data
                </p>
                <p style="font-size: 1rem; color: white; margin: 5px 0;">&copy; 2025 All rights reserved.</p>
            </div>
        </footer>
    """, unsafe_allow_html=True)
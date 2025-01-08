import streamlit as st
from analytics import get_alltime_podium, get_over_under_perform_plot, streamlit_over_under_perform


st.set_page_config(layout="wide")

st.title("THE 55-28 MUSEUM")
st.header("ALL TIME LEADERBOARD")

st.dataframe(get_alltime_podium(), use_container_width=True)

years = st.selectbox("Select Year", ["All-time"] + list(range(2015, 2025)))

st.pyplot(fig=get_over_under_perform_plot())

streamlit_over_under_perform()

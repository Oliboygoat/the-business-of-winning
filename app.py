"""Application entry point: compose five sections without changing the math layer."""
import streamlit as st
from analytics import ROOT, load_data
from ui import install_design
from analyst.ui import render_analyst
from sections import overview, explore, insights, methodology
from multi_analytics import load_panel, cohort
from multi_ui import seasonal_overview, seasonal_insights, multi_overview, multi_explore, multi_insights, multi_methodology

st.set_page_config(page_title='The Business of Winning',page_icon='◈',layout='wide')
install_design()

@st.cache_data(show_spinner='Loading six seasons…')
def get_panel(csv_bytes, cpi_bytes):
    return load_panel()

@st.cache_data(show_spinner='Preparing the 2025 season…')
def get_data(csv_bytes):
    # Bytes form a cache key so changes to the source file cannot leave stale charts.
    return load_data()

try:
    full=get_data((ROOT/'data/teams_2025.csv').read_bytes())
except (ValueError,OSError,KeyError,TypeError) as exc:
    st.error(f'The saved dataset could not be loaded: {exc}. See README for rebuilding instructions.')
    st.stop()

try:
    panel=get_panel((ROOT/'data/multiseason/teams_2021_2026.csv').read_bytes(),(ROOT/'data/multiseason/cpi_march.csv').read_bytes())
except (ValueError,OSError,KeyError,TypeError) as exc:
    st.error(f'The multi-season dataset could not be loaded: {exc}. See MULTISEASON_SOURCES.md for source definitions.')
    st.stop()
label, control=st.columns([3,1])
with control:
    season=st.selectbox('Season',list(range(2021,2027))+['Multi-year'],index=4,key='season')
with label:
    st.caption('2021–2026 · 30 franchises · Opening Day payroll')
if season == 'Multi-year':
    with st.expander('Choose seasons to compare',expanded=False):
        years=st.slider('Season range',2021,2026,(2021,2026),key='year_range')
        include_alternate=st.checkbox('Include 2022 from a different payroll source (The Baseball Cube)',value=False,key='include_alternate')
        st.caption('2022 uses The Baseball Cube rather than Associated Press (AP). Its payroll accounting may differ, so it is left out by default.')
    active=cohort(panel,include_alternate,range(years[0],years[1]+1)) if include_alternate or years != (2022,2022) else None
    if active is None:
        st.info('2022 has no verified AP table in this release. Include The Baseball Cube’s 2022 data or widen the season range.')
        st.stop()
    if include_alternate and 2022 in active.season.values:
        st.warning('Different payroll sources: includes The Baseball Cube (TBC) for 2022 alongside Associated Press (AP) years. Changes may reflect accounting differences as well as spending.')
    else:
        st.caption('Comparable AP seasons: '+', '.join(str(y) for y in sorted(active.season.unique()))+' · 2022 left out because its payroll source differs.')
else:
    active=panel[panel.season==season].copy()
    if season==2022:
        st.warning('2022 uses The Baseball Cube Opening Day payroll. These are not AP figures; accounting may differ. Left out of default multi-year comparisons.')
    else:
        st.caption(f'{season} · AP Opening Day payroll · Final regular-season results')

overview_tab,explore_tab,insights_tab,analyst_tab,methodology_tab=st.tabs(
    ['Overview','Explore Teams','Insights','AI Analyst','Methodology'],key='main_nav',on_change='rerun')
with overview_tab:
    if season == 'Multi-year':multi_overview(active)
    elif season == 2025:overview(full)
    else:seasonal_overview(active,season)
with explore_tab:
    if season == 'Multi-year':multi_explore(active)
    else:explore(active)
with insights_tab:
    if season == 'Multi-year':multi_insights(active)
    elif season == 2025:insights(full)
    else:seasonal_insights(active,season)
with analyst_tab:
    render_analyst(panel,tuple(sorted(active.season.unique().tolist())))
with methodology_tab:
    multi_methodology(active)
    if season == 2025:
        with st.expander('Original 2025 source notes and downloads'):
            methodology(full)
st.html('<div class="footer">THE BUSINESS OF WINNING &nbsp; / &nbsp; 2021–2026 MLB &nbsp; · &nbsp; Opening Day payroll. Regular-season results.</div>')

"""Small reusable visual components. All styling stays outside the math layer."""
from html import escape
import streamlit as st
from analytics import ROOT


def install_design():
    st.html('<style>' + (ROOT / 'assets/style.css').read_text() + '</style>')
    st.html('<div class="masthead"><div class="brand"><span class="brand-mark" aria-hidden="true"></span>The Business of Winning</div><div class="season-label">MLB / 2021–2026</div></div>')


def hero():
    st.html('<div class="hero"><div class="eyebrow">Baseball. Through a business lens.</div><h1>The Business of Winning</h1><p class="hero-subtitle">Understanding the economics of winning in Major League Baseball.</p><p class="hero-intro">Compare Opening Day payroll with regular-season results across all 30 teams. See how spending and success compare.</p></div>')


def section_header(title, description):
    st.html(f'<div class="section-head"><h2>{escape(title)}</h2><p class="section-note">{escape(description)}</p></div>')


def plot(fig, key=None):
    fig.update_layout(template='plotly_white', paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
        font=dict(family='-apple-system, BlinkMacSystemFont, Segoe UI, sans-serif', size=14, color='#59616e'),
        margin=dict(l=12,r=20,t=35,b=30), hoverlabel=dict(bgcolor='#fff',font_color='#1d1d1f',bordercolor='#e1e5eb'),
        legend=dict(title_text='', orientation='h', yanchor='bottom',y=1.03,x=0),
        modebar=dict(bgcolor='rgba(0,0,0,0)',color='#8a95a5',activecolor='#246bd1'))
    fig.update_xaxes(gridcolor='#eef0f4',zeroline=False,automargin=True,title_standoff=15)
    fig.update_yaxes(gridcolor='#eef0f4',zeroline=False,automargin=True,title_standoff=15)
    fig.update_xaxes(title_font_size=13)
    fig.update_yaxes(title_font_size=13)
    st.plotly_chart(fig,width='stretch',key=key,config={'displaylogo':False,'scrollZoom':False,'modeBarButtonsToRemove':['lasso2d','select2d']})


def navigate(section):
    st.session_state['main_nav'] = section


def card(key):
    return st.container(border=True,key='card_'+key)

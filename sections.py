"""Four product sections, composed from shared UI and verified analytics."""
import json
import plotly.express as px
import streamlit as st
from analytics import ROOT, regression, executive_summary
from charts import COLORS, payroll_scatter, residual_bars, ranking_bars
from executive import render_executive_summary
from ui import hero, section_header, plot, navigate, card


def overview(full):
    hero()
    fit=regression(full)
    best=full.sort_values('cost_per_win').iloc[0]
    a,b,c,d=st.columns(4)
    a.metric('Total MLB payroll',f'${full.payroll.sum()/1e9:.2f}B',help=f'Opening Day payroll for all 30 teams: ${full.payroll.sum():,}. Not full-season spending.')
    b.metric('Average team wins',f'{full.wins.mean():.1f}',help='Regular season only. Every team played 162 games.')
    c.metric('Spending and wins: connection',f"{fit['r']:.3f}",help='From −1 to +1: positive values mean higher-payroll teams tended to win more. Zero means no straight-line connection. This does not show that spending caused wins.')
    d.metric('Lowest payroll per win',best.team,help=f'Lowest Opening Day payroll per win: ${best.cost_per_win:,.2f}. This does not measure profit.')
    st.write('')
    with card('overview_plot'):
        title,control=st.columns([2.4,1])
        with title:
            st.subheader('Does a bigger payroll mean more wins?')
            st.caption('Each point is one team. The line shows the season’s payroll-based benchmark, not a guaranteed outcome.')
        with control:
            highlighted=st.selectbox('Highlight a team',['No highlight']+full.team.tolist(),key='spotlight',
                help='Add a blue ring and name to a team without changing the data or benchmark.')
        plot(payroll_scatter(full,highlighted),key='overview_scatter')
        st.caption('$M means millions of dollars. AL = American League; NL = National League.')
        st.caption('Opening Day payroll · 2025 regular-season wins · Dashed line: payroll-based benchmark · Hover for exact figures')
    section_header('Beyond the trend line','A few starting points. A deeper story in Insights.')
    first,second=st.columns(2)
    summary=executive_summary(full)
    gap=summary['brewers_vs_mets']
    with first,card('highlight_result'):
        st.caption('RESULTS OVER SPENDING')
        st.subheader(f"{gap['wins_more']} more wins. Less payroll.")
        st.write(f"Milwaukee won {int(summary['teams'][158]['wins'])} games versus New York’s {int(summary['teams'][121]['wins'])}, with \\${gap['payroll_less']:,} less Opening Day payroll.")
    with second,card('highlight_context'):
        st.caption('KEEP THE CONTEXT')
        st.subheader(f"{fit['r_squared']:.1%} of the differences in wins")
        st.write('The model links payroll with this share of the differences in team wins. It does not show that payroll caused those differences.')
    st.button('Explore the insights →',on_click=navigate,args=('Insights',),key='insights_link',type='primary')
    st.caption('Payroll is only part of a team’s spending. Payroll per win does not measure profit.')


def explore(full):
    year=int(full.season.iloc[0]) if 'season' in full else 2025
    section_header('Explore Teams','Compare team spending, wins, and results against the payroll benchmark.')
    with card('filters'):
        left,right=st.columns([1,2])
        with left:
            league=st.selectbox('League',['All MLB','AL','NL'],key='league_filter',help='AL = American League. NL = National League.')
        eligible=full if league=='All MLB' else full[full.league==league]
        with right:
            divisions=st.multiselect('Divisions',sorted(eligible.division.unique()),key='division_filter',
                placeholder='All divisions',help='Leave empty to include every division in the selected league.')
        view=eligible if not divisions else eligible[eligible.division.isin(divisions)]
        st.caption('Filters apply to this section’s rankings and performance chart. Rankings still use all 30 teams, and the benchmark does not change. Side-by-side comparisons use the full team list.')
    a,b,c,d=st.columns(4)
    a.metric('Teams in view',len(view))
    b.metric('Payroll in view',f'${view.payroll.sum()/1e9:.2f}B')
    c.metric('Average wins in view',f'{view.wins.mean():.1f}' if len(view) else '—')
    d.metric('Lowest payroll per win in view',f'${view.cost_per_win.min()/1e6:.2f}M' if len(view) else '—',
        help='Opening Day payroll divided by regular-season wins. A lower number means less payroll per win, not necessarily a better team or more profit.')
    # Defensive state for future filter extensions; current valid selections always contain teams.
    if view.empty:
        st.info('No teams match these filters. Clear a division or choose another league.')
        return
    with st.expander('How did teams do against the payroll benchmark?',expanded=False):
        st.caption('Actual wins minus the model’s benchmark. Positive numbers mean more wins; negative numbers mean fewer. Neither proves good or bad management.')
        plot(residual_bars(view),key='residual_chart')
    section_header('Who gets more wins for the spending?','Compare payroll per win or wins ahead of the model’s benchmark. These answer different questions.')
    with card('ranking'):
        metric=st.radio('Rank by',['Payroll per win','Wins ahead of payroll benchmark'],horizontal=True,key='rank_metric',
            help='Payroll per win: lower means less spending per win. Wins ahead of the benchmark: higher means more wins than the model predicted. MLB rank always uses payroll per win.')
        field='cost_per_win' if metric=='Payroll per win' else 'wins_above_fit'
        ranked=view.sort_values(field,ascending=field=='cost_per_win')
        plot(ranking_bars(ranked,field),key='rank_chart')
        st.caption(f'Top {min(15,len(ranked))} in this view · Payroll per win includes all wins, including wins even a much cheaper roster might earn.')
    cols=['efficiency_rank','team','league','payroll','wins','losses','win_pct','cost_per_win','wins_above_fit']
    st.dataframe(ranked[cols],hide_index=True,width='stretch',column_config={
        'efficiency_rank':st.column_config.NumberColumn('MLB rank',help='Ranked across all 30 teams by lowest cost per win.'),
        'team':'Team','league':'League','wins':'Wins','losses':'Losses',
        'payroll':st.column_config.NumberColumn('Payroll ($)',format='$%,d'),
        'cost_per_win':st.column_config.NumberColumn('Payroll per win ($)',format='$%,.0f'),
        'win_pct':st.column_config.NumberColumn('Share of games won',format='%.3f'),
        'wins_above_fit':st.column_config.NumberColumn('Wins ahead of benchmark',format='%.1f',help='Actual wins minus the benchmark from the full 30-team model. This is a comparison, not a forecast.')})
    st.download_button('Download this view',ranked.to_csv(index=False).encode(),f'mlb_{year}_analytics.csv','text/csv',key='analytics_download')
    section_header('Side by side','Choose any two to six teams. Compare costs and results in their own units.')
    with card('comparison'):
        teams=st.multiselect('Choose 2–6 teams',full.team.tolist(),
            default=['Los Angeles Dodgers','Milwaukee Brewers','New York Mets'],max_selections=6,key='comparison_teams',placeholder='Search teams…')
        st.caption('Comparison uses the full MLB list independently of the league and division filters.')
        if len(teams)<2:
            st.info('Choose at least two teams to compare.')
        else:
            chosen=full.set_index('team').loc[teams].reset_index()
            left,right=st.columns(2)
            with left:
                plot(px.bar(chosen,x='team',y='payroll_millions',color='league',color_discrete_map=COLORS,
                    labels={'team':'','payroll_millions':'Opening Day payroll ($M)'},height=340),key='comparison_payroll')
            with right:
                plot(px.bar(chosen,x='team',y='wins',color='league',color_discrete_map=COLORS,
                    labels={'team':'','wins':'Regular-season wins'},height=340),key='comparison_wins')
            labels={'payroll_millions':'Payroll ($M)','wins':'Wins','losses':'Losses','cost_per_win':'Payroll per win ($)',
                'efficiency_rank':'MLB payroll-per-win rank','run_differential':'Runs scored minus runs allowed','wins_above_fit':'Wins ahead of payroll benchmark'}
            table=chosen.set_index('team')[list(labels)].T.rename(index=labels)
            styled=table.style.format('{:,.2f}')
            styled=styled.format('{:,.0f}',subset=([name for name in table.index if name in ['Wins','Losses','MLB payroll-per-win rank','Runs scored minus runs allowed']],table.columns))
            st.dataframe(styled,width='stretch')


def insights(full):
    section_header('Insights','What the numbers reveal — and what they cannot tell us.')
    render_executive_summary(full)
    with st.expander('View detailed statistics',expanded=False):
        st.caption('All 30 teams · Ordinary least squares · Opening Day payroll in millions of dollars')
        fit=regression(full)
        a,b,c=st.columns(3)
        a.metric('Pearson correlation (r)',f"{fit['r']:.3f}")
        b.metric('R²',f"{fit['r_squared']:.1%}")
        c.metric('Slope: wins per $10M',f"{fit['slope']*10:.2f}")
        st.write(f"**Fitted equation:** wins = {fit['intercept']:.2f} + {fit['slope']:.3f} × payroll in \\$M.")
        st.write(f"**Two-sided slope p-value:** {fit['p_value']:.4f} (n = 30). This is a model-based test of a zero linear association, not a test of whether payroll causes wins.")
        st.warning('This is descriptive analysis, not a spending recommendation. A single season cannot separate payroll from injuries, player development, roster quality, schedule, luck, or management. Teams play each other, so the observations are not fully independent. The p-value relies on assumptions such as independent, similarly variable errors; treat it cautiously.')


def methodology(full):
    section_header('Methodology','Clear sources. Consistent definitions. Visible limitations.')
    with card('sources'):
        st.subheader('The data behind the dashboard')
        st.markdown((ROOT/'DATA_SOURCES.md').read_text())
    with st.expander('A plain-English statistical glossary',expanded=False):
        st.markdown('''- **Correlation (r)** describes how closely spending and wins move together in a straight-line pattern. It does not establish cause.
- **R²** is the share of differences in wins summarized by this fitted line within this dataset.
- **Residual** means actual wins minus fitted wins. A positive value means a team won more than the line suggests for its payroll.
- **Cost per win** divides payroll by all wins. It rewards low spending and includes wins a team might earn even with a much cheaper roster.
- **Sensitivity check** refits the model without Colorado to see how much the result changes. Colorado remains in the primary analysis.''')
    with st.expander('Descriptive statistics'):
        st.dataframe(full[['payroll_millions','wins','cost_per_win','run_differential']].describe().rename(
            columns={'payroll_millions':'Payroll ($M)','cost_per_win':'Payroll per win ($)'}),width='stretch')
    provenance=json.loads((ROOT/'data/provenance.json').read_text())
    st.caption('Snapshot build time (UTC): '+provenance['built_at_utc'])
    st.download_button('Download verified source dataset',(ROOT/'data/teams_2025.csv').read_bytes(),'teams_2025.csv','text/csv',key='source_download')

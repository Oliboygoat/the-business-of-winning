"""Season selection and longitudinal views; never pool franchise-years into a fit."""
import pandas as pd
import plotly.express as px
import streamlit as st
from analytics import ROOT,regression
from multi_analytics import annual_models,consistency
from charts import payroll_scatter
from ui import hero,section_header,card,plot,navigate
PALETTE=['#246bd1','#479281','#9b719c','#b78347','#6183a1','#a66572']
MEASURES={'Wins':'wins','Winning percentage':'win_pct','Opening Day payroll':'payroll','Payroll per win':'cost_per_win','Wins ahead of payroll benchmark':'wins_above_fit'}


def trend_frame(panel,ids,measure,real=False):
    """UI series retain calendar gaps; source panel itself remains complete."""
    field=MEASURES[measure]
    if real and field=='payroll':field='payroll_2026_dollars'
    if real and field=='cost_per_win':field='real_cost_per_win'
    result=panel[panel.franchise_id.isin(ids)].copy()
    result['value']=result[field]
    result['payroll_source_label']=result.payroll_basis.map({'AP_OPENING_DAY':'Associated Press','TBC_OPENING_DAY_ALTERNATE':'The Baseball Cube (different definition)'})
    money=measure in ['Opening Day payroll','Payroll per win']
    if money:result['value']/=1e6
    # Explicit empty chart slots stop Plotly joining across excluded 2022.
    chunks=[]
    for franchise_id,g in result.groupby('franchise_id'):
        rows=g.set_index('season').reindex(range(int(panel.season.min()),int(panel.season.max())+1))
        rows['franchise_id']=franchise_id;rows['franchise']=g.franchise.iloc[0]
        chunks.append(rows.reset_index())
    return pd.concat(chunks,ignore_index=True) if chunks else result


def trend_chart(panel,ids,measure,real=False):
    df=trend_frame(panel,ids,measure,real)
    money=measure in ['Opening Day payroll','Payroll per win']
    units=('March 2026 USD' if real else 'nominal USD')
    label=f'{measure} ($M, {units})' if money else measure
    fig=px.line(df,x='season',y='value',color='franchise',markers=True,color_discrete_sequence=PALETTE,
        custom_data=['team','payroll_source_label','wins','losses','payroll'],labels={'season':'Season','value':label,'franchise':'Franchise'},height=440)
    value_format='.1%' if measure=='Winning percentage' else ',.2f' if money or measure=='Wins ahead of payroll benchmark' else '.0f'
    fig.update_traces(connectgaps=False,line_width=2.2,marker_size=8,
        hovertemplate='<b>%{fullData.name}</b><br>%{customdata[0]} · %{x:.0f}<br>'+label+': %{y:'+value_format+'}<br>Record: %{customdata[2]}–%{customdata[3]}<br>Nominal Opening Day payroll: $%{customdata[4]:,.0f}<br>Payroll source: %{customdata[1]}<extra></extra>')
    fig.update_xaxes(dtick=1,tickformat='d')
    if measure=='Winning percentage':fig.update_yaxes(tickformat='.0%')
    if measure=='Wins ahead of payroll benchmark':fig.add_hline(y=0,line_dash='dot',line_color='#a8b1bd')
    return fig


def seasonal_overview(full,year):
    hero();fit=regression(full);best=full.sort_values('cost_per_win').iloc[0]
    a,b,c,d=st.columns(4)
    a.metric('Total MLB payroll',f'${full.payroll.sum()/1e9:.2f}B')
    b.metric('Average team wins',f'{full.wins.mean():.1f}')
    c.metric('Spending and wins: connection',f"{fit['r']:.3f}",help='From −1 to +1: positive values mean higher-payroll teams tended to win more. Zero means no straight-line connection. This does not establish cause.')
    d.metric('Lowest payroll per win',best.team,help=f'Opening Day payroll divided by wins: ${best.cost_per_win:,.2f}. This does not measure profit or total team spending.')
    with card('season_scatter'):
        title,control=st.columns([2.4,1])
        with title:st.subheader(f'{year} · Payroll and performance')
        with control:highlight=st.selectbox('Highlight a team',['No highlight']+full.team.tolist(),key='spotlight')
        plot(payroll_scatter(full,highlight),key='overview_scatter')
        st.caption('$M means millions of dollars. AL = American League; NL = National League. The dashed line is the payroll benchmark, not a forecast.')
        st.caption(f'{year} · 30 teams · Regular-season wins · Nominal payroll · Highlighting does not change the benchmark.')
    st.caption('Some final records contain 161 games. Wins are actual wins, and win percentage uses games played; no missing wins are filled in.')
    with card('season_highlight'):
        st.subheader(f"Payroll helps explain {fit['r_squared']:.1%} of the differences in wins")
        st.write('The rest lies outside this simple model. This connection does not show how many wins spending caused or whether a team made a profit.')
    st.button('Explore the insights →',on_click=navigate,args=('Insights',),key='insights_link',type='primary')


def seasonal_insights(full,year):
    section_header('What the numbers reveal',f'{year} · All 30 teams · Opening Day payroll and regular-season results')
    fit=regression(full)
    top=full.sort_values('wins_above_fit',ascending=False).iloc[0]
    bottom=full.sort_values('wins_above_fit').iloc[0]
    with card('annual_insights'):
        st.subheader(f"Payroll helps explain {fit['r_squared']:.2%} of the differences in wins")
        st.write(f"**Observation.** Higher-payroll teams tended to win {'more' if fit['r']>=0 else 'fewer'} games this season. The model leaves {(1-fit['r_squared']):.1%} of the differences in wins outside its explanation.")
        st.write('**Business significance.** Payroll gives teams a starting point for comparison, but cannot by itself tell them how to build a winning roster.')
        st.caption('This is a connection in the data, not proof that spending caused wins or that a club made a profit.')
    for direction,row in [('ahead of',top),('behind',bottom)]:
        with card('annual_'+direction.replace(' ', '_')):
            st.subheader(f'{row.team} — furthest {direction} the payroll benchmark')
            st.write(f"**Observation.** {int(row.wins)} wins against a benchmark of {row.fitted_wins:.2f}: {abs(row.wins_above_fit):.2f} wins {direction} the model. Opening Day payroll: \\${int(row.payroll):,}.")
            st.write('**Conclusion.** This is a case to investigate, not a verdict on management. The model does not identify why results differed or whether they will repeat.')
    from research_ui import model_details
    with st.expander('Does Colorado’s unusual season change the story?'):
        model_details(full,year,technical=False)
    with st.expander('View detailed statistics'):
        model_details(full,year)
    st.info('Hypothesis for future testing: some team practices may help explain results ahead of the benchmark. This dataset does not measure those practices or establish their effects.')


def annual_trend_chart(models,real=False):
    data=models.set_index('season').reindex(range(2021,2027)).reset_index()
    col='real_total_payroll' if real else 'total_payroll'
    data['total_billions']=data[col]/1e9
    fig=px.line(data,x='season',y='total_billions',markers=True,labels={'season':'Season','total_billions':'Total payroll ($B, March 2026 USD)' if real else 'Total payroll ($B, nominal USD)'},height=390)
    fig.update_traces(line_color='#246bd1',connectgaps=False,marker_size=8)
    fig.update_xaxes(dtick=1,tickformat='d')
    return fig


def multi_overview(panel):
    hero();models=annual_models(panel);board=consistency(panel)
    a,b,c,d=st.columns(4)
    a.metric('Seasons in comparison',panel.season.nunique())
    b.metric('MLB teams',panel.franchise_id.nunique())
    c.metric('Win differences linked to payroll',f'{models.iloc[-1].r_squared:.1%}',help=f'For {int(models.iloc[-1].season)}: the share of differences in team wins described by that season’s payroll model (R²). This does not establish cause.')
    d.metric('Most consistently ahead of the benchmark',board.iloc[0].franchise,help='Highest average of actual wins minus each season’s payroll-model benchmark. This is a historical comparison, not proof of better management.')
    with card('multiyear_overview'):
        st.subheader('How team payrolls have changed')
        dollars=st.radio('Payroll display',['Nominal USD','March 2026 USD'],horizontal=True,key='overview_dollars',
            help='Nominal USD means dollars that season. March 2026 USD adjusts for changes in general purchasing power using March consumer prices. It does not measure baseball salary inflation.')
        plot(annual_trend_chart(models,dollars=='March 2026 USD'),key='annual_payroll_trend')
        st.caption('$B means billions of dollars. Nominal means dollars that season.')
        st.caption('Gaps mark seasons left out because their payroll source differs. Inflation-adjusted dollars compare general purchasing power, not baseball salary inflation.')
    section_header('Payroll tells a different story each season','Each point shows how much of that season’s differences in team wins the payroll model describes. Higher does not mean spending caused more wins.')
    rs=models.set_index('season').reindex(range(2021,2027)).reset_index()
    fig=px.line(rs,x='season',y='r_squared',markers=True,labels={'season':'Season','r_squared':'Win differences linked to payroll'},height=310)
    fig.update_traces(connectgaps=False,line_color='#479281',marker_size=8)
    fig.update_yaxes(tickformat='.0%');fig.update_xaxes(dtick=1,tickformat='d')
    plot(fig,key='annual_r2_trend')
    st.button('Explore the insights →',on_click=navigate,args=('Insights',),key='insights_link',type='primary')


def multi_explore(panel):
    section_header('Teams over time','Compare team spending and results across seasons. The payroll benchmark is a comparison point, not a forecast.')
    names=panel[['franchise_id','franchise']].drop_duplicates().set_index('franchise_id').franchise.to_dict()
    with card('trend_controls'):
        selected=st.multiselect('Choose 2–6 teams',sorted(names,key=names.get),default=[158,121,146],format_func=names.get,max_selections=6,key='multi_franchises')
        left,right=st.columns(2)
        with left:measure=st.selectbox('Performance measure',list(MEASURES),key='trend_measure')
        with right:dollars=st.selectbox('Dollar display',['Nominal USD','March 2026 USD'],key='trend_dollars',help='Nominal USD means dollars that season. March 2026 USD adjusts for changes in general purchasing power, using March consumer prices.')
    if len(selected)<2:
        st.info('Choose at least two teams to compare trends.')
    else:
        plot(trend_chart(panel,selected,measure,dollars=='March 2026 USD'),key='franchise_trend')
        st.caption('$M means millions of dollars. The benchmark is the win total our model predicts from payroll within that season, not a forecast.')
        st.caption('The dollar display changes payroll and payroll per win only. Wins and wins ahead of the benchmark stay the same.')
        st.caption('A team stays together through name or location changes. Hover to see its name that season. Gaps are omitted seasons, not estimates.')
        records=panel[panel.franchise_id.isin(selected)].sort_values(['franchise','season'])
        with st.expander('Explore the underlying data'):
            st.dataframe(records[['season','franchise','team','payroll','payroll_2026_dollars','wins','losses','win_pct','cost_per_win','wins_above_fit','payroll_basis']],hide_index=True,width='stretch',column_config={
                'payroll':st.column_config.NumberColumn('Nominal payroll ($)',format='$%,d'),
                'payroll_2026_dollars':st.column_config.NumberColumn('March 2026 payroll ($)',format='$%,.0f'),
                'cost_per_win':st.column_config.NumberColumn('Nominal cost / win ($)',format='$%,.0f'),
                'win_pct':st.column_config.NumberColumn('Win pct.',format='%.3f'),
                'season':'Season','franchise':'Team','team':'Name that season','wins':'Wins','losses':'Losses','payroll_basis':'Payroll source definition',
                'wins_above_fit':st.column_config.NumberColumn('Wins ahead of benchmark',format='%.2f')})
            st.download_button('Download franchise comparison',records.to_csv(index=False).encode(),'franchise_trends.csv','text/csv',key='franchise_download')
    section_header('Who keeps finishing ahead of the benchmark?','Teams ranked by average wins ahead of their own season’s payroll benchmark. This is a historical pattern, not a forecast.')
    league=st.selectbox('League',['All MLB','AL','NL'],key='consistency_league',help='AL = American League. NL = National League.')
    board=consistency(panel)
    if league!='All MLB':board=board[board.franchise_id.isin(panel.loc[panel.league==league,'franchise_id'])]
    fig=px.bar(board.iloc[::-1],x='mean_residual',y='franchise',color='mean_residual',color_continuous_scale=['#ba765c','#dbe1e7','#479281'],
        color_continuous_midpoint=0,labels={'mean_residual':'Average wins ahead of / behind benchmark','franchise':''},height=max(420,len(board)*25))
    fig.update_layout(showlegend=False,coloraxis_showscale=False)
    fig.add_vline(x=0,line_color='#a8b1bd');plot(fig,key='consistency_chart')
    st.caption('Positive numbers mean more wins than the payroll benchmark; negative numbers mean fewer. Each selected season counts equally.')
    with st.expander('View leaderboard details'):
        st.dataframe(board[['franchise','seasons','mean_residual','seasons_above_fit','average_wins','aggregate_cost_per_win']],hide_index=True,width='stretch',column_config={
            'franchise':'Team','seasons':'Seasons compared','average_wins':st.column_config.NumberColumn('Average wins',format='%.1f'),
            'mean_residual':st.column_config.NumberColumn('Average wins ahead',format='%.2f'),
            'seasons_above_fit':st.column_config.NumberColumn('Seasons ahead of benchmark'),
            'aggregate_cost_per_win':st.column_config.NumberColumn('Aggregate cost / win ($)',format='$%,.0f')})
        st.caption('Each season counts equally. Positive numbers mean more wins than the benchmark; negative numbers mean fewer. A repeated pattern does not prove management skill or predict future results.')


def multi_insights(panel):
    section_header('What the numbers reveal','Repeated results worth a closer look. Historical patterns, not predictions.')
    models=annual_models(panel);board=consistency(panel)
    for direction,row in [('ahead of',board.iloc[0]),('behind',board.iloc[-1])]:
        with card('multi_'+('best' if direction=='ahead of' else 'worst')):
            count=int(row.seasons_above_fit) if direction=='ahead of' else int((panel[panel.franchise_id==row.franchise_id].wins_above_fit<0).sum())
            label=f'consistently {direction} the benchmark' if count==int(row.seasons) and int(row.seasons)>1 else f'{direction} the benchmark on average'
            st.subheader(f'{row.franchise} — {label}')
            st.write(f"**Observation.** {row.franchise} averaged **{abs(row.mean_residual):.2f} {'more' if direction=='ahead of' else 'fewer'} wins per season** than its payroll-based benchmark. It finished {direction} that benchmark in **{count} of {int(row.seasons)} selected seasons**.")
            st.write('**Business significance.** A repeated gap can help identify a team for deeper study of how spending and results compare.')
            st.caption('This comparison does not prove good or bad management, explain the cause, or predict future performance. Each season counts equally.')
    weakest=models.loc[models.r_squared.idxmin()];strongest=models.loc[models.r_squared.idxmax()]
    with card('multi_relationship'):
        st.subheader('Payroll’s connection with winning changes from year to year')
        st.write(f"**Observation.** The share of differences in team wins described by payroll ranges from **{weakest.r_squared:.2%} in {int(weakest.season)}** to **{strongest.r_squared:.2%} in {int(strongest.season)}** in the selected seasons.")
        st.write('**Conclusion.** Payroll is an incomplete guide to winning, and the strength of the connection varies. These percentages do not measure how many wins spending caused.')
    with st.expander('View detailed statistics'):
        st.dataframe(models[['season','payroll_basis','n','slope','intercept','r','r_squared','total_payroll','average_wins']],hide_index=True,width='stretch')
        st.caption('R² describes within-season variation. Slopes use payroll in millions of nominal US dollars. Full equations and diagnostics are in Methodology.')
    st.info('Hypothesis for future testing: team practices may help explain repeated results ahead of the benchmark. These data do not measure those practices, so they cannot establish that explanation.')
    st.warning('The same teams appear in multiple seasons and play one another. These are connected observations, not independent repeats of an experiment. No causal spending return, profit estimate, or forecast is established.')
    st.caption('Select a single season for its Colorado check, or open Methodology for every year’s model and sensitivity results.')


def multi_methodology(panel):
    from research_ui import render_methodology
    render_methodology(panel)

"""Plot builders use the existing calculated columns; they never change models."""
import plotly.express as px
import plotly.graph_objects as go
from analytics import regression
COLORS = {'AL':'#3979bc','NL':'#77a69a'}


def payroll_scatter(full, highlighted=None):
    fig = px.scatter(full,x='payroll_millions',y='wins',color='league',symbol='league',
        color_discrete_map=COLORS,symbol_map={'AL':'circle','NL':'diamond'},hover_name='team',
        custom_data=['team','league','payroll','wins','losses','cost_per_win'],
        labels={'payroll_millions':'Opening Day payroll ($M)','wins':'Regular-season wins'})
    fig.update_traces(marker=dict(size=13,opacity=.9,line=dict(width=1.5,color='white')),
        hovertemplate='<b>%{customdata[0]}</b><br>%{customdata[1]} · %{customdata[3]}–%{customdata[4]}<br>Opening Day payroll: $%{customdata[2]:,.0f}<br>Cost per win: $%{customdata[5]:,.0f}<extra></extra>')
    fit=regression(full)
    xs=[full.payroll_millions.min(),full.payroll_millions.max()]
    fig.add_trace(go.Scatter(x=xs,y=[fit['intercept']+fit['slope']*x for x in xs],mode='lines',
        name='Payroll-based benchmark',line=dict(color='#8793a3',width=1.5,dash='dash'),hoverinfo='skip'))
    fig.add_hline(y=81,line_dash='dot',line_color='#c1c7d0',annotation_text='81 wins · half of 162 games',
        annotation_font=dict(color='#7c8592',size=11),annotation_position='bottom right')
    if highlighted and highlighted != 'No highlight':
        team=full[full.team == highlighted]
        fig.add_trace(go.Scatter(x=team.payroll_millions,y=team.wins,mode='markers+text',
            text=team.team,textposition='top center',textfont=dict(color='#1e5fae',size=12),
            marker=dict(size=23,color='rgba(0,0,0,0)',line=dict(color='#246bd1',width=2)),
            name='Highlighted team',showlegend=False,hoverinfo='skip'))
    fig.update_layout(height=490)
    fig.update_xaxes(tickprefix='$',ticksuffix='M',rangemode='tozero')
    return fig


def residual_bars(view):
    residual=view.sort_values('wins_above_fit')
    fig=px.bar(residual,x='wins_above_fit',y='team',color='league',orientation='h',
        color_discrete_map=COLORS,height=max(400,len(view)*26),
        category_orders={'team':residual.team.iloc[::-1].tolist()},
        labels={'wins_above_fit':'Wins ahead of / behind payroll benchmark','team':''})
    fig.add_vline(x=0,line_color='#a9b1bf',line_width=1)
    return fig


def ranking_bars(ranked, field):
    top=ranked.head(15).iloc[::-1].copy()
    top['cost_per_win_millions']=top.cost_per_win/1e6
    x='cost_per_win_millions' if field=='cost_per_win' else field
    return px.bar(top,x=x,y='team',color='league',orientation='h',color_discrete_map=COLORS,
        height=max(330,len(top)*28),category_orders={'team':top.team.iloc[::-1].tolist()},
        labels={x:'Payroll per win ($M)' if field=='cost_per_win' else 'Wins ahead of payroll benchmark','team':''})

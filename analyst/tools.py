"""A small, validated query API. No code execution, files, network, or writes."""
from dataclasses import dataclass, asdict
import json
from analytics import regression
from multi_analytics import YEARS, consistency

ACTIONS=('ranking','compare','trend','models','colorado','consistency','sources')
METRICS=('payroll_per_win','wins_ahead','payroll','wins')
LIMITATION='Opening Day payroll is not total team spending. These comparisons do not establish causes, management quality, profit, or future results.'
AP='Associated Press Opening Day payroll'
TBC='The Baseball Cube Opening Day payroll (different accounting definition)'


class QueryError(ValueError):
    pass


@dataclass(frozen=True)
class Query:
    action: str
    seasons: tuple
    team_ids: tuple=()
    metric: str='payroll_per_win'
    limit: int=5
    real_dollars: bool=False

    def payload(self):
        result=asdict(self)
        result['seasons']=list(self.seasons);result['team_ids']=list(self.team_ids)
        return result


def validate_query(raw, panel, allow_mixed=False):
    if not isinstance(raw,dict) or set(raw)!={'action','seasons','team_ids','metric','limit','real_dollars'}:
        raise QueryError('Use only the documented analysis fields.')
    if raw['action'] not in ACTIONS or raw['metric'] not in METRICS:raise QueryError('That analysis or measure is not supported.')
    years=raw['seasons'];ids=raw['team_ids']
    if not isinstance(years,list) or not 1<=len(years)<=6 or any(type(y)!=int or y not in YEARS for y in years) or len(set(years))!=len(years):
        raise QueryError('Choose unique seasons from 2021–2026.')
    if not isinstance(ids,list) or len(ids)>6 or any(type(i)!=int or i not in set(panel.team_id) for i in ids) or len(ids)!=len(set(ids)):
        raise QueryError('Choose up to six valid MLB franchise IDs.')
    if type(raw['limit'])!=int or not 1<=raw['limit']<=10 or type(raw['real_dollars'])!=bool:raise QueryError('Invalid result limit or dollar setting.')
    if len(years)>1 and 2022 in years and not allow_mixed:
        raise QueryError('2022 uses The Baseball Cube, not AP. Turn on the separate mixed-source permission to compare it with AP seasons, or choose comparable AP years.')
    if raw['action'] in ('ranking','compare','colorado') and len(years)!=1:raise QueryError('This analysis needs one season. Use trends or consistency for multiple years.')
    if raw['action']=='compare' and len(ids)<2:raise QueryError('Choose two to six teams to compare.')
    if raw['action']=='trend' and not ids:raise QueryError('Name at least one team for a trend.')
    if raw['real_dollars'] and raw['action'] not in ('ranking','compare','trend'):
        raise QueryError('Inflation-adjusted dollars are available for payroll rankings, team comparisons, and trends. Annual model estimates and consistency retain their documented nominal-dollar definitions.')
    return Query(raw['action'],tuple(sorted(years)),tuple(ids),raw['metric'],raw['limit'],raw['real_dollars'])


def _records(frame,columns):
    # Pandas converts numpy scalars to JSON-native values; NaN is forbidden below.
    return json.loads(frame[columns].to_json(orient='records',double_precision=12))


def execute_query(raw,panel,allow_mixed=False):
    q=validate_query(raw,panel,allow_mixed)
    data=panel[panel.season.isin(q.seasons)].copy()
    sources=[]
    for year,g in data.groupby('season'):
        row=g.iloc[0]
        sources.append({'season':int(year),'definition':TBC if year==2022 else AP,
            'payroll_url':row.payroll_source_url,'standings_url':row.standings_source_url})
    context='Seasons: '+', '.join(map(str,q.seasons))+'. '
    if 2022 in q.seasons:
        context+='2022 uses The Baseball Cube; its accounting is not reconciled to AP. '
        if len(q.seasons)>1:context+='Mixed-source comparison explicitly permitted; differences can reflect accounting. '
    else:context+='AP payroll years only; AP roster coverage still varies by year. '
    dollars='March 2026 purchasing-power dollars' if q.real_dollars else 'dollars that season'
    monetary='payroll_2026_dollars' if q.real_dollars else 'payroll'
    cost='real_cost_per_win' if q.real_dollars else 'cost_per_win'
    lines=[];title='';rows=[]
    if q.action in ('ranking','compare','trend'):
        chosen=data if not q.team_ids else data[data.franchise_id.isin(q.team_ids)]
        if q.action=='ranking':
            field={'payroll_per_win':cost,'wins_ahead':'wins_above_fit','payroll':monetary,'wins':'wins'}[q.metric]
            chosen=chosen.sort_values([field,'franchise'],ascending=[q.metric=='payroll_per_win',True]).head(q.limit)
            title={'payroll_per_win':'Who spent the least payroll per win?','wins_ahead':'Who finished furthest ahead of the payroll benchmark?','payroll':'Who had the biggest Opening Day payroll?','wins':'Who won the most games?'}[q.metric]
        elif q.action=='compare':title='Spending and results, side by side'
        else:title='How spending and results changed over time'
        chosen=chosen.sort_values(['franchise','season']) if q.action!='ranking' else chosen
        rows=_records(chosen,['season','franchise_id','franchise','team','payroll','payroll_2026_dollars','wins','losses','win_pct','fitted_wins','wins_above_fit','cost_per_win','real_cost_per_win'])
        for r in chosen.itertuples():
            money=getattr(r,monetary);per_win=getattr(r,cost)
            direction='ahead of' if r.wins_above_fit>=0 else 'behind'
            lines.append(f'{r.team} ({r.season}): {r.wins}–{r.losses}, ${money:,.0f} payroll, ${per_win:,.2f} per win; {abs(r.wins_above_fit):.2f} wins {direction} the season’s payroll benchmark.')
        if q.action=='compare':
            # First two explicitly selected teams; render a precise comparison, not LLM arithmetic.
            a=chosen[chosen.franchise_id==q.team_ids[0]].iloc[0];b=chosen[chosen.franchise_id==q.team_ids[1]].iloc[0]
            win_gap=int(a.wins-b.wins);payroll_gap=a[monetary]-b[monetary]
            win_words=f'{abs(win_gap)} '+('more wins' if win_gap>0 else 'fewer wins') if win_gap else 'the same number of wins'
            pay_words=f'${abs(payroll_gap):,.0f} '+('more' if payroll_gap>0 else 'less')+' Opening Day payroll' if payroll_gap else 'the same Opening Day payroll'
            lines.insert(0,f'{a.franchise} recorded {win_words} than {b.franchise}, with {pay_words}.')
        if q.action=='trend':
            for _,g in chosen.groupby('franchise_id'):
                if len(g)>1:
                    a,b=g.iloc[0],g.iloc[-1]
                    lines.append(f'{a.franchise}, {int(a.season)} to {int(b.season)}: {int(b.wins-a.wins):+d} wins; {(b[monetary]/a[monetary]-1):+.2%} payroll in {dollars}. Endpoints alone do not describe every intervening season.')
        explanation='Payroll per win divides payroll by all regular-season wins. A low number can come with a losing record. The benchmark compares actual wins with a model fitted to all thirty teams in that season; it is not a forecast.'
    elif q.action=='consistency':
        board=consistency(data)
        if q.team_ids:board=board[board.franchise_id.isin(q.team_ids)]
        board=board.head(q.limit)
        title='Who repeatedly finished ahead of the benchmark?'
        rows=_records(board,['franchise_id','franchise','seasons','mean_residual','min_residual','max_residual','seasons_above_fit','aggregate_cost_per_win'])
        for r in board.itertuples():
            lines.append(f'{r.franchise}: {r.mean_residual:+.2f} wins per season against the payroll benchmark, ahead in {r.seasons_above_fit} of {r.seasons} selected seasons. Annual range: {r.min_residual:+.2f} to {r.max_residual:+.2f} wins.')
        explanation='Each selected season counts equally. The same franchises recur and play each other, so this is a historical summary, not independent evidence of management skill or future success.'
    elif q.action in ('models','colorado'):
        title='How much does payroll help explain winning?' if q.action=='models' else 'Does Colorado change the payroll–wins picture?'
        for year,g in data.groupby('season'):
            fit={k:float(v) if k!='n' else int(v) for k,v in regression(g).items()}
            result={'season':int(year),**fit}
            lines.append(f'{year}: payroll describes {fit["r_squared"]:.2%} of the differences in team wins (R²). Spending–wins correlation: {fit["r"]:.4f}; the fitted association is {fit["slope"]*10:.3f} wins per $10 million, not wins purchased.')
            if q.action=='colorado':
                without={k:float(v) if k!='n' else int(v) for k,v in regression(g[g.team_id!=115]).items()}
                result['without_colorado']=without
                result['slope_change_pct']=100*(without['slope']/fit['slope']-1)
                lines.append(f'Leaving Colorado out changes R² to {without["r_squared"]:.2%} and the slope to {without["slope"]*10:.3f} wins per $10 million ({result["slope_change_pct"]:+.2f}%). Colorado stays in the primary thirty-team analysis.')
            rows.append(result)
        explanation='Each season gets its own straight-line model. R² describes within-season differences, not the percentage of wins caused by spending. These estimates do not control for roster quality, injuries, schedule, or luck.'
    else:
        title='Where the numbers come from';rows=sources
        lines=['Opening Day payroll is a roster snapshot, not full-season or total operating cost. Wins and losses come from the official MLB standings snapshots. Published values are retained; missing AP amounts are not invented.']
        explanation='The Methodology section contains direct source links, complete payroll definitions, source fingerprints, formulas, and the March CPI adjustment. The publishers’ accounting has not been independently audited against contracts.'
    result={'query':q.payload(),'title':title,'lines':lines,'explanation':explanation,'context':context,'dollar_basis':dollars,'sources':sources,'inflation_source_url':('https://api.bls.gov/publicAPI/v2/timeseries/data/CUUR0000SA0?startyear=2021&endyear=2026' if q.real_dollars else None),'rows':rows,'limitation':LIMITATION}
    # Defense against nonfinite values and accidental non-JSON return types.
    json.dumps(result,allow_nan=False)
    return result


def tool_schema():
    return {'type':'function','name':'analyze_mlb','description':'Read verified MLB payroll/results. Each season model uses all 30 teams. No forecasts, players, profits, causes, or external facts. 2022 alone is allowed; mixing it needs server-side user permission.',
        'strict':True,'parameters':{'type':'object','additionalProperties':False,'properties':{
            'action':{'type':'string','enum':list(ACTIONS)},
            'seasons':{'type':'array','items':{'type':'integer','enum':list(YEARS)},'minItems':1,'maxItems':6},
            'team_ids':{'type':'array','items':{'type':'integer'},'maxItems':6},
            'metric':{'type':'string','enum':list(METRICS)},
            'limit':{'type':'integer','minimum':1,'maximum':10},'real_dollars':{'type':'boolean'}},
            'required':['action','seasons','team_ids','metric','limit','real_dollars']}}

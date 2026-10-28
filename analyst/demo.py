"""Finite, transparent question routing. This is not a language model."""
import re
from analyst.tools import Query, QueryError, execute_query
from multi_analytics import YEARS

EXAMPLES=[
 'Who had the lowest payroll per win in 2025?',
 'Compare the Brewers and Mets in 2025.',
 'Show Brewers payroll and wins over time.',
 'Which teams consistently beat the payroll benchmark across comparable seasons?',
 'How strong was the payroll–wins relationship in 2025?',
 'Does excluding Colorado change the 2025 model?',
]


def team_aliases(panel):
    aliases={}
    for r in panel[['team','franchise_id']].drop_duplicates().itertuples():
        aliases[r.team.lower()]=int(r.franchise_id)
        nickname=r.team.split()[-1].lower()
        if nickname not in ('sox',):aliases[nickname]=int(r.franchise_id)
    aliases.update({'white sox':145,'red sox':111,'a’s':133,"a's":133,'cleveland':114,'oakland':133,'colorado':115,'milwaukee':158,'tampa bay':139})
    return aliases


def parse_question(question,panel,default_years=(2025,),allow_mixed=False):
    if not isinstance(question,str) or not question.strip() or len(question)>1200:raise QueryError('Ask a question of up to 1,200 characters.')
    text=question.lower().strip()
    if re.search(r'\b(profit|profitable|revenue|roi|bet|betting|odds|predict|forecast|salary cap|player|postseason|world series|caus\w*|why|management|injur\w*|202[0789]|20[013]\d)\b',text):
        raise QueryError('The demo cannot answer causes, predictions, player questions, or financial returns. It supports verified team payrolls, regular-season results, comparisons, trends, and model summaries for 2021–2026.')
    mentioned_years=list(map(int,re.findall(r'\b(?:19|20)\d{2}\b',text)))
    if any(y not in YEARS for y in mentioned_years):raise QueryError('The verified dataset covers 2021–2026 only.')
    years=sorted(set(map(int,re.findall(r'\b202[1-6]\b',text))))
    if len(years)==2 and re.search(r'\b(from|through|between|to|since)\b|[–-]',text):years=list(range(years[0],years[-1]+1))
    ids=[];matches=[]
    for name,team_id in team_aliases(panel).items():
        found=re.search(r'(?<!\w)'+re.escape(name)+r'(?!\w)',text)
        if found:matches.append((found.start(),-len(name),team_id))
    for _,__,team_id in sorted(matches):
        if team_id not in ids:ids.append(team_id)
    if any(k in text for k in ['consisten','across comparable','multi-year']):action='consistency'
    elif any(k in text for k in ['excluding colorado','without colorado','does excluding','outlier','sensitivity']):action='colorado'
    elif any(k in text for k in ['relationship','correlation','regression','r-squared','r²','model strength']):action='models'
    elif any(k in text for k in ['compare','versus',' vs ','side by side']):action='compare'
    elif any(k in text for k in ['over time','trend','change from','changed','payroll and wins change']):action='trend'
    elif any(k in text for k in ['source','where the numbers','definition']):action='sources'
    elif any(k in text for k in ['lowest payroll per win','most efficient','payroll efficiency','most wins','biggest payroll','highest payroll','ahead of','beat the payroll']):action='ranking'
    else:raise QueryError('That wording is outside this limited demo. Try an example question, or ask to compare named teams in a specific season.')
    if not years:
        years=list(YEARS) if action in ('consistency','trend') else list(default_years)
    # Broad default comparable-year requests omit 2022; explicit ranges mentioning it require opt-in.
    explicit=bool(re.search(r'\b202[1-6]\b',text))
    if not explicit and not allow_mixed and len(years)>1:years=[y for y in years if y!=2022]
    # A named endpoint range still explicitly requests all six years; never silently remove 2022.
    metric='wins_ahead' if any(k in text for k in ['ahead','beat the payroll']) else 'wins' if 'most wins' in text else 'payroll' if any(k in text for k in ['biggest payroll','highest payroll']) else 'payroll_per_win'
    return Query(action,tuple(years),tuple(ids),metric,5,'inflation' in text or 'real dollars' in text).payload()


def answer_demo(question,panel,default_years=(2025,),allow_mixed=False):
    try:
        result=execute_query(parse_question(question,panel,default_years,allow_mixed),panel,allow_mixed)
        return {'ok':True,'results':[result],'message':'Free demo · calculated locally from the verified dataset.'}
    except QueryError as exc:
        return {'ok':False,'results':[],'message':str(exc)}

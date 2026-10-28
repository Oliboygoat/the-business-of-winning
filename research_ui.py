"""Progressive disclosure for research details, using the existing analytical layer."""
import json
import pandas as pd
import streamlit as st
from analytics import ROOT, regression
from multi_analytics import load_panel, annual_models, consistency
from ui import section_header


def diagnostic_table(panel):
    """Refit each intact season with/without Colorado; no pooled model."""
    rows=[]
    for year,frame in panel.groupby('season'):
        primary=regression(frame)
        without=regression(frame[frame.team_id!=115])
        row=frame[frame.team_id==115].iloc[0]
        rows.append({'season':int(year),'colorado_wins':int(row.wins),'colorado_losses':int(row.losses),
            'colorado_payroll':int(row.payroll),'colorado_residual':row.wins_above_fit,
            'n_primary':primary['n'],'n_without_colorado':without['n'],
            'slope_primary':primary['slope'],'slope_without_colorado':without['slope'],
            'r_squared_primary':primary['r_squared'],'r_squared_without_colorado':without['r_squared'],
            'slope_change_pct':100*(without['slope']/primary['slope']-1)})
    return pd.DataFrame(rows)


def model_details(frame,year,technical=True):
    fit=regression(frame);check=diagnostic_table(frame).iloc[0]
    st.write(f"Colorado won {int(check.colorado_wins)} games and lost {int(check.colorado_losses)}. Leaving it out changes the share of win differences described by payroll from {fit['r_squared']:.2%} to {check.r_squared_without_colorado:.2%}. Colorado stays in the main analysis with all 30 teams.")
    st.caption('One unusual result can change a small study’s estimates. Removing it is a check on the model, not a correction to the source data.')
    if technical:
        st.markdown(f"**{year} OLS equation:** fitted wins = {fit['intercept']:.6f} + {fit['slope']:.8f} × payroll (nominal \\$M).")
        st.write(f"Pearson r = {fit['r']:.6f}; R² = {fit['r_squared']:.6f}; n = {fit['n']}; two-sided slope p-value = {fit['p_value']:.6f}.")
        st.caption('The p-value tests a zero linear slope under model assumptions, not causation. Interdependent games, a sample of only 30 teams, unequal error variance and omitted variables limit inference.')


def render_methodology(selected):
    section_header('Methodology','Sources, formulas, and checks you can inspect and reproduce.')
    st.write('The main views use plain-English payroll benchmarks. Here are the statistical definitions, complete annual models, source records, and limits behind them.')
    st.warning('2022 uses The Baseball Cube rather than AP and is excluded from default comparable-year results. Even AP’s roster coverage varies across years. Neither source has been audited against confidential contracts. Payroll per win is not profitability, and model association is not causation.')
    all_years=load_panel()
    with st.expander('Data sources, payroll definitions, and cleaning',expanded=False):
        # Retain original source documentation and direct citations; publisher captures are private.
        st.markdown((ROOT/'MULTISEASON_SOURCES.md').read_text())
        with st.expander('Original 2025 source documentation'):
            st.markdown((ROOT/'DATA_SOURCES.md').read_text())
    with st.expander('Formulas and statistical assumptions'):
        st.markdown(r'''
**Units and performance measures**

- $P$ = nominal Opening Day payroll in US dollars; $x=P/1{,}000{,}000$; $y$ = actual regular-season wins.
- Games played = wins + losses. Winning percentage = wins / games played. Actual 161-game records are retained.
- Payroll per win = $P/y$. Wins per million dollars = $y/x$. No replacement-level baseline is subtracted.
- Run differential = runs scored − runs allowed. MLB payroll-per-win rank uses all 30 teams, lower first; ties share the minimum rank.

**Separate annual ordinary least squares (OLS) models, each with an intercept**

$\hat y_i = a + b x_i$, where $b=\sum_i(x_i-\bar x)(y_i-\bar y)/\sum_i(x_i-\bar x)^2$ and $a=\bar y-b\bar x$.

Pearson correlation: $r=\sum_i(x_i-\bar x)(y_i-\bar y)/\sqrt{\sum_i(x_i-\bar x)^2\sum_i(y_i-\bar y)^2}$.

Residual: $e_i=y_i-\hat y_i$. This is **wins ahead of / behind the payroll benchmark** in the main interface. Fitted wins are within-sample comparisons, not guaranteed real-world outcomes or validated forecasts.

$R^2=1-\sum_i e_i^2/\sum_i(y_i-\bar y)^2=r^2$ for these one-predictor OLS models with an intercept. It is the share of observed within-season variation in team wins described by the fitted line; it is not a causal share of wins and does not measure forecast accuracy.

**Multi-year consistency**

For a selected balanced cohort of $T$ seasons, mean residual for franchise $j$ is $\bar e_j=\sum_{t=1}^T e_{jt}/T$. Every selected season has equal weight. Seasons ahead counts $e_{jt}>0$; seasons behind counts $e_{jt}<0$; zero is neither. Rank by mean residual, descending; ties sort by franchise name. Total residual is the sum; the range is the minimum and maximum annual residual. Aggregate payroll per win = total payroll / total wins, not the average of seasonal ratios. Filters do not refit an annual model or change its all-MLB ranks.

**Inflation adjustment**

Real payroll = nominal payroll × March 2026 CPI / that season’s March CPI. CPI-U series CUUR0000SA0 is US city average, all items, not seasonally adjusted. “March 2026 USD” means general purchasing power, not baseball salary inflation or annual-average 2026 prices. A common rescaling within a season leaves its residuals, correlation, R², and ranks unchanged; the numerical slope changes with dollar units.

**Assumptions and limitations**

OLS describes a straight-line association. Annual models have only 30 observations, so influential teams can affect estimates. Conventional slope p-values additionally rely on independent, similarly variable errors and model/distribution assumptions. Teams play one another; errors need not be independent. Repeated franchise observations across seasons also share unmeasured characteristics. No stacked/pooled regression, multi-year significance test, management-skill estimate, causal effect, or validated prediction is claimed. The model does not control for roster quality, schedule, injuries, development, or luck. Opening Day payroll is a roster snapshot rather than full-season cost or total financial investment. Revenue, operating costs, and profit are absent.
''')
    models=annual_models(all_years)
    with st.expander('Annual regression equations and complete estimates'):
        st.caption('All six seasons shown separately; 2022 is an alternate payroll definition. Slopes are wins per $1M of nominal payroll. Tables retain machine-readable field names for reproducibility.')
        for row in models.itertuples():
            st.markdown(f"**{row.season} · {row.payroll_basis}:** fitted wins = {row.intercept:.6f} + {row.slope:.8f} × payroll (\\$M).")
        st.dataframe(models,hide_index=True,width='stretch')
        st.download_button('Download annual model estimates',models.to_csv(index=False).encode(),'annual_model_estimates.csv','text/csv',key='model_estimates_download')
        weakest=models.loc[models.r_squared.idxmin()];strongest=models.loc[models.r_squared.idxmax()]
        st.write(f"Across all source definitions shown, R² ranges from {weakest.r_squared:.4f} ({int(weakest.season)}) to {strongest.r_squared:.4f} ({int(strongest.season)}). Compare 2022 separately because its accounting basis differs. Changing model strength is descriptive, not evidence of a causal change in spending returns.")
    checks=diagnostic_table(all_years)
    with st.expander('Colorado Rockies: influential-observation sensitivity checks'):
        st.write('Every primary model retains Colorado. Each sensitivity model removes only Colorado, refits OLS with an intercept, and uses n = 29. Changes in slope and R² show influence on these estimates; better fit after exclusion does not justify deleting a valid record. This is a targeted exclusion check, not a complete influence or model-validation study.')
        st.dataframe(checks,hide_index=True,width='stretch')
        audited=json.loads((ROOT/'audit/results.json').read_text())
        st.write(f"2025 audited influence measures: Colorado’s leverage = {audited['colorado']['leverage']:.6f}; internally studentized residual = {audited['colorado']['internally_studentized_residual']:.6f}; Cook’s distance = {audited['colorado']['cooks_distance']:.6f}, compared with the screening rule 4/n = {audited['cooks_screening_threshold']:.6f}. Cook’s distance measures how much an observation shifts the fitted coefficients; exceeding a screening rule flags a case to examine, not invalid data.")

        st.download_button('Download Colorado sensitivity checks',checks.to_csv(index=False).encode(),'colorado_sensitivity.csv','text/csv',key='diagnostics_download')
    with st.expander('Selected seasons: team predictions, residuals, and consistency'):
        st.caption('Selected seasons: '+', '.join(map(str,sorted(selected.season.unique())))+'. These summaries are descriptive; repeated franchise rows are not independent samples.')
        details=selected[['season','team','payroll_basis','payroll','wins','losses','games','win_pct','fitted_wins','wins_above_fit','cost_per_win','efficiency_rank','march_cpi','payroll_2026_dollars']]
        st.dataframe(details,hide_index=True,width='stretch')
        st.dataframe(consistency(selected),hide_index=True,width='stretch')
        st.download_button('Download selected-season analytics',selected.to_csv(index=False).encode(),'selected_season_analytics.csv','text/csv',key='panel_analytics_download')
    with st.expander('Reproduce the analysis and inspect data provenance'):
        st.markdown('The application runs from bundled numerical records without a live data request. Source captures are not distributed. Manifests retain exact URLs and historical archive SHA-256 fingerprints. The public checks verify the exported records and reproduce the mathematics; independently re-extracting the publishers’ figures requires separately obtained source access. Neither check audits confidential accounting.')
        st.code('python scripts/verify_public_data.py\npython -m pytest -q',language='bash')
        st.caption('Historical archive filenames identify private evidence, not downloadable public files. Source URLs remain available; inspect PUBLICATION_RIGHTS.md before redistributing data.')
        manifest=json.loads((ROOT/'data/multiseason/provenance.json').read_text())
        st.caption('Source archive build (UTC): '+manifest['built_at_utc'])
        st.dataframe(pd.DataFrame(manifest['sources']),hide_index=True,width='stretch')
        st.json(manifest,expanded=False)
        st.download_button('Download provenance manifest',json.dumps(manifest,indent=2),'multiseason_provenance.json','application/json',key='provenance_download')
        st.download_button('Download all 180 verified source records',(ROOT/'data/multiseason/teams_2021_2026.csv').read_bytes(),'mlb_2021_2026_sources.csv','text/csv',key='panel_download')
        st.download_button('Download March CPI observations',(ROOT/'data/multiseason/cpi_march.csv').read_bytes(),'cpi_march.csv','text/csv',key='cpi_download')

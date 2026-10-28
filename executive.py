"""Accessible 2025 stories; every number comes from the verified summary."""
import streamlit as st
from analytics import executive_summary
from ui import card


def render_executive_summary(full):
    summary = executive_summary(full)
    primary, sensitivity = summary['primary'], summary['without_colorado']
    teams = summary['teams']
    st.caption('2025 · All 30 teams · Explore Teams filters do not change these findings')
    with card('summary_regression'):
        st.subheader('Bigger payrolls tended to come with more wins. There is much more to the story.')
        st.markdown(f"**Observation.** The payroll model accounts for **{primary['r_squared']:.2%} of the differences in team wins** this season. Most of the differences lie outside this simple model.")
        st.markdown('**Conclusion.** Payroll offers a useful comparison point, but spending alone is too limited a guide for a team budget. This connection does not tell us how many wins extra spending would cause.')
        with st.expander('How was this calculated?'):
            st.markdown(f"Pearson r = {primary['r']:.4f}. R² = {primary['r_squared']:.4f}. The ordinary least squares equation is wins = {primary['intercept']:.4f} + {primary['slope']:.6f} × Opening Day payroll in \\$M. The slope is {primary['slope']*10:.3f} wins per \\$10M. These are within-sample associations, not wins purchased.")
    st.subheader('Three teams. Three different spending stories.')
    brewers, mets, marlins = (teams[i] for i in (158,121,146))
    gap = summary['brewers_vs_mets']
    # Full-width stories keep the reading order clear on phones and desktops.
    for key,team,headline,evidence,meaning in [
        ('brewers',brewers,'Milwaukee won more while spending less',
         f"Milwaukee led MLB in wins and finished {brewers['wins_above_fit']:+.2f} wins ahead of the payroll benchmark. It won {gap['wins_more']} more games than the Mets with \\${gap['payroll_less']:,} less payroll.",
         'Milwaukee is a useful case for studying wins relative to payroll spending. This comparison does not establish which decisions made the difference or whether the result will repeat.'),
        ('mets',mets,'The biggest payroll did not lead the standings',
         f"New York had MLB’s highest Opening Day payroll. It won {int(mets['wins'])} games against a model benchmark of {mets['fitted_wins']:.2f}: {mets['wins_above_fit']:+.2f} wins relative to that benchmark.",
         'A bigger payroll did not guarantee more wins in this comparison. The shortfall is not proof of poor management or financial loss.'),
        ('marlins',marlins,'The lowest payroll per win still came with a losing record',
         f"Miami ranked #{int(marlins['efficiency_rank'])} for lowest payroll per win. It spent \\${summary['marlins_vs_brewers']['payroll_less']:,} less than Milwaukee, but won {summary['marlins_vs_brewers']['wins_fewer']} fewer games.",
         'Payroll per win and competitive success answer different questions. Read this measure alongside total wins; it does not measure revenue, profit or financial return.')]:
        with card('summary_'+key):
            st.subheader(headline)
            st.markdown(f"**{team['team']}** · {int(team['wins'])}–{int(team['losses'])} · \\${int(team['payroll']):,} payroll · \\${team['cost_per_win']:,.2f} per win")
            st.markdown('**Observation.** '+evidence)
            st.markdown('**Conclusion / business implication.** '+meaning)
    colorado=teams[115]
    with st.expander('Does Colorado’s unusual season change the story?'):
        st.markdown(f"**Observation.** Colorado went {int(colorado['wins'])}–{int(colorado['losses'])} with \\${int(colorado['payroll']):,} payroll: {colorado['wins_above_fit']:+.2f} wins against a benchmark of {colorado['fitted_wins']:.2f}. Leaving it out changes the model’s strength from {primary['r_squared']:.2%} to {sensitivity['r_squared']:.2%}. The spending–wins connection stays positive, but its size changes.")
        st.markdown('**Conclusion.** Colorado remains in the primary 30-team fit and all rankings. An unusual, valid result helps show how sensitive a small study can be; it is not a reason to remove data.')
        st.markdown(f"**Technical detail.** Slope: {primary['slope']*10:.3f} to {sensitivity['slope']*10:.3f} wins per \\$10M ({summary['slope_change_pct']:+.2f}%). R²: {primary['r_squared']:.4f} to {sensitivity['r_squared']:.4f}; sensitivity n = 29.")
    st.info('Hypothesis for future testing: some team practices may help explain repeated results ahead of a payroll benchmark. The multi-year view describes historical patterns, but does not measure those practices or establish their effects.')
    st.caption('Opening Day payroll is not total team spending. These comparisons do not establish causes, management quality, profit, or future performance. Dollar amounts are exact source figures; calculated values are rounded for display.')

# iveret backend documentation

This folder documents the plotting backend behind the iveret weather-map website
(the `vaerkart*.html` pages).

| Document | Contents |
|---|---|
| [overview.md](overview.md) | Project purpose, processing chain, deployment layout, dependencies |
| [weather-sources.md](weather-sources.md) | Weather sources: where the data comes from, which variables are required, which time steps are plotted |
| [domains-and-plots.md](domains-and-plots.md) | Plot domains, the catalogue of plot types, and which plot types are produced per domain and weather source |

The tables are derived from the code as of this writing. The authoritative
definitions live in:

- `plotconfig.py`: domains, variables, plot types, plots per source/domain, web pages
- `plotconfig_ihavet.py`: the same for the ocean (NorKyst) pages
- `plot_forecast*.py`: how each source's input files are read and which time steps are plotted
- `download_*.py`, `download_cleanup_*.sh`: which data is fetched
- `plot_n_update*.sh`: the run order of each source's pipeline

If you change one of these files, please update the matching table here.

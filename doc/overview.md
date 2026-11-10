# Overview

## Purpose

This repository is the backend of the iveret weather-map website (served from
`iveret.gfi.uib.no`). It produces map plots, vertical cross sections and
meteograms from several numerical weather prediction (NWP) and ocean models. It
also renders the static HTML pages (`vaerkart*.html`, `publoop.html`) that let a
user page through forecast lead times, earlier initialisations and plot types.

The website itself is static. All "dynamic" content comes from this backend
being run periodically. Each run:

1. finds the most recent forecast initialisation that should now be available,
2. downloads the input data (for most sources),
3. plots every configured plot type for every configured domain and time step,
4. writes a status file recording which initialisation has been plotted,
5. re-renders the HTML pages from Jinja2 templates, and
6. deletes old input data and old plots.

The periodic triggering (e.g. cron) is configured on the server and is not part
of this repository.

## Processing chain per source

| Pipeline script | Source | Download step | Plot scripts | Status file written |
|---|---|---|---|---|
| `plot_n_update.sh` | ECMWF HRES, ensemble, AIFS / GraphCast | *external*: data is placed in `/share/base/ecmwf/<init>/` and `/share/base/ecmwf_ai/<init>/` by another process (user `ecmwf`). The script waits for marker files (up to 2 h for HRES, 1 h each for ensemble and meteogram files). | `plot_forecast_eclocal2.py`, `plot_forecast2.py <set>` with sets `ai`, `isentropic`, `pv2`, `sfc`, `plev`, then `ens`; `plot_forecast_meteograms.py` | `status/ecmwf` |
| `plot_n_update_ext.sh` | ECMWF extended-range ensemble | *external*, into `/share/base/ecmwf_ext/<init>/`; waits for `ec.ens.<init>.850.t.nc` | `plot_forecast_ext2.py all` | `status/ecmwf_ext` |
| `plot_n_update_arome.sh` | MET Norway AROME (MEPS) and AROME Arctic | `download_cleanup_arome.sh` → `download_arome.py`, `download_arome_section.py` (OPeNDAP, thredds.met.no) | `plot_forecast_arome2.py`, `plot_forecast_arome_arctic2.py`, `plot_forecast_arome_section.py` | `status/arome` |
| `plot_n_update_gfs.sh` | NOAA GFS 0.5° | `download_cleanup_gfs.sh` (wget, NOMADS) | `plot_forecast_gfs2.py` with sets `pv2`, `sfc`, `plev` | `status/gfs` |
| `plot_n_update_dmi.sh` | DMI HARMONIE DINI | `download_cleanup_dmi.sh` (wget, DMI open data S3, needs API key, filters GRIB with `grib_copy`) | `plot_forecast_dmi2.py` | `status/dmi` |
| `plot_n_update_kyst.sh` | MET Norway NorKyst-800 (ocean) | `download_cleanup_kyst.sh` (wget, thredds NCSS) | `plot_forecast_kyst2.py` | – |

After plotting, most pipelines also run:

- `publoop.py`: renders `publoop.html`, a slide show of selected ECMWF and AROME plots. It reads the `status/ecmwf` and `status/arome` files.
- `cleanup.py`: deletes plots older than 10 days. Exceptions: extended-range `mtafreqa` plots are kept for 40 days, and analysis-time plots (init = valid) of a few ECMWF plot types are kept permanently as an archive (`natl`: `z500_msl`, `t850_msl`, `tcwv`, `iwvt_axis`, `ptpv2_jets`; `npolar`: `z500_msl`, `t850_msl`, `tcwv`, `ptpv2_jets`).

Other helpers:

| Script | Role |
|---|---|
| `current_fc*.py`, `current_ext_fc.py` | Return the init time that should be available now (see [weather-sources.md](weather-sources.md)). They also read back the last plotted init from the status files. |
| `cleanup_ec.sh`, `cleanup_ai.sh`, `cleanup_ec_ext.sh` | Delete old ECMWF input data (34 h, 34 h and 60 h respectively). |
| `cleanup_mtaens.py` | Prunes the saved ensemble moisture transport axis (MTA) and jet detections in `/share/web/mtaens` and `/share/web/jetens`. Keeps 11 days, plus Monday 00 UTC inits indefinitely. Not called by any pipeline script. |
| `update_KH_position.py` | Fetches the current position of RV *Kronprins Haakon* and stores it in `status/KH_position.pickle`. The position defines the moving `ff_kh` domain. |
| `extract_decorations.sh` | Manual tool: crops colour bars from plots made with `DECORATIONS = True` into `templates/static/deco/cbar_*.png`. |

## Code structure

- **`plotconfig.py`**: the central, declarative configuration:
  - `domains`: map projection and figure geometry per plot domain
  - `variables`: name, unit and level of every plotted quantity
  - `map_archetypes()` / `sect_archetypes()` / `special_archetypes()`: plot types, made of one shading and a list of overlays (contours, barbs, quivers, lines, extra shadings)
  - `plots[fcsrc][domain]`: which plot types are made for which source and domain
  - `pages`, `plots_per_page`: the HTML page per (source, domain)
  - `plotter`: the class that draws one plot type for one time step
  - `render_webpage()`: renders `templates/template_jinja2.html`
- **`plotconfig_ihavet.py`**: the same structure for the ocean pages (written to `/share/web/ocean`).
- **`settings/common2.py`**: global dynlib plot settings (colour maps, unit-conversion hooks) and the paths `VAERKART_ROOT` and `WEB_ROOT`.
- **`plot_forecast*.py`**: one script per source. Each one maps the abstract variable names from `plotconfig.py` to the source's file/GRIB names (`q_map`), computes derived quantities (`get_special`), loops over time steps and calls `plotter.plot()`.

A plot type declares what it needs through its variables. `plotter.requires` lists
the `(level, variable name)` pairs. Each plot script loads (or derives) every
required pair once and shares it between all plots. When a required field is
missing, the plot is still written, as an "Error: Data unavailable" image.

### Output naming

```
/share/web/plots/<domain>/<plot type>/<fcsrc>/<init YYYYmmddHH>_for_<valid YYYYmmddHH>.png
```

`<fcsrc>` is the source key: `ec`, `ec_ext`, `noaa`, `no`, `dmi`, `no_kyst`. Note that
`ec_local` and `no_arctic` write into `ec` and `no` respectively. The website reaches
the plots under `/maps`.

## Deployment layout

| Path | Contents |
|---|---|
| `/home/ubuntu/sw/vaerkart` | This repository (`VAERKART_ROOT`) |
| `/home/ubuntu/sw/vaerkart/dynlib`, `.../topens` | Required libraries checked out next to the code (git-ignored) |
| `/home/ubuntu/sw/vaerkart/.dmi_api_key` | Shell file defining `API_KEY` for DMI open data (git-ignored) |
| `/home/ubuntu/data` | ERA5 1979–2020 climatologies and percentiles (`ea.ans.1979-2020.*`) |
| `/home/ubuntu/log` | Log files of every step (`web_*_out.log` / `_err.log`) |
| `/home/ubuntu/log/status` | Status files: last plotted init per source, ship position |
| `/share/base/{ecmwf,ecmwf_ai,ecmwf_ext,metno,metno_kyst,noaa,dmi2}` | Input data, one sub-folder per init |
| `/share/web` | Web root (`WEB_ROOT`): HTML pages, `plots/`, `ocean/`, `mtaens/`, `jetens/`, `static/` |

## Dependencies

### Runtime environment

Production runs **Python 3.10** with deliberately **older package versions**. The
reason is the compiled Fortran extension in `dynlib` (`dynfor`): it is built with
f2py against a specific NumPy, and newer NumPy/Python versions break the binding.
Do not upgrade NumPy, Matplotlib or Basemap without first rebuilding and testing
`dynlib`.

The repository has no `requirements.txt`, and the exact versions are not
recorded here. To capture them, run `pip freeze` on the production host and keep
the result in this folder.

### Python packages

| Package | Used for | Used in |
|---|---|---|
| **dynlib** (UiB, contains the Fortran module `dynfor`) | File access (`metopen`), map plotting (`fig.map`, overlays), map projections, colour maps, thermodynamics, diagnostics (deformation, frontogenesis, irrotational wind), feature detection (jet / moisture-transport axes, fronts, cyclones, cold-air outbreak index), spherical-harmonic filtering | all plot scripts, `settings/common2.py` |
| **topens** (`PersistentGraph`) | Multimodality / clustering in the ensemble meteograms | `plot_forecast_meteograms.py` |
| numpy | Arrays | everywhere |
| scipy | `interpolate.RectBivariateSpline` (θ at jet axis positions) | `plot_forecast2.py`, `plot_forecast_gfs2.py`, … |
| matplotlib (Agg backend) | Plotting | all plot scripts |
| basemap (`mpl_toolkits.basemap`) | Map projections, via `dynlib.shorthands.proj` (e.g. `proj.Basemap` for `ff_kh`) | `plotconfig.py` |
| netCDF4 | NetCDF reading/writing (dynlib, xarray engine) | all |
| xarray | OPeNDAP download of AROME data | `download_arome*.py` |
| pandas | Writing the ensemble jet / MTA detections | `plot_forecast2.py` |
| pygrib | Reading GRIB2 | `plot_forecast_gfs2.py`, `plot_forecast_dmi2.py` |
| pyproj | NorKyst vector rotation | `plot_forecast_kyst2.py` |
| jinja2 | HTML page rendering | `plotconfig.py`, `publoop.py` |
| requests | Ship position | `update_KH_position.py` |

### Command-line tools

| Tool | Used for |
|---|---|
| bash, GNU coreutils/`date`, `find` | Pipeline scripts |
| `wget` | GFS, DMI and NorKyst downloads |
| `grib_copy` (ecCodes) | Subsetting the DMI GRIB files |
| `convert` (ImageMagick) | `extract_decorations.sh` |
| `sudo` (as user `ecmwf`) | Deleting ECMWF input data in `cleanup_ec*.sh`, `cleanup_ai.sh` |

### External data and services

| Data / service | Used for |
|---|---|
| ECMWF HRES, ensemble, extended-range and AIFS/GraphCast data | Delivered to `/share/base/ecmwf*` by a separate process outside this repository |
| thredds.met.no (OPeNDAP / NCSS) | AROME/MEPS, AROME Arctic, NorKyst-800 |
| nomads.ncep.noaa.gov | GFS |
| dmi-opendata.s3.eu-north-1.amazonaws.com | DMI HARMONIE DINI (API key required) |
| vessel.npolar.io | Position of RV *Kronprins Haakon* |
| ERA5 1979–2020 climatologies (`/home/ubuntu/data`) | Temperature/geopotential percentiles, monthly SST, cyclone and MTA climatologies |
| `settings/ecmwf_hrfc_sea_mask.npy` | Land/sea mask for the high-resolution ECMWF regional plots |
| `settings/norkyst_bathymetry.nc` | Bathymetry contours in the NorKyst plots |

## Known quirks

- `plot_n_update.sh` stops with `exit -1` if the ensemble files never arrive, so meteograms and `cleanup.py` are skipped for that run.
- `publoop.py` builds the colour-bar name as `cbar_<fcsrc>_for_<plot>.png`, without the domain. The AROME Arctic `shf_winds` panel therefore looks for `cbar_no_for_shf_winds.png`, which does not exist (the matching file is `cbar_no_for_arctic_shf_winds.png`).

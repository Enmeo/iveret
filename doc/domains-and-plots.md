# Plot domains and plot types

## Plot domains

Map domains are defined in `plotconfig.domains`. Projections come from
`dynlib.shorthands.proj`. Figures are saved at 96 dpi without decorations
(colour bars are separate images in `templates/static/deco/`).

| Domain key | Region | Projection (`proj.*`) | Figure size (in → px) | Sources plotting it |
|---|---|---|---|---|
| `npolar` | Northern Hemisphere | `n_hemisphere_forecast` | 6.4 × 6.4 → 614 × 614 | `ec`, `ec_ext`, `noaa` |
| `spolar` | Southern Hemisphere | `s_hemisphere_forecast` | 6.4 × 6.4 → 614 × 614 | `ec`, `ec_ext`, `noaa` |
| `natl` | North Atlantic | `N_Atlantic_forecast` | 7.2 × 4.8 → 691 × 461 | `ec`, `noaa` |
| `tindpac` | Tropical Indo-Pacific | `Tropical_IndoPacific` | 12.5 × 5.0 → 1200 × 480 | `ec` |
| `ff_kh` | Moving 4500 × 4500 km domain centred on RV *Kronprins Haakon* (position from `update_KH_position.py`, ship marked) | gnomonic `Basemap`, built at import time | 6.4 × 6.4 → 614 × 614 | `ec` |
| `nordicseas` | Nordic Seas | `Nordic_Seas` | 5.0 × 6.25 → 480 × 600 | `ec` |
| `atlarctic` | Atlantic sector of the Arctic | `Atlantic_Arctic` | 5.0 × 6.25 → 480 × 600 | `ec` |
| `scandes` | Scandinavia | `Scandinavia` | 5.5 × 6.18 → 528 × 593 | `ec_local`, `no` |
| `barents` | Barents Sea | `Barents_Sea` | 5.0 × 6.375 → 480 × 612 | `ec_local`, `no_arctic` |
| `snorway` | Southern Norway | `S_Norway` | 6.4 × 6.4 → 614 × 614 | `no`, `dmi`, `no_kyst` |
| `vestland` | Vestland county (western Norway) | `Vestland` | 6.4 × 6.4 → 614 × 614 | `no`, `dmi`, `no_kyst` |
| `bergen` | Bergen area | `Bergen` | 6.4 × 6.4 → 614 × 614 | `no_kyst` |

The NorKyst plots use their own copies of `snorway`, `vestland` and `bergen` from
`plotconfig_ihavet.domains`. Projection and size are the same, but the current-vector
spacing differs (`vector_space_interval` 20 / 10 / 2).
| `dmi` | DMI DINI model domain (north-western Europe) | `DMI_Arome` | 6.4 × 6.4 → 614 × 614 | `dmi` |

Non-map "domains":

| Domain key | What | Defined in | Figure size | Source |
|---|---|---|---|---|
| `we60` | Vertical west–east cross section along ~60° N (axis 4–14° E, 1050–80 hPa) | `plot_forecast_arome_section.py` | 9.6 × 4.8 → 922 × 461 | `no` (MEPS model levels) |
| `meteograms` | Ensemble meteograms for Bergen | `plot_forecast_meteograms.py` | 8.4 × 3.6 → 806 × 346 | `ec` (ensemble) |

## Domains × sources

Number of plot types per (domain, source). Empty means the combination is not produced.

| Domain | `ec` | `ec_local` | `ec_ext` | `noaa` | `no` | `no_arctic` | `dmi` | `no_kyst` |
|---|---|---|---|---|---|---|---|---|
| `natl` | 21 | | | 13 | | | | |
| `npolar` | 12 | | 4 | 4 | | | | |
| `spolar` | 11 | | 4 | 4 | | | | |
| `tindpac` | 5 | | | | | | | |
| `ff_kh` | 4 | | | | | | | |
| `nordicseas` | 4 | | | | | | | |
| `atlarctic` | 4 | | | | | | | |
| `scandes` | | 9 | | | 13 | | | |
| `barents` | | 9 | | | | 13 | | |
| `snorway` | | | | | 13 | | 10 | 3 |
| `vestland` | | | | | 13 | | 10 | 3 |
| `bergen` | | | | | | | | 3 |
| `dmi` | | | | | | | 10 | |
| `we60` | | | | | 4 | | | |
| `meteograms` | 9 | | | | | | | |

## Plot type catalogue

### Map plot types (`plotconfig.map_archetypes()`)

| Plot type | Title on website | Shading | Overlays |
|---|---|---|---|
| `z500_msl` | 500 hPa Geopotential and SLP | Z500 | 552 gpdm contour, SLP |
| `z500_msl_aifs` | … (AIFS) | Z500 from AIFS | 552 gpdm contour, SLP from AIFS |
| `t850_msl` | 850 hPa Temperature, SLP and wind barbs | T850 | 0 °C contour, SLP, 850 hPa barbs |
| `t925_msl` | 925 hPa Temperature, SLP and wind barbs | T925 | 0 °C contour, SLP, 925 hPa barbs |
| `t2m_msl` | 2m Temperature and SLP | T2m | 0 °C contour, SLP |
| `t850_perc` | 850 hPa Temperature anomalies | T850 anomaly vs. ERA5 median | Monthly / yearly recurrence and record contours (ERA5 1979–2020 percentiles) |
| `q925_msl`, `q850_msl` | 925/850 hPa Specific humidity, SLP and wind barbs | q | T850 −5 °C, SLP, barbs |
| `eqpt850_cape` | 850 hPa EQPT, CAPE and fronts | θe 850 | Frontal volumes, frontogenesis ±, CAPE 250/500/1000/2000 J/kg, SLP |
| `deform850_fronts` | 850 hPa Deformation, fronts and precipitation | Total deformation 850 | Frontal volumes, axes of dilatation, T850 −5 °C, large-scale and convective precip |
| `tcwv` | Total column water vapour, fluxes and precip. | TCWV | IWVT vectors, large-scale and convective precip, T850 −5 °C |
| `iwvt_axis` | Water vapour transport, axes, and precipitation | \|IWVT\| | Moisture transport axes, precip, T850 −5 °C |
| `tcc` | Cloud cover | Low clouds | Mid- and high-cloud shadings |
| `ff10_gusts` | 10m wind speed, barbs and gusts | 10 m wind speed | Gust contours 17.2/24.5/32.7 m/s, 10 m barbs |
| `rh2m_tp` | 2m Relative humidity and precipitation | RH2m | Precipitation shading, sea ice 0.2/0.8, T850 −5 °C |
| `clba_msl` | Cloud base altitude and SLP | Cloud base | SLP |
| `cao_winds` | Cold-air outbreak index, 10m winds, SSTs and MIZ | CAO index | SST, sea-ice edge, 10 m wind thresholds |
| `shf_winds` | Surface fluxes, 10m winds, SSTs and MIZ | Sensible + latent heat flux | 10 m barbs, SST, sea ice, wind thresholds |
| `sshf_winds` | Sensible heat flux, 10m winds, SSTs and MIZ | Sensible heat flux | as `shf_winds` |
| `slhf_winds` | Latent heat flux, 10m winds, SSTs and MIZ | Latent heat flux | as `shf_winds` |
| `ssta_ssh` | SST anomalies, sea-surface height and 10 winds | SST anomaly (ERA5 monthly) | 10 m barbs, sea-surface height |
| `sfc_fcerror` | Sea-level pressure forecast increment | SLP change vs. previous init (−12 h) | SLP |
| `w850_ff` | 850 hPa Vertical wind and 925 hPa wind speed | 925 hPa wind speed | 850 hPa vertical wind |
| `w700_winds`, `w500_winds` | 700/500 hPa Vertical wind and wind barbs | Vertical wind | Barbs |
| `pvpt315_irot_wind`, `pvpt330_irot_wind` | 315/330 K Pot. Vorticity and irrot. winds | PV on isentrope | PV = 2 contour, irrotational wind vectors |
| `ptpv2_jets` | PV2 Pot. temperature, jets and wind speed | θ on PV2 | T84-filtered wind speed, jet axes coloured by θ |
| `eddy_uv` | 300 hPa eddy u'v', 500 hPa geopotential and jets | u'v' 300 | Z500, jet axes |
| `eddy_vT` | 850 hPa eddy v'T' and SLP | v'T' 850 | SLP |
| `cycfreq_msl` | Ensemble feature detections | Ensemble cyclone frequency | MTA and jet frequency (10/50/90 %), control and ensemble-mean SLP |
| `prob_z500` | Probability of high and low-pressure conditions | P(Z500 < 30th pct.) | P(Z500 > 70th pct.) |
| `prob_t850` | Probability of warm and cold conditions | P(T850 < 30th pct.) | P(T850 > 70th pct.) |
| `cycfreqa` | Ensemble Cyclone detection anomalies | Cyclone frequency anomaly vs. ERA5 | – |
| `mtafreqa` | Ensemble MTA detection anomalies | MTA frequency anomaly vs. ERA5 | – |

### Ocean plot types (`plotconfig_ihavet.map_archetypes()`)

| Plot type | Title | Shading | Overlays |
|---|---|---|---|
| `sst_sfccur` | SST and surface currents | SST | Bathymetry 500/1000/1500 m, current vectors |
| `sss_sfccur` | SSS and surface currents | Sea-surface salinity | Bathymetry, current vectors |
| `ff_sfccur` | Surface current speed and direction | Current speed | Bathymetry, current vectors |

### Cross-section plot types (`we60`, `plot_forecast_arome_section.py`)

| Plot type | Title | Shading | Overlays |
|---|---|---|---|
| `ff_pt` | Winds and pot. temperature | Cross-plane wind | θ (5 K; 270/300/350 K bold), in-plane wind vectors |
| `eqpt_pt` | Equivalent pot. and pot. temperature | θe | 0 °C isotherm, θ |
| `q_pt` | Humidity and pot. temperature | q | 0 °C isotherm, θ |
| `cc_pt` | Cloud cover and pot. temperature | Cloud fraction | θ |

(`eturb_pt`, turbulent kinetic energy, is defined but disabled.)

### Meteogram plot types (`meteograms`, Bergen)

| Plot type | Content |
|---|---|
| `t2m_bgo`, `tcwv_bgo`, `msl_bgo` | Ensemble meteogram of 2 m temperature / TCWV / SLP |
| `t2m_modal_bgo`, `tcwv_modal_bgo`, `msl_modal_bgo` | Multimodality analysis (KMeans, `topens.PersistentGraph`) |
| `t2m_modal_naive_bgo`, `tcwv_modal_naive_bgo`, `msl_modal_naive_bgo` | Multimodality analysis (naive method) |

## Plot types per domain and weather source

Taken from `plotconfig.plots` (and `plotconfig_ihavet.plots` for NorKyst).

### ECMWF HRES (`ec`, plot_forecast2.py)

| Plot type | `natl` | `npolar` | `spolar` | `tindpac` | `ff_kh` | `nordicseas` | `atlarctic` |
|---|---|---|---|---|---|---|---|
| `z500_msl` | ✓ | ✓ | ✓ |  |  |  |  |
| `t850_msl` | ✓ | ✓ | ✓ | ✓ |  |  |  |
| `t850_perc` | ✓ |  |  |  |  |  |  |
| `eqpt850_cape` | ✓ |  |  | ✓ |  |  |  |
| `deform850_fronts` | ✓ |  |  |  |  |  |  |
| `tcwv` | ✓ | ✓ | ✓ | ✓ |  |  |  |
| `iwvt_axis` | ✓ | ✓ | ✓ | ✓ |  |  |  |
| `ff10_gusts` | ✓ |  |  |  |  |  |  |
| `tcc` | ✓ |  |  |  |  |  |  |
| `rh2m_tp` | ✓ |  |  | ✓ | ✓ | ✓ | ✓ |
| `sshf_winds` | ✓ |  |  |  |  |  |  |
| `slhf_winds` | ✓ |  |  |  |  |  |  |
| `cao_winds` | ✓ |  |  |  | ✓ | ✓ | ✓ |
| `sfc_fcerror` | ✓ | ✓ |  |  |  |  |  |
| `cycfreq_msl` | ✓ | ✓ | ✓ |  |  |  |  |
| `pvpt315_irot_wind` | ✓ | ✓ | ✓ |  |  |  |  |
| `pvpt330_irot_wind` | ✓ | ✓ | ✓ |  |  |  |  |
| `ptpv2_jets` | ✓ | ✓ | ✓ |  |  |  |  |
| `eddy_uv` | ✓ | ✓ | ✓ |  |  |  |  |
| `eddy_vT` | ✓ | ✓ | ✓ |  |  |  |  |
| `z500_msl_aifs` | ✓ | ✓ | ✓ |  |  |  |  |
| `shf_winds` |  |  |  |  | ✓ | ✓ | ✓ |
| `ssta_ssh` |  |  |  |  | ✓ | ✓ | ✓ |

### ECMWF HRES high-res regional (`ec_local`, plot_forecast_eclocal2.py)

| Plot type | `scandes` | `barents` |
|---|---|---|
| `t2m_msl` | ✓ | ✓ |
| `t925_msl` | ✓ | ✓ |
| `t850_msl` | ✓ | ✓ |
| `q925_msl` | ✓ | ✓ |
| `q850_msl` | ✓ | ✓ |
| `ff10_gusts` | ✓ | ✓ |
| `rh2m_tp` | ✓ | ✓ |
| `cao_winds` | ✓ | ✓ |
| `shf_winds` | ✓ | ✓ |

### ECMWF extended range (`ec_ext`, plot_forecast_ext2.py)

| Plot type | `npolar` | `spolar` |
|---|---|---|
| `prob_z500` | ✓ | ✓ |
| `prob_t850` | ✓ | ✓ |
| `cycfreqa` | ✓ | ✓ |
| `mtafreqa` | ✓ | ✓ |

### NOAA GFS (`noaa`, plot_forecast_gfs2.py)

| Plot type | `natl` | `npolar` | `spolar` |
|---|---|---|---|
| `z500_msl` | ✓ | ✓ | ✓ |
| `t850_msl` | ✓ | ✓ | ✓ |
| `t850_perc` | ✓ |  |  |
| `eqpt850_cape` | ✓ |  |  |
| `tcwv` | ✓ | ✓ | ✓ |
| `iwvt_axis` | ✓ |  |  |
| `ff10_gusts` | ✓ |  |  |
| `tcc` | ✓ |  |  |
| `rh2m_tp` | ✓ |  |  |
| `sshf_winds` | ✓ |  |  |
| `slhf_winds` | ✓ |  |  |
| `cao_winds` | ✓ |  |  |
| `ptpv2_jets` | ✓ | ✓ | ✓ |

### MET Norway AROME/MEPS + AROME Arctic (`no` / `no_arctic`, plot_forecast_arome2.py, plot_forecast_arome_arctic2.py)

| Plot type | `vestland` | `snorway` | `scandes` | `barents` |
|---|---|---|---|---|
| `t2m_msl` | ✓ | ✓ | ✓ | ✓ |
| `t925_msl` | ✓ | ✓ | ✓ | ✓ |
| `t850_msl` | ✓ | ✓ | ✓ | ✓ |
| `q925_msl` | ✓ | ✓ | ✓ | ✓ |
| `q850_msl` | ✓ | ✓ | ✓ | ✓ |
| `w850_ff` | ✓ | ✓ | ✓ | ✓ |
| `w500_winds` | ✓ | ✓ | ✓ | ✓ |
| `w700_winds` | ✓ | ✓ | ✓ | ✓ |
| `ff10_gusts` | ✓ | ✓ | ✓ | ✓ |
| `rh2m_tp` | ✓ | ✓ | ✓ | ✓ |
| `clba_msl` | ✓ | ✓ | ✓ | ✓ |
| `cao_winds` | ✓ | ✓ | ✓ | ✓ |
| `shf_winds` | ✓ | ✓ | ✓ | ✓ |

### DMI HARMONIE DINI (`dmi`, plot_forecast_dmi2.py)

| Plot type | `vestland` | `snorway` | `dmi` |
|---|---|---|---|
| `t2m_msl` | ✓ | ✓ | ✓ |
| `t925_msl` | ✓ | ✓ | ✓ |
| `t850_msl` | ✓ | ✓ | ✓ |
| `q925_msl` | ✓ | ✓ | ✓ |
| `q850_msl` | ✓ | ✓ | ✓ |
| `ff10_gusts` | ✓ | ✓ | ✓ |
| `rh2m_tp` | ✓ | ✓ | ✓ |
| `clba_msl` | ✓ | ✓ | ✓ |
| `cao_winds` | ✓ | ✓ | ✓ |
| `shf_winds` | ✓ | ✓ | ✓ |

Note: in the AROME table, `vestland`, `snorway` and `scandes` come from MEPS
(`plot_forecast_arome2.py`, `plots['no']`). `barents` comes from AROME Arctic
(`plot_forecast_arome_arctic2.py`, `plots['no_arctic']`). Both write into the
`no` plot folder.

### MET Norway AROME/MEPS cross section (`no`, plot_forecast_arome_section.py)

| Plot type | `we60` |
|---|---|
| `ff_pt` | ✓ |
| `eqpt_pt` | ✓ |
| `q_pt` | ✓ |
| `cc_pt` | ✓ |

### MET Norway NorKyst-800 (`no_kyst`, plot_forecast_kyst2.py)

| Plot type | `bergen` | `vestland` | `snorway` |
|---|---|---|---|
| `sst_sfccur` | ✓ | ✓ | ✓ |
| `sss_sfccur` | ✓ | ✓ | ✓ |
| `ff_sfccur` | ✓ | ✓ | ✓ |

### ECMWF ensemble meteograms (`ec`, plot_forecast_meteograms.py)

All nine meteogram plot types are produced for `meteograms`, once per init.

## ECMWF plot sets

`plot_forecast2.py` and `plot_forecast_gfs2.py` take a plot-set argument, so
`plot_n_update*.sh` can run several processes in parallel. Each set picks plot
types; the domains come from the tables above.

| Script | Set | Plot types |
|---|---|---|
| `plot_forecast2.py` | `plev` | `z500_msl`, `t850_msl`, `deform850_fronts`, `eqpt850_cape`, `eddy_vT`, `tcwv`, `iwvt_axis`, `t850_perc` |
| | `isentropic` | `pvpt315_irot_wind`, `pvpt330_irot_wind` |
| | `pv2` | `ptpv2_jets`, `eddy_uv` |
| | `sfc` | `tcc`, `ff10_gusts`, `cao_winds`, `ssta_ssh`, `sshf_winds`, `slhf_winds`, `shf_winds`, `rh2m_tp`, `sfc_fcerror` |
| | `ai` | `z500_msl_aifs` |
| | `ens` | `cycfreq_msl` |
| | `website_only`, `test` | nothing (only re-renders the pages) |
| `plot_forecast_gfs2.py` | `plev` | `z500_msl`, `t850_msl`, `eqpt850_cape`, `tcwv`, `iwvt_axis`, `t850_perc` |
| | `pv2` | `ptpv2_jets` |
| | `sfc` | `tcc`, `ff10_gusts`, `cao_winds`, `sshf_winds`, `slhf_winds`, `rh2m_tp` |
| `plot_forecast_ext2.py` | `all` | `prob_z500`, `prob_t850`, `cycfreqa`, `mtafreqa` |

Without an argument, every plot type of the source is plotted.

## Web pages

One HTML page per (source, domain), from `plotconfig.pages` (under `/share/web`) and
`plotconfig_ihavet.pages` (under `/share/web/ocean`):

| Source | Domain | Page title | File |
|---|---|---|---|
| `noaa` | `natl` | GFS forecasts North Atlantic | `/vaerkart.html` |
| `noaa` | `npolar` | GFS forecasts Northern Hemisphere | `/vaerkart_npolar.html` |
| `noaa` | `spolar` | GFS forecasts Southern Hemisphere | `/vaerkart_spolar.html` |
| `ec` | `natl` | ECMWF forecasts North Atlantic (restricted) | `/closed/vaerkart_ec.html` |
| `ec` | `npolar` | ECMWF forecasts Northern Hemisphere (restricted) | `/closed/vaerkart_ec_npolar.html` |
| `ec` | `spolar` | ECMWF forecasts Southern Hemisphere (restricted) | `/closed/vaerkart_ec_spolar.html` |
| `ec` | `tindpac` | ECMWF forecasts Tropical Indopacific (restricted) | `/closed/vaerkart_ec_tindpac.html` |
| `ec` | `ff_kh` | ECMWF forecasts FF Kronprins Haakon (restricted) | `/closed/vaerkart_ec_ff_kh.html` |
| `ec` | `nordicseas` | ECMWF forecasts Nordic Seas (restricted) | `/closed/vaerkart_ec_nordicseas.html` |
| `ec` | `atlarctic` | ECMWF forecasts Atlantic Arctic (restricted) | `/closed/vaerkart_ec_atlarctic.html` |
| `ec` (`ec_local`) | `scandes` | ECMWF forecasts Scandinavia (restricted) | `/closed/vaerkart_ec_scandes.html` |
| `ec` (`ec_local`) | `barents` | ECMWF forecasts Barents Sea (restricted) | `/closed/vaerkart_ec_barents.html` |
| `ec` | `meteograms` | ECMWF forecast Meteograms (restricted) | `/closed/vaerkart_ec_meteograms.html` |
| `ec_ext` | `npolar` | ECMWF extended-range forecasts Northern Hemisphere (restricted) | `/closed/vaerkart_ec_ext_npolar.html` |
| `ec_ext` | `spolar` | ECMWF extended-range forecasts Southern Hemisphere (restricted) | `/closed/vaerkart_ec_ext_spolar.html` |
| `no` | `vestland` | AROME forecasts Vestland | `/vaerkart_arome_vestland.html` |
| `no` | `snorway` | AROME forecasts Southern Norway | `/vaerkart_arome.html` |
| `no` | `scandes` | AROME forecasts Scandinavia | `/vaerkart_arome_scandes.html` |
| `no` | `we60` | AROME forecasts Cross section 60°N | `/vaerkart_arome_we60.html` |
| `no` (`no_arctic`) | `barents` | AROME Arctic forecasts Barents Sea | `/vaerkart_arome_arctic.html` |
| `dmi` | `vestland` | DMI forecasts Vestland | `/vaerkart_dmi_vestland.html` |
| `dmi` | `snorway` | DMI forecasts Southern Norway | `/vaerkart_dmi_snorway.html` |
| `dmi` | `dmi` | DMI forecasts Northwestern Europe | `/vaerkart_dmi_dmi.html` |
| `no_kyst` | `bergen` | NorKyst forecasts Bergen | `/ocean/vaerkart_kyst_bergen.html` |
| `no_kyst` | `vestland` | NorKyst forecasts Vestland | `/ocean/vaerkart_kyst_vestland.html` |
| `no_kyst` | `snorway` | NorKyst forecasts Southern Norway | `/ocean/vaerkart_kyst.html` |

The ECMWF `natl` (since 2017-09-22) and `npolar` (since 2021-06-02) pages also link
to an archive of analysis-time plots at 12-hourly steps. The archived plot types
are the ones `cleanup.py` keeps. Extended-range plots are kept for 40 days.

`publoop.html` (from `publoop.py`) is a slide show of: ECMWF `natl` `z500_msl`,
`tcwv` and `t850_msl` (0–66 h every 6 h, then 72–168 h every 12 h); AROME `scandes`
`t2m_msl`, `rh2m_tp` and `q925_msl`; AROME Arctic `barents` `t2m_msl`, `rh2m_tp` and
`shf_winds` (0–66 h every 6 h).

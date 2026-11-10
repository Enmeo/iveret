# Weather sources

Each source has a key (`fcsrc`). The key is used in `plotconfig.plots`, in the plot
output path and in the page definitions.

## Summary

| Source | `fcsrc` key | Model | Data origin | Format | Input directory | Inits plotted (UTC) | Lead times plotted | Step | Inits selectable on page |
|---|---|---|---|---|---|---|---|---|---|
| ECMWF HRES (global) | `ec` | ECMWF IFS deterministic | external delivery | NetCDF | `/share/base/ecmwf/<YYYYmmddHH>/` | 00, 12 | 0–240 h | 3 h to 69 h, then 6 h from 72 h | 15 (7 days, 12-hourly) |
| ECMWF AI models | `ec` (`*_aifs`, `*_dmgc` plot types) | ECMWF AIFS, Google DeepMind GraphCast | external delivery | NetCDF | `/share/base/ecmwf_ai/<YYYYmmddHH>/` | 00, 12 | as ECMWF HRES | as ECMWF HRES | as ECMWF HRES |
| ECMWF ensemble | `ec` (`cycfreq_msl`, meteograms) | ECMWF IFS ENS, 50 members + control | external delivery | NetCDF | `/share/base/ecmwf/<YYYYmmddHH>/` | 00, 12 | time steps in the ensemble files; meteograms: one image per init | – | 15 |
| ECMWF HRES high resolution (regional) | `ec_local` (written as `ec`) | ECMWF IFS deterministic, full resolution | external delivery | NetCDF | `/share/base/ecmwf/<YYYYmmddHH>/` | 00, 12 | 0–72 h | 3 h | 15 |
| ECMWF extended range | `ec_ext` | ECMWF IFS ENS extended | external delivery | NetCDF | `/share/base/ecmwf_ext/<YYYYmmddHH>/` | 00 (daily) | 0–840 h (35 days) | 12 h | 21 (daily) |
| MET Norway AROME / MEPS | `no` | MEPS deterministic 2.5 km | thredds.met.no, OPeNDAP (`mepslatest`) | NetCDF | `/share/base/metno/<YYYYmmddTHHZ>/` | 00, 06, 12, 18 | 0–66 h | 3 h | 29 (7 days, 6-hourly) |
| MET Norway AROME / MEPS cross section | `no` (domain `we60`) | MEPS deterministic 2.5 km, model levels (`meps_det_vc`) | thredds.met.no, OPeNDAP | NetCDF | `/share/base/metno/<YYYYmmddTHHZ>/` | 00, 06, 12, 18 | 0–66 h | 3 h | 29 |
| MET Norway AROME Arctic | `no_arctic` (written as `no`) | AROME Arctic deterministic 2.5 km | thredds.met.no, OPeNDAP (`aromearcticlatest`) | NetCDF | `/share/base/metno/<YYYYmmddTHHZ>/` | 00, 06, 12, 18 | 0–66 h | 3 h | 29 |
| NOAA GFS | `noaa` | GFS 0.5° (`pgrb2.0p50`) | nomads.ncep.noaa.gov | GRIB2 | `/share/base/noaa/<YYYYmmddHH>/` | 00, 06, 12, 18 | 0–240 h | 3 h to 72 h, then 6 h | 31 (~7.5 days, 6-hourly) |
| DMI HARMONIE DINI | `dmi` | HARMONIE-AROME, DINI domain | DMI open data (S3, API key) | GRIB | `/share/base/dmi2/<YYYYmmddHH>/` | 00, 06, 12, 18 | 0–60 h | 3 h | 29 |
| MET Norway NorKyst-800 (ocean) | `no_kyst` | NorKyst-800m ocean model, surface level | thredds.met.no, NCSS (`fou-hi/norkyst800m-1h`) | NetCDF | `/share/base/metno_kyst/` | 00 (daily) | 0–120 h (analysis + forecast file) | 3 h | 5 (daily) |

### Which init is plotted

Each run plots the init returned by its `current_fc*.py` script. The script
compares the server clock with fixed hour windows, which allow for the time each
source needs to make its data available:

| Source | Script | Server hour → init plotted |
|---|---|---|
| ECMWF HRES / ens / AI | `current_fc.py` | 07–18 → 00 UTC today; 19–23 → 12 UTC today; 00–06 → 12 UTC yesterday |
| ECMWF extended | `current_ext_fc.py` | 00–19 → 00 UTC yesterday; 20–23 → 00 UTC today |
| AROME / AROME Arctic | `current_fc_arome.py` | 02–07 → 00; 08–13 → 06; 14–19 → 12; 20–23 → 18; 00–01 → 18 yesterday |
| DMI | `current_fc_dmi.py` | 03–08 → 00; 09–14 → 06; 15–20 → 12; 21–23 → 18; 00–02 → 18 yesterday |
| GFS | `current_fc_gfs.py` | 04–09 → 00; 10–15 → 06; 16–21 → 12; 22–23 → 18; 00–03 → 18 yesterday |
| NorKyst | `current_fc_kyst.py` | 00–10 → 00 UTC yesterday; 11–23 → 00 UTC today |

### How time steps are selected

- **ECMWF (`ec`, `ec_local`, `ec_ext`)**: every time step in the input files is plotted. The ranges in the table are what the web pages link to (`leadlist` in each plot script), so the delivered files must contain those steps.
- **AROME, AROME Arctic, cross section**: the download takes every 3rd hourly step from 0 to 66 h (`time[0:3:66]`). The plot scripts also skip any step whose hour is not a multiple of 3.
- **GFS**: `download_cleanup_gfs.sh` fetches `f000`–`f072` every 3 h and `f078`–`f240` every 6 h. `plot_forecast_gfs2.py` opens one file per lead time.
- **DMI**: `download_cleanup_dmi.sh` fetches one PL and one SF file per lead time, 0–60 h every 3 h. Files that stay below a minimum size are retried up to 5 times with backoff.
- **NorKyst**: hourly model output downloaded with `timeStride=3`. The analysis and forecast files are joined in time.

## Required variables per source

The **Used by** column lists the plot types (see [domains-and-plots.md](domains-and-plots.md)) that
need each field. Derived quantities are computed in the plot scripts from the
fields listed. Examples: wind speed, equivalent potential temperature, relative
humidity, precipitation rate from accumulations, fronts, jet and moisture
transport axes, cold-air outbreak index.

### ECMWF HRES (`ec`), files `ec.for.<init>.<level>.<var>.nc`

| Level | Variables | Used by |
|---|---|---|
| `sfc` | `msl` | `z500_msl`, `t850_msl`, `eqpt850_cape`, `eddy_vT`, `cao_winds`, `sfc_fcerror`; also masks 850/925 hPa below ground |
| `sfc` | `t2m`, `d2m` | `rh2m_tp` |
| `sfc` | `u10`, `v10`, `fg10` | `ff10_gusts`, `cao_winds`, `*hf_winds`, `ssta_ssh` |
| `sfc` | `lsp`, `cp` (accumulated) | `tcwv`, `iwvt_axis`, `deform850_fronts`, `rh2m_tp` |
| `sfc` | `cape` | `eqpt850_cape` |
| `sfc` | `tcwv` | `tcwv` |
| `sfc` | `viewvt`, `vinwvt` (vertically integrated water vapour flux) | `tcwv`, `iwvt_axis` |
| `sfc` | `lcc`, `mcc`, `hcc` | `tcc` |
| `sfc` | `sst`, `zos`, `siconc`, `sithick` | `cao_winds`, `ssta_ssh`, `rh2m_tp`, `*hf_winds` (`zos` doubles as ocean mask) |
| `sfc` | `sshf`, `slhf` (accumulated) | `sshf_winds`, `slhf_winds`, `shf_winds` |
| `925`, `850`, `700` hPa | `t`, `q` | `eqpt850_cape`, `deform850_fronts` (frontal volumes from θe at 700/850/925) |
| `850` hPa | `t`, `u`, `v` | `t850_msl`, `t850_perc`, `deform850_fronts`, `eqpt850_cape`, `eddy_vT`, −5 °C contour in several plots |
| `500` hPa | `z` | `z500_msl`, `eddy_uv` |
| `300` hPa | `u`, `v` | `eddy_uv` |
| `pt315`, `pt330` (isentropic) | `pv`, `u`, `v` | `pvpt315_irot_wind`, `pvpt330_irot_wind` |
| `pv2000` (PV = 2 surface) | `pt`, `u`, `v` | `ptpv2_jets`, `eddy_uv` |
| previous init (−12 h) | `sfc.msl` | `sfc_fcerror` |

The pipeline starts plotting once `ec.for-hr.<init>.700.t.nc` and
`ec.for.<init>.pt330.pv.nc` exist.

**ECMWF AI models**, in `/share/base/ecmwf_ai/<init>/`:

| File | Used by |
|---|---|
| `aifs.for.<init>.500.z`, `aifs.for.<init>.sfc.msl` | `z500_msl_aifs` |
| `dmgc.for.<init>.500.z`, `dmgc.for.<init>.sfc.msl` | `z500_msl_dmgc` |

**ECMWF ensemble**, files `ec.ens.*` (members) and `ec.ensctrl.*` (control):

| File / variables | Used by |
|---|---|
| `sfc.msl` | `cycfreq_msl` (cyclone frequency, ensemble mean and control SLP). Its arrival gates the `ens` plot set |
| `sfc.viewvt`, `sfc.vinwvt` | `cycfreq_msl` (moisture transport axis frequency) |
| `pv2000.u`, `pv2000.v` | `cycfreq_msl` (jet frequency) |
| `sfc.meteogram.nc` with `t2m`, `tcwv`, `msl` | meteograms (Bergen). Its arrival gates the meteogram step |

Side effect: `plot_forecast2.py ens` writes every member's jet and MTA detections to
`/share/web/jetens` and `/share/web/mtaens`. `plot_n_update.sh` also copies the raw
ensemble `viewvt`/`vinwvt` and `pv2000.u/v` files there.

**Climatology** (`/home/ubuntu/data`): `ea.ans.1979-2020.850.t_percs` (`t850_perc`),
`ea.ans.1979-2020.month_composites` (`sst`, for `ssta_ssh`).

### ECMWF HRES high resolution (`ec_local`), files `ec.for-hr.<init>.<level>.<var>.nc`

| Level | Variables | Used by |
|---|---|---|
| `sfc` | `msl`, `t2m`, `d2m`, `u10`, `v10`, `fg10` | `t2m_msl`, `*_msl`, `rh2m_tp`, `ff10_gusts`, `cao_winds`, `shf_winds` |
| `sfc` | `lsp`, `cp`, `sshf`, `slhf` (accumulated) | `rh2m_tp`, `shf_winds` |
| `sfc` | `sst`, `siconc` | `cao_winds`, `shf_winds`, `rh2m_tp` |
| `925`, `850` hPa | `t`, `q`, `u`, `v` | `t925_msl`, `t850_msl`, `q925_msl`, `q850_msl` |

Plus the static land/sea mask `settings/ecmwf_hrfc_sea_mask.npy`.

### ECMWF extended range (`ec_ext`), files `ec.ens.<init>.<level>.<var>.nc`

| Level | Variables | Used by |
|---|---|---|
| `500` hPa | `z` | `prob_z500` |
| `850` hPa | `t` (its arrival gates the pipeline) | `prob_t850` |
| `sfc` | `msl` | `cycfreqa` |
| `sfc` | `viewvt`, `vinwvt` | `mtafreqa` |

Climatology: `ea.ans.1979-2020.500.z_percs`, `ea.ans.1979-2020.850.t_percs` (30th/70th
percentiles), and `ea.ans.1979-2020.month_composites` (`cyc_freq`, `wvfaxis_dist`).
All fields are 5-day low-pass filtered before plotting.

### MET Norway AROME / MEPS (`no`) and AROME Arctic (`no_arctic`)

Downloaded by `download_arome.py` from the `meps_det_2_5km` and `arome_arctic_det_2_5km`
datasets. Each variable/level goes into its own file:
`arome.<init>.<level>.<var>.nc` or `arome_arctic.<init>.<level>.<var>.nc`.

| Level | Variable (MET Norway name) | Used by |
|---|---|---|
| `sfc` | `air_pressure_at_sea_level` | `*_msl`, `cao_winds` |
| `sfc` | `surface_air_pressure` | masking 850/925 hPa below ground |
| `sfc` | `air_temperature_2m` | `t2m_msl` |
| `sfc` | `relative_humidity_2m` | `rh2m_tp` |
| `sfc` | `x_wind_10m`, `y_wind_10m`, `wind_speed_of_gust` | `ff10_gusts`, `cao_winds`, `shf_winds` |
| `sfc` | `precipitation_amount_acc` | `rh2m_tp` |
| `sfc` | `cloud_base_altitude` | `clba_msl` |
| `sfc` | `SFX_SST`, `SFX_SIC` | `cao_winds`, `shf_winds`, `rh2m_tp` |
| `sfc` | `integral_of_surface_downward_sensible_heat_flux_wrt_time`, `…latent_heat_evaporation_flux…`, `…latent_heat_sublimation_flux…` | `shf_winds` |
| `925`, `850`, `700`, `500` hPa | `air_temperature_pl`, `specific_humidity_pl`, `x_wind_pl`, `y_wind_pl`, `upward_air_velocity_pl` | `t925_msl`, `t850_msl`, `q925_msl`, `q850_msl`, `w850_ff`, `w700_winds`, `w500_winds`, −5 °C contour |
| `925`–`500` hPa | `geopotential_pl` | downloaded, not used by any current plot |

**Cross section** (`download_arome_section.py`, dataset `meps_det_vc_2_5km`). The
section is the grid row `x = 233…454` labelled `W-E_60` (west–east along about
60° N), on model levels 0–64. Files: `arome.<init>.sect.W-E_60.<var>.nc`.

| Variables | Used by |
|---|---|
| `air_temperature_ml`, `ap`, `b`, `surface_air_pressure` (pressure and θ) | all section plots |
| `x_wind_ml`, `y_wind_ml`, `upward_air_velocity_ml` | `ff_pt` |
| `specific_humidity_ml` | `q_pt`, `eqpt_pt` |
| `cloud_area_fraction_ml` | `cc_pt` |

### NOAA GFS (`noaa`), files `gfs.t<HH>z.pgrb2.0p50.f<LLL>` (GRIB names)

| Level | Variables | Used by |
|---|---|---|
| surface | `MSLP (Eta model reduction)` | `*_msl`, `cao_winds` |
| surface | `10 metre U/V wind component`, `Wind speed (gust)` | `ff10_gusts`, `cao_winds`, `*hf_winds` |
| surface (avg) | `Precipitation rate`, `Convective precipitation rate` | `tcwv`, `iwvt_axis`, `rh2m_tp` |
| surface (avg) | `Sensible heat net flux`, `Latent heat net flux` | `sshf_winds`, `slhf_winds` |
| surface | `Precipitable water` | `tcwv` |
| surface | `Convective available potential energy` | `eqpt850_cape` |
| surface | `2 metre relative humidity` | `rh2m_tp` |
| surface | low/mid/high cloud cover (`typeOfFirstFixedSurface` 214/224/234) | `tcc` |
| surface | `Temperature` (as SST), `Sea ice area fraction`, `Land-sea mask` | `cao_winds`, `*hf_winds`, `rh2m_tp` |
| 500 hPa | `Geopotential Height` | `z500_msl` |
| 925, 850, 700 hPa | `Temperature`, `Specific humidity` | `t850_msl`, `t850_perc`, `eqpt850_cape` (fronts) |
| 850 hPa | `U/V component of wind` | `t850_msl`, `eqpt850_cape` |
| 1000–200 hPa (19 levels) | `Specific humidity`, `U/V component of wind` | `tcwv`, `iwvt_axis` (vertically integrated moisture flux computed in the script) |
| tropopause (stands in for PV 2) | `Temperature`, `Tropopause pressure`, `U/V component of wind` | `ptpv2_jets` |

Climatology: `ea.ans.1979-2020.850.t_percs` (`t850_perc`). At lead time 0, accumulated
or averaged fields and cloud cover are set to zero.

### DMI HARMONIE DINI (`dmi`)

Files: `HARMONIE_DINI_{PL,SF}_<init>_<valid>.grib`. After download, the SF and PL
files are reduced with `grib_copy` to these parameters:

| File | paramId | Variable | Used by |
|---|---|---|---|
| SF | 167 | 2 m temperature | `t2m_msl` |
| SF | 54 (heightAboveSea) | Sea-level pressure | `*_msl`, `cao_winds` |
| SF | 165, 166 | 10 m u, v wind | `ff10_gusts`, `cao_winds`, `shf_winds` |
| SF | 260065 | 10 m gusts | `ff10_gusts` |
| SF | 260242 | 2 m relative humidity | `rh2m_tp` |
| SF | 228228 | Total precipitation (accumulated) | `rh2m_tp` |
| SF | 260107 | Cloud base altitude | `clba_msl` |
| SF | 260003, 260002 | Sensible and latent heat flux (accumulated) | `shf_winds` |
| SF | 130 (heightAboveGround 0) | Surface temperature, used as SST | `cao_winds`, `shf_winds` |
| SF | 260179 | Land-sea mask | `cao_winds` |
| PL | 130, 131, 132, 157 at 925/850/700/500 hPa | T, u, v, RH (q is derived from RH and T) | `t925_msl`, `t850_msl`, `q925_msl`, `q850_msl` (only 850/925 used today) |

Sea ice is not available and is set to zero.

### MET Norway NorKyst-800 (`no_kyst`)

Files: `norkyst_an_<init>.sfc.nc` and `norkyst_fc_<init>.sfc.nc`. Surface level
(`vertCoord=0`), 3-hourly.

| Variables | Used by |
|---|---|
| `temperature` | `sst_sfccur` |
| `salinity` | `sss_sfccur` |
| `u`, `v` | all plots (current vectors), `ff_sfccur` |

Plus the static bathymetry `settings/norkyst_bathymetry.nc` (variable `h`).

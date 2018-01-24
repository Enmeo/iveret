#!/bin/bash

# Setup some paths
basepath='/Data/gfi/metno/visualisation'
logpath='/Data/gfi/metno/log'

# Make the scripts find dynlib and django and the matplotlib config
source /Data/gfi/users/local/share/virtualenv/dynpie3/bin/activate
export MPLCONFIGDIR="$basepath/mpl_config"

# Do the plotting first
python $basepath/plot_forecast_arome.py > $logpath/web_plot_no_out.log 2> $logpath/web_plot_no_err.log

# Then render the fitting website
python $basepath/web/render_vaerkart_arome.py > $logpath/web_render_no_out.log 2> $logpath/web_render_no_err.log
python $basepath/web/render_vaerkart_arome_scandies.py > $logpath/web_render_no_scandi_out.log 2> $logpath/web_render_no_scandi_err.log

# And then the same once more for the Arctic forecasts
python $basepath/plot_forecast_arome_arctic.py > $logpath/web_plot_no_arctic_out.log 2> $logpath/web_plot_no_arctic_err.log
python $basepath/web/render_vaerkart_arome_arctic.py > $logpath/web_render_no_arctic_out.log 2> $logpath/web_render_no_arctic_err.log

# Clean-up old plots
#find $basepath/web/plots -ctime +13 -delete
python cleanup.py

# the end

// Reload weather map when changing different properties

// Bind the arrow keys to functions
document.onkeydown = function(e) {
	e = e || window.event;
	_shifted = e.shiftKey;
	switch(e.which || e.keyCode) {
		case 16: // shift: do nothing, but prevent default
		break;

		case 37: // left
			prevtim();
		break;

		case 38: // up
			prevfc();
		break;

		case 39: // right
			nexttim();
		break;

		case 40: // down
			nextfc();
		break;

		default: return; // exit this handler for other keys
	}
	e.preventDefault(); // prevent the default action (scroll / move caret)
};
document.onkeyup = function(e) {
	e = e || window.event;
	_shifted = e.shiftKey;
	return;
}

// Get long variable / level names by plot by looking through varselect dropwdown list
function get_plotname_by_plot(plot) {
	var sel = document.getElementById('plotselect1');
	var opts = sel.childNodes;

	for (i=0; i <= opts.length; i++) {
		if (opts[i].value == plot) {
			return opts[i].childNodes[0].data;
		}
	}
	
	return 'Unknown plot.'
}

// Humanize the date: Takes a moment object and returns "%d %M %Y, %HZ"
function humanize(date) {
	return date.format('ddd, DD MMM YYYY, HH')+'Z';
}

// Filename from date: Takes a moment object and returns "%Y%M%d%H".
function filename(date) {
	return date.format('YYYYMMDDHH');
}

// moment-js string, a format directly feedable to moment.utc();
function momentfmt(date) {
	return date.format('YYYY-MM-DD HH');
}

// Create a new time / forecast title for panel i from date_vis and date_fc
function get_timtitle(i) {
	if ( lead_vis == 0 ) {
		return fcsrcs[fcsrc[i]]+' analysis for '+humanize(date_fc)
	}
	else {
		return fcsrcs[fcsrc[i]]+' forecast from '+humanize(date_fc)+' for '+humanize(date_vis)+' [+'+lead_vis+'h]';
	}
}

// Create filename based on current state
function get_current_filename(i) {
	return plotdir+'/'+fcsrc[i]+'_for_'+plot[i]+'_from_'+filename(date_fc)+'_for_'+filename(date_vis)+'.png';
}


// Change the forecasted date (lead time)
function chlead(newlead) {
	// Set new current valid time
	lead_vis = newlead;
	date_vis = moment(date_fc);
	date_vis.add(newlead, 'hours');
	
	document.cookie="date_vis="+momentfmt(date_vis);

	// Update map, heading
	for (i = 1; i <= 4; i++) {
		$('#map'+i).attr('src',get_current_filename(i));
		$('#fcstatus'+i ).text(get_timtitle(i));
	}
}

// Change the lead time for untrusted input
function chtim(newlead) {
	// Find closest available valid time using the new fc data
	if (_shifted || date_vis < avail_fcs[0]) {
		leads = avail_leads;
	}
	else {
		leads = cur_leads;
	}
	diff = 9999;
	for (i = 0; i <= leads.length; i++) {
		diff_ = Math.abs(newlead - leads[i]);
		if ( diff_ < diff ) {
			diff = diff_;
			lead_vis = leads[i];
		}
	}
	chlead(lead_vis);
}

// Involves custom check of equality of two dates, as indexOf and the-like use object-identity instead of equality
function date_array_contains(date, array) {
	for (j = 0; j <= array.length; j++) {
		date2 = moment(array[j]);
		if ( date2.diff(date) == 0 ) {
			return j
		}
	}
	return -1
}

// Change the forecast origin
function chfc(fcidx) {
	// Set new current forecast init time
	date_fc = avail_fcs[fcidx].clone();

	document.cookie = "date_fc="+momentfmt(date_fc);

	// Recreate available times
	cur_leads = [];
	for (i = 0; i < avail_leads.length; i++) {
		date = moment(date_fc).add(avail_leads[i], 'hours');
		if (date_array_contains(date, browse_tims) > -1) {
			cur_leads.push(avail_leads[i]);
			if ( $('#timselect_'+avail_leads[i].toString()).length > 0 ) {
				$('#timselect_'+avail_leads[i].toString()).removeClass('disabled');
			}
		}
		else if ( $('#timselect_'+avail_leads[i].toString()).length > 0) {
			$('#timselect_'+avail_leads[i].toString()).addClass('disabled');
		}
	}

	// Find closest available valid time using the new fc data
	if (date_vis < avail_fcs[0]) {
		leads = avail_leads;
	}
	else {
		leads = cur_leads;
	}
	diff = 9999;
	for (i = 0; i <= leads.length; i++) {
		date = moment(date_fc).add(leads[i], 'hours');
		diff_ = Math.abs(date_vis.diff(date, 'hours'));
		if ( diff_ < diff ) {
			diff = diff_;
			lead_vis = leads[i];
		}
	}
	chlead(lead_vis);

	// Update map, heading and drop-down box; remove focus from drop down box
	for (i = 1; i <= 4; i++) {
		$('#map'+i).attr('src',get_current_filename(i));
		$('#fcstatus'+i).text(get_timtitle(i));
	}
	$('#fcselect').val(fcidx).selectmenu("refresh");
}

// Change the forecast origin in archive mode
function chfctim_archive(forward) {
	// Set new current forecast init time
	if (forward) {
		timestep = archive_step;
	}
	else {
		timestep = -archive_step;
	}
	date_fc.add(timestep, 'hours');
	if (date_fc.isBefore(archive_start)) {
		date_fc = archive_start.clone();
	}
	date_vis = date_fc;

	document.cookie = "date_fc="+momentfmt(date_fc);

	// Recreate available times
	cur_leads = [];
	for (i = 0; i < avail_leads.length; i++) {
		$('#timselect_'+avail_leads[i].toString()).addClass('disabled');
	}

	// Update map, heading and drop-down box; remove focus from drop down box
	for (i = 1; i <= 4; i++) {
		$('#map'+i).attr('src',get_current_filename(i));
		$('#fcstatus'+i).text(get_timtitle(i));
	}
}

// Change the plot origin
function chplot(i, newplot) {
	// Set the new current variable and update plot details
	if ( display_details ) 
		$('#'+plot[i]+'_details'+i).css('display', 'none');
	plot[i] = newplot;
	if ( display_details ) 
		$('#'+plot[i]+'_details'+i).css('display', 'inline-block');
	
	document.cookie = "chart_plot"+i+"="+plot[i];

	prefix = fcsrc[i]+'_for_'+plot[i];

	// Update map, colorbar and heading
	$('#map'+i).attr('src', get_current_filename(i));
	$('#cbar'+i).attr('src', 'http://iveret.gfi.uib.no/static/deco/cbar_'+prefix+'.png');
	if ( units[prefix].length > 0 ) 
		$('#cbar_units'+i).text('['+units[prefix]+']');
	else 
		$('#cbar_units'+i).text('');
	//$('#plottitle').text(get_plotname_by_plot(newplot));

	// Remove focus from drop down to avoid changes due to arrow key strokes
	$('#plotselect'+i).blur();
}

// Change the forcast source for single or all panels
function chfcsrc(i, newfcsrc) {
	// Single panel
	if ( i > 0 ) {
		chfcsrc_single(i, newfcsrc);
	}
	else {
		for (i = 1; i <= 4; i++) {
			chfcsrc_single(i, newfcsrc);
		}
	}
}

// Change forecast source for single panel
function chfcsrc_single(i, newfcsrc) {
	// Update internal status
	fcsrc[i] = newfcsrc;
	document.cookie = "chart_fcsrc"+i+"="+fcsrc[i];
	
	// Update plot
	$('#map'+i).attr('src', get_current_filename(i));
	$('#fcstatus'+i).text(get_timtitle(i));

	// Update plot selection dropdown
	var menu = $( '#plotselect'+i );
	menu.empty();
	for (const [key, value] of Object.entries(plots[fcsrc[i]])) {
		if ( key == plot[i] ) {
			menu.append( '<option value="'+key+'" selected="selected">'+value+'</option>' );
		}
		else {
			menu.append( '<option value="'+key+'">'+value+'</option>' );
		}
	}
	menu.selectmenu("refresh");
}

function toggle_active(i) {
	// Deactivate currently active panel
	if ( i == _activepanel || i == false ) {
		$( '#map_container'+_activepanel ).css('box-shadow', 'none');
		_activepanel = false;
		$( '#scopeid' ).text('For all panels');

		if ( fcsrc[1] != fcsrc[2] || fcsrc[1] != fcsrc[3] || fcsrc[1] != fcsrc[4] ) {
			$('#fcsrcselect' ).val('__mixed__').selectmenu("refresh");
		}
	}
	else {
		$( '#map_container'+_activepanel ).css('box-shadow', 'none');
		$( '#map_container'+i ).css('box-shadow', '0px 0px 5px 5px grey');

		_activepanel = i;
		$( '#scopeid' ).text('For active panel');

		// Update fcsrc selector to relect the selected panel's state
		$('#fcsrcselect' ).val(fcsrc[i]).selectmenu("refresh");
	}
}

function toggle_details() {
	for (i = 1; i <= 4; i++) {
		if ( display_details ) {
			$('#'+fcsrc[i]+'_for_'+plot[i]+'_details'+i).css('display', 'none');
		}
		else {
			$('#'+fcsrc[i]+'_for_'+plot[i]+'_details'+i).css('display', 'inline-block');
		}
	}

	display_details = !display_details;
}

function toggle_maps_for_archive(archive_mode) {
	for (i = 1; i <= 4; i++) {
		options = $('#plotselect'+i+' option')
		for (j = 0; j < options.length; j++) {
			if (archive_mode & archive_plots.indexOf(options[j].value) < 0) {
				$(options[j]).attr("disabled", true);
			}
			else {
				$(options[j]).attr("disabled", false);
			}
		}
		$('#plotselect'+i).selectmenu("refresh");
	}
}

// Change to the next time step (increase lead time)
function nexttim() {
	if (_archive) {
		chfctim_archive(true);

		// Transition out of archive mode
		if (date_vis - avail_fcs[0] >= 0) {
			_archive = false;
			toggle_maps_for_archive(_archive);
			chfc(0);
		}
	}
	else {
		if (date_vis < avail_fcs[0]) {
			leads = avail_leads;
		}
		else {
			leads = cur_leads;
		}

		var idx = leads.indexOf(lead_vis);
		idx = Math.min(idx+1, leads.length-1);
		chlead(leads[idx]);
	}
}

// Change to the previous time step (decrease lead time), but restrict movement to past
function prevtim() {
	// Transition into archive mode
	if (archive_available && _shifted && date_fc.diff(avail_fcs[0]) == 0 && date_vis.diff(avail_fcs[0]) == 0) {
		_archive = true;
		toggle_maps_for_archive(_archive);
		chlead(0);
	}

	if (_archive) {
		chfctim_archive(false);
	}
	else {
		if (_shifted || date_vis < avail_fcs[0]) {
			leads = avail_leads;
		}
		else {
			leads = cur_leads;
		}

		var idx = leads.indexOf(lead_vis);
		idx = Math.max(idx-1, 0);
		chlead(leads[idx]);
	}
}

// Change to the next time step (increase lead time)
function nextfc() {
	if (_archive) {
		prevtim();
	}
	else {
		var idx = date_array_contains(date_fc, avail_fcs);
		idx = Math.min(idx+1, avail_fcs.length-1);
		chfc(idx);
	}
}

// Change to the next time step (increase lead time)
function prevfc() {
	if (_archive) {
		nexttim();
	}
	else {
		var idx = date_array_contains(date_fc, avail_fcs);
		idx = Math.max(idx-1, 0);
		chfc(idx);
	}
}

// From: http://www.quirksmode.org/js/cookies.html
function get_cookie(name) {
	var nameEQ = name + "=";
	var ca = document.cookie.split(';');
	for(var i=0;i < ca.length;i++) {
		var c = ca[i];
		while (c.charAt(0)==' ') c = c.substring(1,c.length);
		if (c.indexOf(nameEQ) == 0) return c.substring(nameEQ.length,c.length);
	}
	return null;
}

function chpanel(id) {
	cur_panels = id;
	document.cookie = 'panels='+id;

	if (id == 21 || id == 22) {
		$('#panel_top_left').css('width', '49.5%');
		$('#panel_bottom_left').css('width', '49.5%');
	}
	else {
		$('#panel_top_left').css('width', '100%');
		$('#panel_bottom_left').css('width', '100%');
	}
	$('#panel_top_right').css('width', '49.5%');
	$('#panel_bottom_right').css('width', '49.5%');

	if (id == 11) {
		$('#panel_top_right').css('display', 'none');
		$('#panel_bottom_left').css('display', 'none');
		$('#panel_bottom_right').css('display', 'none');
	}
	else if (id == 12) {
		$('#panel_top_right').css('display', 'none');
		$('#panel_bottom_left').css('display', 'inline-block');
		$('#panel_bottom_right').css('display', 'none');
	}
	else if (id == 21) {
		$('#panel_top_right').css('display', 'inline-block');
		$('#panel_bottom_left').css('display', 'none');
		$('#panel_bottom_right').css('display', 'none');
	}
	else if (id == 22) {
		$('#panel_top_right').css('display', 'inline-block');
		$('#panel_bottom_left').css('display', 'inline-block');
		$('#panel_bottom_right').css('display', 'inline-block');
	}
}

function view_help() {
	$('#help_modal').dialog('open');	
}


// Startup definitions
$( document ).ready(function() {
	$( '#domainselect' ).selectmenu({
		change: function( event, ui ) {
			window.location.replace(ui.item.value);
		}
	}).selectmenu( "option", "width", 250 );

	$( '#fcsrcselect' ).selectmenu({
		change: function( event, ui ) {
			chfcsrc(_activepanel, ui.item.value);
		}
	}).selectmenu( "option", "width", 180 );
	
	for (i = 1; i <= 4; i++) {
		//$( '#map_container'+i ).mouseenter(function() {
		//	$('#time_controls').stop(true);
		//	$('#time_controls').slideDown(200).delay(2000).slideUp(500);
		//});
		//$( '#map_container'+i ).mouseleave(function() {
		//	$('#time_controls').stop(true);
		//	$('#time_controls').slideUp(200);
		//});

		$( '#plotselect'+i ).selectmenu({
			change: function( event, ui ) {
				id = parseInt(event.target.id.slice(-1));
				chplot(id, ui.item.value);
			}
		}).selectmenu( "option", "width", 550 );
	}

	$( '#fc_older' ).datepicker({
		changeMonth: true, changeYear: true
	});

	$( '#panelselect' ).selectmenu({
		change: function( event, ui ) {
			chpanel(ui.item.value);
		}
	}).selectmenu( "option", "width", 150 );

	// Take into account saved state when switching between forecast areas
	for (i = 1; i <= 4; i++) {
		_fcsrc = get_cookie('chart_fcsrc'+i);
		_plot = get_cookie('chart_plot'+i);
		if (_fcsrc in plots) {
			fcsrc[i] = _fcsrc;
			chfcsrc(i, fcsrc[i]);

			if (_plot in plots[_fcsrc]) {
				plot[i] = _plot;
				chplot(i, plot[i]);
				$('#plotselect'+i).val(plot[i]).selectmenu("refresh");
			}
			else {
				document.cookie = 'chart_plot'+i+'='+plot[i];
			}

			$( '#plot'+i ).click( function( event, ui) { 
				id = parseInt(event.target.id.slice(-1));
				toggle_active(id);
				event.stopPropagation();
			});
		}
		else {
			chfcsrc(i, fcsrc[i]);
			document.cookie = 'chart_fcsrc'+i+'='+fcsrc[i];
		}
	}
	// Deselect active plot by clicking on body
	$( '.content' ).click( function ( event, ui ) {
		toggle_active( false );
	});

	_date_fc = moment.utc(get_cookie('date_fc'));
	_date_vis = moment.utc(get_cookie('date_vis'));
	_panels = get_cookie('panels');
	if (_panels != null) {
		chpanel(_panels);
		$('#panelselect').val(_panels).selectmenu("refresh");
	}
	if (_date_fc != null) {
		idx = date_array_contains(_date_fc, avail_fcs);
		if (idx > -1) {
			if (_date_vis != null) {
				date_vis = _date_vis;
			}
			chfc(idx);
		}
	}
	else {
		document.cookie = 'date_fc='+momentfmt(date_fc);
	}

	$( "#help_modal" ).dialog({
		modal: true,
		autoOpen: false,
		buttons: {
			Close: function() {
				$( this ).dialog( "close" );
			}
		}
	});
});

// the end

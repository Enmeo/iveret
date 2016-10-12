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

// Get long variable / level names by prefix by looking through varselect dropwdown list
function get_varname_by_prefix(prefix) {
	var sel = document.getElementById('varselect');
	var opts = sel.childNodes;

	for (i=0; i <= opts.length; i++) {
		if (opts[i].value == prefix) {
			return opts[i].childNodes[0].data;
		}
	}
	
	return 'Unknown prefix.'
}

// Humanize the date: Takes a moment object and returns "%d %M %Y, %H UTC"
function humanize(date) {
	return date.format('dddd, DD MMM YYYY, HH')+' UTC';
}

// Filename from date: Takes a moment object and returns "%Y%M%d%H".
function filename(date) {
	return date.format('YYYYMMDDHH');
}

// moment-js string, a format directly feedable to moment.utc();
function momentfmt(date) {
	return date.format('YYYY-MM-DD HH');
}

// Create a new time / forecast title from date_vis and date_fc
function get_timtitle() {
	return 'Forecast from '+humanize(date_fc)+' for '+humanize(date_vis)+' [+'+lead_vis+'h]';
}

// Create filename based on current state
function get_current_filename() {
	return './'+plotdir+'/'+plot_prefix+'_'+prefix+'_from_'+filename(date_fc)+'_for_'+filename(date_vis)+'.png';
}


// Change the forecasted date (lead time)
function chlead(newlead) {
	// Set new current valid time
	lead_vis = newlead;
	date_vis = moment(date_fc);
	date_vis.add(newlead, 'hours');
	
	document.cookie="date_vis="+momentfmt(date_vis);

	// Update map, heading
	$('#map').attr('src',get_current_filename());
	$('#timtitle').text(get_timtitle());
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
	date_fc = avail_fcs[fcidx];

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
	$('#map').attr('src',get_current_filename());
	$('#timtitle').text(get_timtitle());
	$('#fcselect').val(fcidx).selectmenu("refresh");
}

// Change the forecast origin
function chvar(newvar) {
	// Set the new current variable and update plot details
	if ( display_details ) 
		$('#'+prefix+'_details').css('display', 'none');
	prefix = newvar;
	if ( display_details ) 
		$('#'+prefix+'_details').css('display', 'block');

	document.cookie = "chart_prefix="+prefix

	// Update map, colorbar and heading
	$('#map').attr('src', get_current_filename());
	$('#cbar').attr('src', './static/deco/cbar_'+plot_prefix+'_'+prefix+'.png');
	if ( units[prefix].length > 0 ) 
		$('#cbar_units').text('['+units[prefix]+']');
	else 
		$('#cbar_units').text('');
	//$('#vartitle').text(get_varname_by_prefix(newvar));

	// Remove focus from drop down to avoid changes due to arrow key strokes
	$('#varselect').blur();
}

function toggle_details() {
	if ( display_details ) {
		$('#'+prefix+'_details').css('display', 'none');
		display_details = false;
	}
	else {
		$('#'+prefix+'_details').css('display', 'block');
		display_details = true;
	}
}

// Change to the next time step (increase lead time)
function nexttim() {
	clear_timeouts(); 

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

// Change to the previous time step (decrease lead time), but restrict movement to past
function prevtim() {
	clear_timeouts();

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

// Skip back to first time step
function firsttim() {
	clear_timeouts();

	chlead(cur_leads[0]);
}

// Change to the next time step (increase lead time)
function nextfc() {
	clear_timeouts();

	var idx = avail_fcs.indexOf(date_fc);
	idx = Math.min(idx+1, avail_fcs.length-1);
	chfc(idx);
}

// Change to the next time step (increase lead time)
function prevfc() {
	clear_timeouts();

	var idx = avail_fcs.indexOf(date_fc);
	idx = Math.max(idx-1, 0);
	chfc(idx);
}

function play() {
	//console.log($('#play')); //.css('display'));
	// Toggle which buttons to display
	$('#but_play').css('display', 'none');
	$('#but_pause').css('display', 'inline-block');

	var idx = cur_leads.indexOf(lead_vis);
	var maxidx = cur_leads.length-1;
	
	for (i=idx+1; i <= maxidx; i++) {
		set_timeout(i, idx);
	}
}
function pause() {
	clear_timeouts()

	// Toggle which buttons to display
	$('#but_play').css('display', 'inline-block');
	$('#but_pause').css('display', 'none');
}

// Set timeout for the play function (needs to be separate, because javascript is stupid)
function set_timeout(i, idx) {
	setTimeout(function() {
		chlead(cur_leads[i]);
	}, (i-idx-1)*500+50);
}

// Clear all timeouts set in play.
function clear_timeouts() {
	var id = window.setTimeout(function() {}, 0);

	while (id--) {
		window.clearTimeout(id); 
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


// Startup definitions
$( document ).ready(function() {
	// Initial display: play controls
	$('#time_controls').delay(3000).slideUp(1000);
	
	// Define hide/show behaviour of play controls
	$( '#time_controls' ).mouseenter(function() {
		$('#time_controls').stop(true);
		$('#time_controls').slideDown(100);
	});
	$( '#time_controls' ).mouseleave(function() {
		$('#time_controls').delay(2000).slideUp(500);
	});
	$( '#map_container' ).mouseenter(function() {
		$('#time_controls').stop(true);
		$('#time_controls').slideDown(200).delay(2000).slideUp(500);
	});
	$( '#map_container' ).mouseleave(function() {
		$('#time_controls').stop(true);
		$('#time_controls').slideUp(200);
	});

	$( '#domainselect' ).selectmenu({
		change: function( event, ui ) {
			window.location.replace(ui.item.value);
		}
	}).selectmenu( "option", "width", 320 );
	$( '#fcselect' ).selectmenu({
		change: function( event, ui ) {
			chfc(ui.item.value);
		}
	}).selectmenu( "option", "width", 320 );

	$( '#varselect' ).selectmenu({
		change: function( event, ui ) {
			chvar(ui.item.value);
		}
	}).selectmenu( "option", "width", 550 );

	$( '#fc_older' ).datepicker({
		changeMonth: true, changeYear: true
	});

	// Take into account saved state
	_prefix = get_cookie('chart_prefix');
	_date_fc = moment.utc(get_cookie('date_fc'));
	_date_vis = moment.utc(get_cookie('date_vis'));
	if (_prefix in units) {
		prefix = _prefix;
		chvar(prefix);
		$('#varselect').val(prefix).selectmenu("refresh");
	}
	else {
		document.cookie = 'chart_prefix='+prefix;
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
});

// the end

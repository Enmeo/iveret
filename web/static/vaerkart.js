// Reload weather map when changing different properties

// Bind the arrow keys to functions
document.onkeydown = function(e) {
	e = e || window.event;
	switch(e.which || e.keyCode) {
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

// Humanize the date: Takes a string "%Y%m%d%H" and returns "%d %M %Y, %H UTC"
function humanize_datetime(datestr) {
	return datestr.substr(6,2)+' '+datestr.substr(4,2).replace('01','Jan').replace('02', 'Feb').replace('03', 'Mar').replace('04', 'Apr').replace('05', 'May').replace('06', 'Jun').replace('07', 'Jul').replace('08', 'Aug').replace('09', 'Sep').replace('10', 'Oct').replace('11', 'Nov').replace('12', 'Dec')+' '+datestr.substr(0,4)+', '+datestr.substr(8,2)+' UTC'
}

// Create a new time / forecast title from date_vis and date_fc
function get_timtitle() {
	return 'Forecast from '+humanize_datetime(date_fc)+' for '+humanize_datetime(date_vis);
}


// Change the forecasted date (lead time)
function chtim(newtim) {
	var map = document.getElementById('map');

	date_vis = newtim;
	map.src = './'+plotdir+'/ec_for_'+prefix+'_from_'+date_fc+'_for_'+date_vis+'.png';

	var heading = document.getElementById('timtitle');
	heading.childNodes[0].data = get_timtitle();
}

// Change the forecast origin
function chfc(newfc) {
	// Update map
	var map = document.getElementById('map');
	date_fc = newfc;
	map.src = './'+plotdir+'/ec_for_'+prefix+'_from_'+date_fc+'_for_'+date_vis+'.png';
	
	// Update heading
	var heading = document.getElementById('timtitle');
	heading.childNodes[0].data = get_timtitle();
	
	// Update drop down box
	var sel = document.getElementById('fcselect');
	var opts = sel.childNodes;

	for (i=0; i <= opts.length; i++) {
		if (opts[i].value == newfc) {
			return opts[i].selected='selected';
		}
	}
	
	return 'Unknown prefix.'
}

// Change the forecast origin
function chvar(newvar) {
	$('#map').attr('src', './'+plotdir+'/ec_for_'+prefix+'_from_'+date_fc+'_for_'+date_vis+'.png');
	$('#cbar').attr('src', './static/info/'+prefix+'_cbar.png');

	var heading = document.getElementById('vartitle');
	heading.childNodes[0].data = get_varname_by_prefix(newvar);
}

// Change to the next time step (increase lead time)
function nexttim(){
	clear_timeouts(); 

	var idx = avail_tims.indexOf(date_vis);
	idx = Math.min(idx+1, avail_tims.length-1);
	chtim(avail_tims[idx]);
}

// Change to the next time step (increase lead time)
function prevtim(){
	clear_timeouts();

	var idx = avail_tims.indexOf(date_vis);
	idx = Math.max(idx-1, 0);
	chtim(avail_tims[idx]);
}

// Skip back to first time step
function firsttim(){
	clear_timeouts();

	chtim(avail_tims[0]);
}

// Change to the next time step (increase lead time)
function nextfc(){
	clear_timeouts();

	var idx = avail_fcs.indexOf(date_fc);
	idx = Math.min(idx+1, avail_fcs.length-1);
	chfc(avail_fcs[idx]);
}

// Change to the next time step (increase lead time)
function prevfc(){
	clear_timeouts();

	var idx = avail_fcs.indexOf(date_fc);
	idx = Math.max(idx-1, 0);
	chfc(avail_fcs[idx]);
}

function play(){
	//console.log($('#play')); //.css('display'));
	// Toggle which buttons to display
	$('#but_play').css('display', 'none');
	$('#but_pause').css('display', 'inline-block');

	var idx = avail_tims.indexOf(date_vis);
	var maxidx = avail_tims.length-1;
	
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
		chtim(avail_tims[i]);
	}, (i-idx-1)*500+50);
}

// Clear all timeouts set in play.
function clear_timeouts() {
	var id = window.setTimeout(function() {}, 0);

	while (id--) {
	    window.clearTimeout(id); 
	}
}


// the end

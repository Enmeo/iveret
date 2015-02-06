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
	var map = document.getElementById('map');

	prefix = newvar;
	map.src = './'+plotdir+'/ec_for_'+prefix+'_from_'+date_fc+'_for_'+date_vis+'.png';

	var heading = document.getElementById('vartitle');
	heading.childNodes[0].data = get_varname_by_prefix(newvar);
}

// Change to the next time step (increase lead time)
function nexttim(){
	var idx = avail_tims.indexOf(date_vis);
	idx = Math.min(idx+1, avail_tims.length-1);
	chtim(avail_tims[idx]);
}

// Change to the next time step (increase lead time)
function prevtim(){
	var idx = avail_tims.indexOf(date_vis);
	idx = Math.max(idx-1, 0);
	chtim(avail_tims[idx]);
}

// Change to the next time step (increase lead time)
function nextfc(){
	var idx = avail_fcs.indexOf(date_fc);
	idx = Math.min(idx+1, avail_fcs.length-1);
	chfc(avail_fcs[idx]);
}

// Change to the next time step (increase lead time)
function prevfc(){
	var idx = avail_fcs.indexOf(date_fc);
	idx = Math.max(idx-1, 0);
	chfc(avail_fcs[idx]);
}


// the end

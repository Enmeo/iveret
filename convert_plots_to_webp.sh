#!/bin/bash
#
# One-time migration of existing plots to the new plot format (B9, B10)
#
# Plots made before the switch are PNG files without colour bar; the colour
# bars were shown next to them from separately extracted images in
# static/deco (see extract_decorations.sh). This script appends the matching
# colour bar to the right of each existing PNG plot and writes the result as
# WebP next to it, so old plots (the retained 10/40-day runs and the
# permanent archive) follow the same format and URL scheme as new plots.
#
# The colour bar for a plot is looked up with the same rules the old web
# pages used (templates/static/vaerkart.js, chvar()):
#   natl, snorway:          cbar_<fcsrc>_for_<plot>.png
#   scandes (except ec):    cbar_<fcsrc>_for_full_<plot>.png
#   all other domains:      cbar_<fcsrc>_for_<domain>_<plot>.png
# plus a few older domain names found in static/deco (barents -> arctic,
# scandes -> scandies) as fallbacks. If the colour bar does not have the
# same height as the plot, it is scaled to the plot height.
#
# Meteograms have no colour bar and stay PNG. Plots for which no colour bar
# is found are left untouched (reported as MISSING), unless -m is given.
#
# The script is idempotent: plots that already have a WebP counterpart are
# skipped, so it can be run while the pipelines are already writing WebP,
# and it can be re-run after adding missing colour bars.
#
# Usage: convert_plots_to_webp.sh [options] [PLOTDIR]
#
#   PLOTDIR     Plot root, default /share/web/plots
#   -c DIR      Directory with the cbar_*.png files; can be given several
#               times, searched in order. Default /share/web/static/deco
#   -j N        Number of parallel convert processes, default 4
#   -n          Dry run: only report what would be done
#   -d          Delete the PNG after a successful conversion (and PNGs whose
#               WebP counterpart already exists). Default: keep the PNGs.
#   -m          Convert plots without a matching colour bar as they are
#   -l FILE     Log file, default ./convert_plots_to_webp.<timestamp>.log
#   -h          Show this help
#
# Requires ImageMagick 6 (convert, identify) with WebP support.

set -u

PLOTDIR="/share/web/plots"
DECODIRS=()
JOBS=4
DRYRUN=0
DELETE=0
NOCBAR_OK=0
LOGFILE="./convert_plots_to_webp.$(date +%Y%m%d%H%M%S).log"

# Keep in sync with WEBP_QUALITY in settings/common2.py
WEBP_QUALITY=90

usage() {
	sed -n '/^# Usage:/,/^# Requires/p' "$0" | sed 's/^# \{0,1\}//'
	exit "${1:-0}"
}

while getopts "c:j:ndml:h" opt; do
	case "$opt" in
		c) DECODIRS+=("${OPTARG%/}") ;;
		j) JOBS="$OPTARG" ;;
		n) DRYRUN=1 ;;
		d) DELETE=1 ;;
		m) NOCBAR_OK=1 ;;
		l) LOGFILE="$OPTARG" ;;
		h) usage 0 ;;
		*) usage 1 ;;
	esac
done
shift $((OPTIND-1))
[ $# -gt 1 ] && usage 1
[ $# -eq 1 ] && PLOTDIR="${1%/}"
[ ${#DECODIRS[@]} -eq 0 ] && DECODIRS=("/share/web/static/deco")

if ! command -v convert >/dev/null || ! command -v identify >/dev/null; then
	echo "ImageMagick (convert, identify) not found." >&2
	exit 1
fi
if ! convert -list format 2>/dev/null | grep -qi '^ *WEBP.*rw'; then
	echo "This ImageMagick cannot write WebP." >&2
	exit 1
fi
if [ ! -d "$PLOTDIR" ]; then
	echo "Plot directory $PLOTDIR does not exist." >&2
	exit 1
fi
for d in "${DECODIRS[@]}"; do
	[ -d "$d" ] || { echo "Colour bar directory $d does not exist." >&2; exit 1; }
done


# Print the candidate colour bar file names for domain, plot, fcsrc
cbar_candidates() {
	local domain="$1" plot="$2" fcsrc="$3"
	case "$domain" in
		natl|snorway)
			echo "cbar_${fcsrc}_for_${plot}.png" ;;
		scandes)
			if [ "$fcsrc" != "ec" ]; then
				echo "cbar_${fcsrc}_for_full_${plot}.png"
			fi
			echo "cbar_${fcsrc}_for_scandes_${plot}.png"
			echo "cbar_${fcsrc}_for_scandies_${plot}.png" ;;
		barents)
			echo "cbar_${fcsrc}_for_barents_${plot}.png"
			echo "cbar_${fcsrc}_for_arctic_${plot}.png" ;;
		*)
			echo "cbar_${fcsrc}_for_${domain}_${plot}.png" ;;
	esac
}

# Find the colour bar file; prints its path, or nothing
find_cbar() {
	local name d
	for name in $(cbar_candidates "$@"); do
		for d in "${DECODIRS_STR[@]}"; do
			if [ -f "$d/$name" ]; then
				echo "$d/$name"
				return 0
			fi
		done
	done
	return 1
}

# Convert a batch of plots; output lines:  STATUS domain/plot/fcsrc file [detail]
convert_batch() {
	local -A cbar_height
	local f rel domain plot fcsrc fname out tmp cbar h ch
	IFS=':' read -r -a DECODIRS_STR <<< "$DECODIRS_JOINED"

	for f in "$@"; do
		rel="${f#"$PLOTDIR"/}"
		IFS='/' read -r domain plot fcsrc fname <<< "$rel"
		key="$domain/$plot/$fcsrc"
		out="${f%.png}.webp"

		if [ "$domain" == "meteograms" ]; then
			echo "NOCBAR $key $f meteogram, stays PNG"
			continue
		fi

		if [ -e "$out" ]; then
			if [ "$DELETE" -eq 1 ] && [ "$DRYRUN" -eq 0 ] && [ -s "$out" ]; then
				rm -f -- "$f"
				echo "SKIP $key $f WebP exists, PNG deleted"
			else
				echo "SKIP $key $f WebP exists"
			fi
			continue
		fi

		cbar="$(find_cbar "$domain" "$plot" "$fcsrc")"
		if [ -z "$cbar" ] && [ "$NOCBAR_OK" -eq 0 ]; then
			echo "MISSING $key $f tried: $(cbar_candidates "$domain" "$plot" "$fcsrc" | tr '\n' ' ')"
			continue
		fi

		if [ "$DRYRUN" -eq 1 ]; then
			echo "OK $key $f would use ${cbar:-no colour bar}"
			continue
		fi

		tmp="${out}.tmp"
		if [ -n "$cbar" ]; then
			h="$(identify -format '%h' "$f" 2>/dev/null)"
			if [ -z "${cbar_height[$cbar]+x}" ]; then
				cbar_height[$cbar]="$(identify -format '%h' "$cbar" 2>/dev/null)"
			fi
			ch="${cbar_height[$cbar]}"
			if [ -z "$h" ] || [ -z "$ch" ]; then
				echo "FAIL $key $f cannot read image size"
				continue
			fi
			if [ "$h" == "$ch" ]; then
				convert "$f" "$cbar" -background white -gravity center +append \
					-quality "$WEBP_QUALITY" -define webp:method=4 "webp:$tmp"
			else
				convert "$f" \( "$cbar" -resize "x${h}" \) -background white -gravity center +append \
					-quality "$WEBP_QUALITY" -define webp:method=4 "webp:$tmp"
			fi
		else
			convert "$f" -quality "$WEBP_QUALITY" -define webp:method=4 "webp:$tmp"
		fi

		if [ $? -eq 0 ] && [ -s "$tmp" ]; then
			touch -r "$f" "$tmp"
			mv -f -- "$tmp" "$out"
			if [ "$DELETE" -eq 1 ]; then
				rm -f -- "$f"
			fi
			if [ -z "$cbar" ]; then
				echo "OK $key $f without colour bar"
			elif [ "$h" == "$ch" ]; then
				echo "OK $key $f $(basename "$cbar")"
			else
				echo "OK $key $f $(basename "$cbar") scaled from height $ch to $h"
			fi
		else
			rm -f -- "$tmp"
			echo "FAIL $key $f convert failed"
		fi
	done
}

# Arrays cannot be exported; pass the colour bar directories as a string
DECODIRS_JOINED="$(IFS=':'; echo "${DECODIRS[*]}")"
export PLOTDIR DECODIRS_JOINED DRYRUN DELETE NOCBAR_OK WEBP_QUALITY
export -f cbar_candidates find_cbar convert_batch

echo "Converting PNG plots in $PLOTDIR, colour bars from ${DECODIRS[*]}, $JOBS processes."
[ "$DRYRUN" -eq 1 ] && echo "Dry run, nothing is written."
echo "Log: $LOGFILE"

# Plots are <PLOTDIR>/<domain>/<plot>/<fcsrc>/<init>_for_<valid>.png
find "$PLOTDIR" -mindepth 4 -maxdepth 4 -type f -name '*_for_*.png' -print0 \
	| xargs -0 -r -n 100 -P "$JOBS" bash -c 'convert_batch "$@"' _ \
	> "$LOGFILE"

# Summary
echo
for status in OK SKIP NOCBAR MISSING FAIL; do
	printf '%-8s %8d\n' "$status" "$(grep -c "^$status " "$LOGFILE")"
done

if grep -q '^MISSING ' "$LOGFILE"; then
	echo
	echo "No colour bar found for (files: domain/plot/fcsrc):"
	grep '^MISSING ' "$LOGFILE" | awk '{print $2}' | sort | uniq -c
fi
if grep -q '^FAIL ' "$LOGFILE"; then
	echo
	echo "Failed conversions are listed in $LOGFILE."
	exit 2
fi

# the end

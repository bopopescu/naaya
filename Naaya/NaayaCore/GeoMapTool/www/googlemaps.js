/**
 * class GGeoMapTool
 * Description: Wrapper class around the Google Maps implementation.
 */

function GGeoMapTool() {
	this.description = "GeoMap Tool implementation wrapper for Yahoo maps";
	this.geocoder = null;
	this.markerHash = {};
}


/**
 * Create a marker to be displayed on the map with given attributes.
 * @param lat Geographical latitude
 * @param lng Geographical longitude
 * @param html HTML text that appears in the body of the tooltip ballon
 * @param title Title that appears in the tooltip baloon (like title HTML tag)
 * @param icon Icon symbol for the marker
 * @return Initialized marker
 */
GGeoMapTool.prototype.createMarker = function(lat, lng, html, title, icon) {
	var p = new GLatLng(lat, lng);
    var marker = new GMarker(p, {title:title, icon:icon});
    GEvent.addListener(marker, "click", function() {
      marker.openInfoWindowHtml(html);
    });
    return marker;
}


/**
 * Clear all the markers (and elements) from the map.
 */
GGeoMapTool.prototype.clearMap = function() {
	map.clearOverlays();
}


/**
 * Create a new symbol (icon) to be displayed for markers.
 * @param imageURL URL for the image icon
 * @return an initialized icon symbol.
 */
GGeoMapTool.prototype.createIconSymbol = function(imageURL) {
	var icon = new GIcon(G_DEFAULT_ICON);
	icon.image = imageURL;
	icon.iconSize = new GSize(17, 17);
	icon.iconAnchor = new GPoint(1, 25);
	icon.shadow = "misc_/NaayaCore/shadow.png";
	icon.shadowSize = new GSize(26, 17);
	icon.infoWindowAnchor = new GPoint(5, 1);
	return icon;
}


/**
 * Add a new marker on the map.
 * @param marker Marker to be added on map (created with createMarker)
 */
GGeoMapTool.prototype.addMarkerOnMap = function(marker) {
	map.addOverlay(marker);
}


/**
 * Initialize (if required) and retrieve the geocoder object.
 * @return Geocoder object initialized
 */
GGeoMapTool.prototype.getGeocoder = function() {
	if(!this.geocoder) {
		this.geocoder = new GClientGeocoder();
	}
	return this.geocoder;
}


/**
 * Initialize and display the map in the page.
 * @param center A location (address type) to center the map on,
 * ex.: Frankfurt, Germany
 * @param zoom Zoom factor for the map
 * @param enableScrollWheelZoom Enable/Disable zooming using mouse scroll wheel
 * and keyboard controls
 * @param map_types An array of map types available for the map.
 * Possible values in array: {"hybrid", "map", satellite"}
 */
GGeoMapTool.prototype.showMap = function(center, zoom, enableScrollWheelZoom, map_types, initial_map_type) {
	var arrLayers = [];
	for( i = 0; i < map_types.length; i++) {
		if( "hybrid" == map_types[ i ] ) { arrLayers[arrLayers.length] = G_HYBRID_MAP; }
		if( "map" == map_types[ i ] ) { arrLayers[arrLayers.length] = G_NORMAL_MAP; }
		if( "satellite" == map_types[ i ] ) { arrLayers[arrLayers.length] = G_SATELLITE_MAP; }
	}
	map = new GMap2(document.getElementById("map"), {mapTypes:arrLayers});
	mapNavCtrl = new GSmallMapControl();
	map.addControl( mapNavCtrl )
	if( arrLayers.length > 1 ) {
		mapTypeCtrl = new GMenuMapTypeControl();
		map.addControl( mapTypeCtrl )
	}
	init_type = G_NORMAL_MAP;
	if( "hybrid" == initial_map_type ) { init_type = G_HYBRID_MAP; }
	if( "satellite" == initial_map_type ) { init_type = G_SATELLITE_MAP; }
	map.setMapType( init_type );
	var coord = this.getGeocoder().getLatLng(center, function(point) {
		if(!point) {
			map.setCenter(new GLatLng(45.4419, 1.1419), zoom);
		} else {
			map.setCenter(point, zoom);
		}
	});
	if(enableScrollWheelZoom) {
		map.enableScrollWheelZoom();
	}
}

GGeoMapTool.prototype.showMapLocations = function(){
	GEvent.addListener(map, 'load', showMapLocationsHandler);
}

GGeoMapTool.prototype.drawZoomAndCenter = function(center){
	var coord = this.getGeocoder().getLatLng(center, function(point) {
		if(point) {
			map.setCenter(point, 12);
		}
	});
}

/**
 * Load category from server doing an XMLHTTPRequest to retrieve the points.
 */
GGeoMapTool.prototype.showCategoryServer = function(idCategory, show)
{
	var category = 'mk_' + idCategory;
	// Look first into the cache to see if we didn't already loaded the
	// points for this category
	if( show && this.markerHash[ category ] == null ) {
		// Cache miss, load points from server
		document.body.style.cursor = "wait";
		doHttpRequest( server_base_url + "/xrjs_getGeoPoints?geo_types%3Alist=" + idCategory, httpDocumentHandler);
	} else {
		// We have a cache hit, show them
		this.showCategory(idCategory);
	}
}


/**
 * Show a category, client side. Assumes that markers for this category are
 * already loaded on the client side and are taken directly from marker cache.
 */
GGeoMapTool.prototype.showCategory = function(idCategory)
{
	var category = 'mk_' + idCategory;
	if( this.markerHash[ category ] != null ) {
		markerArr = this.markerHash[ category ];
		for( i = 0; i < markerArr.length; i++ ) {
			var marker = markerArr[ i ];
			if( marker.isHidden() )
			{
				marker.show();
			}
			else
			{
				marker.hide();
			}
		}
	}
	this.updateRecordCounter();
}

GGeoMapTool.prototype.updateRecordCounter = function () {
	counter = 0;
	for( key in mapTool.markerHash) {
		var markerArr = mapTool.markerHash[ key ];
		for( i = 0; i < markerArr.length; i++ ) {
			var marker = markerArr[ i ];
			if( !marker.isHidden() ) counter++;
		}
	}
	setRecordCounter( counter );
}




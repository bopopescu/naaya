/**
 * Here we define the settings required for the GeoMapTool. This template is
 * loaded via GeoMapTool.py and their values replaced with settings from 
 * the Configuration of GeoMapTool.  
 */

/**
 * Defines the map engine currently in use. Possible values are "google", "yahoo"
 */
var map_engine = "%s"
var symbolImageURLPairArray = {%s};
var center_address = "%s";
var initial_zoom = %s;
var enableScrollZoom = %s;
var map_types = %s;
var initial_map_type = "%s";

var symbolIcons = new Array();
var map = null;
var mapTool = null;


/**
 * Show on map selected types of locations.
 * Map engine independent.
 * @return Nothing
 */
function showMapLocations() {
	checkConfig( "showMapLocations" );
	mapTool.clearMap();
	document.body.style.cursor = "wait";
	doHttpRequest( "%s/xrjs_getGeoPoints?" + encodeForm("frmFilterMap"), httpDocumentHandler);
}

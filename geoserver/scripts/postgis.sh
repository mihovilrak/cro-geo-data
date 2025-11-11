curl -X POST "${GEOSERVER_URL}/geoserver/rest/workspaces/cro-geo-data/datastores" \
-H  "accept: text/html" \
-H  "content-type: application/json" \
-d @json/postgis.json
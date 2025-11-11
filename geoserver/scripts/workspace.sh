curl -X POST "${GEOSERVER_URL}/geoserver/rest/workspaces?default=true" \
-H  "accept: text/html" \
-H  "content-type: application/json" \
-d @json/workspace.json
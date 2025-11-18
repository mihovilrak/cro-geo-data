tables_exist() {
    PGPASSWORD=${DB_PASSWORD} \
    psql -U ${DB_USER} -d ${DB_NAME} -h ${DB_HOST} -p ${DB_PORT} \
        -tAf table_check.sql 2>/dev/null | grep -q "^t$"
}

post_request() {
    curl -X POST -u ${GEOSERVER_USER}:${GEOSERVER_PASSWORD} \
    "${GEOSERVER_URL}/geoserver/rest/${1}" \
    -H  "accept: text/html" \
    -H  "content-type: application/json" \
    -d ${2}
}

post_sld() {
    curl -X POST -u ${GEOSERVER_USER}:${GEOSERVER_PASSWORD} \
    "${GEOSERVER_URL}/geoserver/rest/styles" \
    -H  "accept: text/plain" \
    -H  "content-type: application/vnd.ogc.sld+xml" \
    -H  "Content-Type: SLD" \
    -d @sld/${1}
}

get_native_bbox() {
    bbox = $(
        PGPASSWORD=${DB_PASSWORD} \
        psql -U ${DB_USER} -d ${DB_NAME} -h ${DB_HOST} -p ${DB_PORT} \
        -tA -c "SELECT gs.get_native_bbox('${1}')" 2>/dev/null)
    IFS='|' read -r xmin xmax ymin ymax <<< "$bbox"
    echo sed 's/"XMIN"/${xmin}/g' ${1} \
    | sed 's/"XMAX"/${xmax}/g' \
    | sed 's/"YMIN"/${ymin}/g' \
    | sed 's/"YMAX"/${ymax}/g'
}

ws = "workspaces"
ds = "${ws}/cro-geo-data/datastores"
ft = "${ds}/postgis/featuretypes"

requests = ("${ws}?default=true|json/workspace.json" \
"${ds}|json/postgis.json" \
"${ft}/addresses|json/addresses.json" \
"${ft}/postal_offices|json/postal_offices.json" \
"${ft}/streets|json/streets.json" \
"${ft}/municipalities|json/municipalities.json" \
"${ft}/settlements|json/settlements.json" \
"${ft}/counties|json/counties.json" \
"${ft}/country|json/country.json" \
"${ft}/cadastral_municipalities|json/cadastral_municipalities.json" \
"${ft}/cadastral_parcels|json/cadastral_parcels.json" \
"${ft}/buildings|json/buildings.json")

slds = ("house_numbers.sld" "parcels.sld")

while ! tables_exist; do
    echo "Waiting for tables to be created..."
    sleep 5
done

echo "Tables exist, continuing with GeoServer initialization..."

for request in "${requests[@]}"; do
    IFS='|' read -r request_url request_file <<< "$request"
    if [ "$request_file" = "json/postgis.json" ]; then
        post_request "$request_url" "$(sed 's/DB_NAME/${DB_NAME}/g' ${request_file} \
        | sed 's/DB_HOST/${DB_HOST}/g' \
        | sed 's/DB_PORT/${DB_PORT}/g' \
        | sed 's/DB_USER/${DB_USER}/g' \
        | sed 's/DB_PASSWORD/${DB_PASSWORD}/g')"
    else
        post_request "$request_url" "$(get_native_bbox ${request_file})"
    fi
done

for sld in "${slds[@]}"; do
    post_sld "$sld"
done
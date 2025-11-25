#!/bin/bash
set -euo pipefail

DB_HOST=${DB_HOST:-db}
DB_PORT=${DB_PORT:-5432}
DB_NAME=${DB_NAME:-gis}
DB_USER=${DB_USER:-postgres}
DB_PASSWORD=${DB_PASSWORD:-postgres}

GEOSERVER_URL=${GEOSERVER_URL:-http://geoserver:8080/geoserver}
GEOSERVER_USER=${GEOSERVER_USER:-admin}
GEOSERVER_PASSWORD=${GEOSERVER_PASSWORD:-geoserver}
GEOSERVER_WORKSPACE=${GEOSERVER_WORKSPACE:-cro-geo-data}
GEOSERVER_DATASTORE="workspaces/${GEOSERVER_WORKSPACE}/datastores"
GEOSERVER_FEATURE_TYPES="${GEOSERVER_DATASTORE}/postgis/featuretypes"


SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
JSON_DIR="${SCRIPT_DIR}/json"
SLD_DIR="${SCRIPT_DIR}/sld"

echo "GeoServer initialization script starting..."
echo "DB_HOST: ${DB_HOST}"
echo "DB_NAME: ${DB_NAME}"
echo "GEOSERVER_URL: ${GEOSERVER_URL}"
echo "GEOSERVER_WORKSPACE: ${GEOSERVER_WORKSPACE}"

wait_for_geoserver() {
    local max_attempts=60
    local attempt=0
    echo "Waiting for GeoServer to be ready..."
    while [ $attempt -lt $max_attempts ]; do
        if curl -s -f -u "${GEOSERVER_USER}:${GEOSERVER_PASSWORD}" \
            "${GEOSERVER_URL}/rest/about/version" > /dev/null 2>&1; then
            echo "GeoServer is ready!"
            return 0
        fi
        attempt=$((attempt + 1))
        echo "Attempt $attempt/$max_attempts: GeoServer not ready yet, waiting 5 seconds..."
        sleep 5
    done
    echo "ERROR: GeoServer did not become ready after $max_attempts attempts"
    return 1
}

tables_exist() {
    PGPASSWORD="${DB_PASSWORD}" \
    psql -U "${DB_USER}" -d "${DB_NAME}" -h "${DB_HOST}" -p "${DB_PORT}" \
        -tAf "${SCRIPT_DIR}/table_check.sql" 2>/dev/null | grep -q "^t$"
}

wait_for_tables() {
    local max_attempts=60
    local attempt=0
    echo "Waiting for database tables to be created..."
    while [ $attempt -lt $max_attempts ]; do
        if tables_exist; then
            echo "Database tables exist!"
            return 0
        fi
        attempt=$((attempt + 1))
        echo "Attempt $attempt/$max_attempts: Tables not ready yet, waiting 5 seconds..."
        sleep 5
    done
    echo "ERROR: Database tables did not become available after $max_attempts attempts"
    return 1
}

post_request() {
    local endpoint="$1"
    local json_data="$2"
    local url="${GEOSERVER_URL}/rest/${endpoint}"

    echo "POST ${endpoint}"
    local response=$(curl -s -w "\n%{http_code}" -X POST \
        -u "${GEOSERVER_USER}:${GEOSERVER_PASSWORD}" \
        -H "accept: application/json" \
        -H "content-type: application/json" \
        -d "${json_data}" \
        "${url}")

    local http_code=$(echo "$response" | tail -n1)
    local body=$(echo "$response" | sed '$d')

    if [ "$http_code" -eq 201 ] || [ "$http_code" -eq 200 ]; then
        echo "Success (HTTP $http_code)"
        return 0
    elif [ "$http_code" -eq 409 ]; then
        echo "Already exists (HTTP $http_code), attempting update..."
        curl -s -X PUT \
            -u "${GEOSERVER_USER}:${GEOSERVER_PASSWORD}" \
            -H "accept: application/json" \
            -H "content-type: application/json" \
            -d "${json_data}" \
            "${url}" > /dev/null
        echo "Updated"
        return 0
    else
        echo "Failed (HTTP $http_code): $body"
        return 1
    fi
}

post_sld() {
    local sld_file="$1"
    local style_name=$(basename "$sld_file" .sld)
    local url="${GEOSERVER_URL}/rest/styles"

    echo "POST style: ${style_name}"

    local check_response=$(curl -s -w "\n%{http_code}" \
        -u "${GEOSERVER_USER}:${GEOSERVER_PASSWORD}" \
        "${url}/${style_name}")
    local http_code=$(echo "$check_response" | tail -n1)

    if [ "$http_code" -eq 200 ]; then
        echo "Style ${style_name} already exists, skipping..."
        return 0
    fi

    local response=$(curl -s -w "\n%{http_code}" -X POST \
        -u "${GEOSERVER_USER}:${GEOSERVER_PASSWORD}" \
        -H "accept: application/json" \
        -H "content-type: application/vnd.ogc.sld+xml" \
        --data-binary "@${sld_file}" \
        "${url}?name=${style_name}")

    local http_code=$(echo "$response" | tail -n1)

    if [ "$http_code" -eq 201 ] || [ "$http_code" -eq 200 ]; then
        echo "Success (HTTP $http_code)"
        return 0
    else
        echo "Failed (HTTP $http_code)"
        return 1
    fi
}

get_native_bbox() {
    local table_name="$1"
    local bbox

    bbox=$(PGPASSWORD="${DB_PASSWORD}" \
        psql -U "${DB_USER}" -d "${DB_NAME}" -h "${DB_HOST}" -p "${DB_PORT}" \
        -tA -c "SELECT gs.get_native_bbox('${table_name}')" 2>/dev/null)

    if [ -z "$bbox" ] || [ "$bbox" = "" ]; then
        echo "ERROR: Could not get bbox for ${table_name}" >&2
        return 1
    fi

    IFS='|' read -r xmin xmax ymin ymax <<< "$bbox"

    sed "s/\"XMIN\"/${xmin}/g;" \
        "s/\"XMAX\"/${xmax}/g;" \
        "s/\"YMIN\"/${ymin}/g;" \
        "s/\"YMAX\"/${ymax}/g;" \
        "$2"
}

main() {
    wait_for_geoserver || exit 1
    wait_for_tables || exit 1

    echo ""
    echo "Starting GeoServer layer publication..."
    echo ""

    declare -a requests=(
        "workspaces?default=true|${JSON_DIR}/workspace.json"
        "${GEOSERVER_DATASTORE}|${JSON_DIR}/postgis.json"
        "${GEOSERVER_FEATURE_TYPES}|${JSON_DIR}/addresses.json"
        "${GEOSERVER_FEATURE_TYPES}|${JSON_DIR}/streets.json"
        "${GEOSERVER_FEATURE_TYPES}|${JSON_DIR}/municipalities.json"
        "${GEOSERVER_FEATURE_TYPES}|${JSON_DIR}/settlements.json"
        "${GEOSERVER_FEATURE_TYPES}|${JSON_DIR}/counties.json"
        "${GEOSERVER_FEATURE_TYPES}|${JSON_DIR}/country.json"
        "${GEOSERVER_FEATURE_TYPES}|${JSON_DIR}/cadastral_municipalities.json"
        "${GEOSERVER_FEATURE_TYPES}|${JSON_DIR}/cadastral_parcels.json"
        "${GEOSERVER_FEATURE_TYPES}|${JSON_DIR}/buildings.json"
    )

    for request in "${requests[@]}"; do
        IFS='|' read -r endpoint json_file <<< "$request"

        if [ ! -f "$json_file" ]; then
            echo "ERROR: JSON file not found: ${json_file}"
            continue
        fi

        if [ "$(basename "$json_file")" = "postgis.json" ]; then
            json_content=$(sed "s/DB_NAME/${DB_NAME}/g;" \
                "s/DB_HOST/${DB_HOST}/g;" \
                "s/DB_PORT/${DB_PORT}/g;" \
                "s/DB_USER/${DB_USER}/g;" \
                "s/DB_PASSWORD/${DB_PASSWORD}/g;" \
                "$json_file")
            post_request "$endpoint" "$json_content" \
            || echo "Warning: Failed to create/update ${endpoint}"
        elif [[ "$json_file" == *"addresses.json" ]] || \
             [[ "$json_file" == *"streets.json" ]] || \
             [[ "$json_file" == *"municipalities.json" ]] || \
             [[ "$json_file" == *"settlements.json" ]] || \
             [[ "$json_file" == *"counties.json" ]] || \
             [[ "$json_file" == *"country.json" ]] || \
             [[ "$json_file" == *"cadastral_municipalities.json" ]] || \
             [[ "$json_file" == *"cadastral_parcels.json" ]] || \
             [[ "$json_file" == *"buildings.json" ]]; then
            local table_name
            case "$(basename "$json_file")" in
                addresses.json)
                    table_name="gs.v_addresses"
                    ;;
                streets.json)
                    table_name="gs.mv_streets"
                    ;;
                municipalities.json)
                    table_name="gs.v_municipalities"
                    ;;
                settlements.json)
                    table_name="gs.v_settlements"
                    ;;
                counties.json)
                    table_name="gs.v_counties"
                    ;;
                country.json)
                    table_name="gs.v_country"
                    ;;
                cadastral_municipalities.json)
                    table_name="gs.v_cadastral_municipalities"
                    ;;
                cadastral_parcels.json)
                    table_name="gs.v_cadastral_parcels"
                    ;;
                buildings.json)
                    table_name="gs.v_buildings"
                    ;;
                *)
                    table_name=""
                    ;;
            esac

            if [ -n "$table_name" ]; then
                json_content=$(get_native_bbox "$table_name" "$json_file")
                if [ $? -eq 0 ]; then
                    post_request "$endpoint" "$json_content" \
                    || echo "Warning: Failed to create/update ${endpoint}"
                else
                    echo "Skipping ${endpoint} due to bbox error"
                fi
            fi
        else
            json_content=$(cat "$json_file")
            post_request "$endpoint" "$json_content" \
            || echo "Warning: Failed to create/update ${endpoint}"
        fi
    done

    echo ""
    echo "Uploading SLD styles..."
    echo ""

    declare -a slds=(
        "${SLD_DIR}/addresses.sld"
        "${SLD_DIR}/streets.sld"
        "${SLD_DIR}/municipalities.sld"
        "${SLD_DIR}/settlements.sld"
        "${SLD_DIR}/counties.sld"
        "${SLD_DIR}/country.sld"
        "${SLD_DIR}/cadastral_municipalities.sld"
        "${SLD_DIR}/cadastral_parcels.sld"
        "${SLD_DIR}/buildings.sld"
    )

    for sld_file in "${slds[@]}"; do
        if [ -f "$sld_file" ]; then
            post_sld "$sld_file" \
            || echo "Warning: Failed to upload $(basename "$sld_file")"
        else
            echo "SLD file not found: ${sld_file}"
        fi
    done

    echo ""
    echo "GeoServer initialization complete!"
}

main

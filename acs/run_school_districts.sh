#!/usr/bin/env bash
# Loads the ACS 5-year school district rows of the given pipelines (default: the Priority 2 cubes).
#
# Usage, after `source .env`:
#   acs/run_school_districts.sh [--year=2024] [--server=clickhouse-database] [pipeline ...]
#
# Each pipeline runs from its own folder with that folder first on PYTHONPATH, so its local
# static.py / helper.py are imported instead of acs/static.py and acs/helper.py.
# LoadStep appends: running a pipeline twice for the same year duplicates its rows.
# Fully suppressed districts are recorded in acs/reports/school_districts_suppressed.csv.
set -u
# Ctrl+C stops the whole run, not only the pipeline in progress
trap 'echo "Interrupted"; exit 130' INT

ACS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
YEAR=2024
SERVER=clickhouse-database
PIPELINES=()

for arg in "$@"; do
  case "$arg" in
    --year=*) YEAR="${arg#--year=}" ;;
    --server=*) SERVER="${arg#--server=}" ;;
    *) PIPELINES+=("${arg%/}") ;;
  esac
done

if [ ${#PIPELINES[@]} -eq 0 ]; then
  PIPELINES=(
    acs_yg_household_income
    acs_ygh_households_with_no_internet_2016
    acs_ygc_citizenship_status
    acs_ygf_place_of_birth_for_foreing_born
    acs_ygsi_gender_by_industry_c
    acs_ygsi_gender_by_industry_for_median_earnings
    acs_ygso_gender_by_occupation_for_median_earnings
    acs_ygi_industry_for_median_earnings
    acs_ygo_tenure
    acs_ygo_housing_value_bucket
    acs_ygmt_mortgage_status_by_real_estate_taxes
    acs_ygh_health_care_coverage_overall
    acs_yghsa_health_coverage_status_by_gender_by_age
    acs_ygt_means_of_transportation_to_work
    acs_ygt_travel_time_to_work
    acs_ygt_mean_transportation_time_to_work
    acs_ygsv_gender_of_workers_by_vehicles_available
    acs_ygv_veterans
  )
fi

FAILED=()
for p in "${PIPELINES[@]}"; do
  echo "=== $p ($YEAR) ==="
  if ! (cd "$ACS_DIR/$p" && PYTHONPATH=".:${PYTHONPATH:-}" bamboo-cli --folder . --entry "${p}_pipeline" \
      --year="$YEAR" --estimate=5 --server="$SERVER" --geo=school_district); then
    echo "FAILED: $p"
    FAILED+=("$p")
  fi
done

echo "Finished ${#PIPELINES[@]} pipelines, ${#FAILED[@]} failed${FAILED[*]:+: ${FAILED[*]}}"

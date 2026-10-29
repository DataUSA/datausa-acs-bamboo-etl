#!/usr/bin/env bash
# Loads the ACS 5-year school district rows of the given pipelines
# (default: the Priority 2 cubes; --priority=3 for the Priority 3 cubes).
#
# Usage, after `source .env`:
#   acs/run_school_districts.sh [--year=2024] [--server=clickhouse-database] [--priority=2|3] [pipeline ...]
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
PRIORITY=2
PIPELINES=()

for arg in "$@"; do
  case "$arg" in
    --year=*) YEAR="${arg#--year=}" ;;
    --server=*) SERVER="${arg#--server=}" ;;
    --priority=*) PRIORITY="${arg#--priority=}" ;;
    *) PIPELINES+=("${arg%/}") ;;
  esac
done

if [ ${#PIPELINES[@]} -eq 0 ] && [ "$PRIORITY" = 3 ]; then
  PIPELINES=(
    acs_ygh_occupied_households_lacking_plumbing
    acs_ygh_occupied_households_lacking_kitchen
    acs_ygh_homeowners_with_mortgage_spending_30_percent_on_costs
    acs_yg_gini
    acs_ygh_renters_by_income_percentage
    acs_ygo_occupation_for_median_earnings
    acs_ygpa_place_of_birth_by_age
    acs_ygcs_median_age_by_citizenship_status_by_gender
    acs_ygst_gender_of_workers_by_transportation_to_work
    acs_ygs_aggregate_travel_time_to_work
  )
elif [ ${#PIPELINES[@]} -eq 0 ]; then
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

NULL_LIST = [-555555555, -999999999, -222222222, -666666666, -333333333]

LIST_STATE = ['28', '29', '30', '31', '32', '33', '34', '35', '36', '37', '38', '39', '40', '41', '42', '44', '45', '46', '47',
              '48', '50', '49', '51', '53', '54', '55', '56', '72', '01', '02', '04', '05', '06', '08', '10', '11', '09', '12', 
              '13', '16', '15', '17', '18', '19', '20', '21', '22', '23', '24', '25', '26', '27']

FIPS_CODE = {
    'us': '01000US',
    'state': '04000US',
    'county': '05000US',
    'place': '16000US',
    'public use microdata area': '79500US',
    'msa': '31000US',
    'tract': '14000US',
    'congressional district': '50000US',
    'zip code tabulation area': '86000US'
}

DICT_APIS = {
    'acs_yg_gini': ['https://api.census.gov/data/{}/acs/acs{}?get=B19083_001E,B19083_001M&for={}&key={}', 
                    'https://api.census.gov/data/{}/acs/acs{}?get=B19083_001E,B19083_001M&for={}&key={}&in=state:{}'],
    'acs_health_coverage_s': ['https://api.census.gov/data/{}/acs/acs{}/subject?get=S2703_C02_003E,S2703_C02_004E,S2703_C02_005E,S2703_C02_007E,S2703_C02_008E,S2703_C02_009E,S2703_C02_011E,S2703_C02_012E,S2703_C02_013E,S2704_C02_003E,S2704_C02_004E,S2704_C02_005E,S2704_C02_007E,S2704_C02_008E,S2704_C02_009E,S2704_C02_011E,S2704_C02_012E,S2704_C02_013E,S2701_C04_011E,S2701_C04_012E,S2701_C04_013E,S2703_C01_003E,S2703_C01_004E,S2703_C01_005E,S2703_C01_001E,S2703_C02_003M,S2703_C02_004M,S2703_C02_005M,S2703_C02_007M,S2703_C02_008M,S2703_C02_009M,S2703_C02_011M,S2703_C02_012M,S2703_C02_013M,S2704_C02_003M,S2704_C02_004M,S2704_C02_005M,S2704_C02_007M,S2704_C02_008M,S2704_C02_009M,S2704_C02_011M,S2704_C02_012M,S2704_C02_013M,S2701_C04_011M,S2701_C04_012M,S2701_C04_013M,S2703_C01_003M,S2703_C01_004M,S2703_C01_005M,S2703_C01_001M&for={}&key={}', 
                              'https://api.census.gov/data/{}/acs/acs{}/subject?get=S2703_C02_003E,S2703_C02_004E,S2703_C02_005E,S2703_C02_007E,S2703_C02_008E,S2703_C02_009E,S2703_C02_011E,S2703_C02_012E,S2703_C02_013E,S2704_C02_003E,S2704_C02_004E,S2704_C02_005E,S2704_C02_007E,S2704_C02_008E,S2704_C02_009E,S2704_C02_011E,S2704_C02_012E,S2704_C02_013E,S2701_C04_011E,S2701_C04_012E,S2701_C04_013E,S2703_C01_003E,S2703_C01_004E,S2703_C01_005E,S2703_C01_001E,S2703_C02_003M,S2703_C02_004M,S2703_C02_005M,S2703_C02_007M,S2703_C02_008M,S2703_C02_009M,S2703_C02_011M,S2703_C02_012M,S2703_C02_013M,S2704_C02_003M,S2704_C02_004M,S2704_C02_005M,S2704_C02_007M,S2704_C02_008M,S2704_C02_009M,S2704_C02_011M,S2704_C02_012M,S2704_C02_013M,S2701_C04_011M,S2701_C04_012M,S2701_C04_013M,S2703_C01_003M,S2703_C01_004M,S2703_C01_005M,S2703_C01_001M&for={}&key={}&in=state:{}'],
    'acs_yg_household_income': ['https://api.census.gov/data/{}/acs/acs{}?get=B19001_002E,B19001_003E,B19001_004E,B19001_005E,B19001_006E,B19001_007E,B19001_008E,B19001_009E,B19001_010E,B19001_011E,B19001_012E,B19001_013E,B19001_014E,B19001_015E,B19001_016E,B19001_017E,B19001_002M,B19001_003M,B19001_004M,B19001_005M,B19001_006M,B19001_007M,B19001_008M,B19001_009M,B19001_010M,B19001_011M,B19001_012M,B19001_013M,B19001_014M,B19001_015M,B19001_016M,B19001_017M&for={}&key={}', 
                                'https://api.census.gov/data/{}/acs/acs{}?get=B19001_002E,B19001_003E,B19001_004E,B19001_005E,B19001_006E,B19001_007E,B19001_008E,B19001_009E,B19001_010E,B19001_011E,B19001_012E,B19001_013E,B19001_014E,B19001_015E,B19001_016E,B19001_017E,B19001_002M,B19001_003M,B19001_004M,B19001_005M,B19001_006M,B19001_007M,B19001_008M,B19001_009M,B19001_010M,B19001_011M,B19001_012M,B19001_013M,B19001_014M,B19001_015M,B19001_016M,B19001_017M&for={}&key={}&in=state:{}'],
    'acs_yg_housing_median_value': ['https://api.census.gov/data/{}/acs/acs{}?get=B25077_001E,B25077_001M&for={}&key={}', 
                                    'https://api.census.gov/data/{}/acs/acs{}?get=B25077_001E,B25077_001M&for={}&key={}&in=state:{}'],
    'acs_yg_total_population': ['https://api.census.gov/data/{}/acs/acs{}?get=B01003_001E,B01003_001M&for={}&key={}', 
                                'https://api.census.gov/data/{}/acs/acs{}?get=B01003_001E,B01003_001M&for={}&key={}&in=state:{}'],
    'acs_ygc_citizenship_status': ['https://api.census.gov/data/{}/acs/acs{}?get=B05001_002E,B05001_003E,B05001_004E,B05001_005E,B05001_006E,B05001_002M,B05001_003M,B05001_004M,B05001_005M,B05001_006M&for={}&key={}', 
                                   'https://api.census.gov/data/{}/acs/acs{}?get=B05001_002E,B05001_003E,B05001_004E,B05001_005E,B05001_006E,B05001_002M,B05001_003M,B05001_004M,B05001_005M,B05001_006M&for={}&key={}&in=state:{}'],
    'acs_ygcs_median_age_by_citizenship_status_by_gender': ['https://api.census.gov/data/{}/acs/acs{}?get=B05004_001E,B05004_002E,B05004_003E,B05004_004E,B05004_005E,B05004_006E,B05004_007E,B05004_008E,B05004_009E,B05004_010E,B05004_011E,B05004_012E,B05004_014E,B05004_015E,B05004_001M,B05004_002M,B05004_003M,B05004_004M,B05004_005M,B05004_006M,B05004_007M,B05004_008M,B05004_009M,B05004_010M,B05004_011M,B05004_012M,B05004_014M,B05004_015M&for={}&key={}', 
                                                           'https://api.census.gov/data/{}/acs/acs{}?get=B05004_001E,B05004_002E,B05004_003E,B05004_004E,B05004_005E,B05004_006E,B05004_007E,B05004_008E,B05004_009E,B05004_010E,B05004_011E,B05004_012E,B05004_014E,B05004_015E,B05004_001M,B05004_002M,B05004_003M,B05004_004M,B05004_005M,B05004_006M,B05004_007M,B05004_008M,B05004_009M,B05004_010M,B05004_011M,B05004_012M,B05004_014M,B05004_015M&for={}&key={}&in=state:{}'],
    'acs_ygs_median_age_total': ['https://api.census.gov/data/{}/acs/acs{}?get=B01002_001E,B01002_002E,B01002_003E,B01002_001M,B01002_002M,B01002_003M&for={}&key={}', 
                                 'https://api.census.gov/data/{}/acs/acs{}?get=B01002_001E,B01002_002E,B01002_003E,B01002_001M,B01002_002M,B01002_003M&for={}&key={}&in=state:{}'],
    'acs_ygs_aggregate_travel_time_to_work': ['https://api.census.gov/data/{}/acs/acs{}?get=B08013_002E,B08013_003E,B08013_002M,B08013_003M&for={}&key={}', 
                                              'https://api.census.gov/data/{}/acs/acs{}?get=B08013_002E,B08013_003E,B08013_002M,B08013_003M&for={}&key={}&in=state:{}'],
    'acs_ygr_race_with_hispanic': ['https://api.census.gov/data/{}/acs/acs{}?get=B03002_003E,B03002_004E,B03002_005E,B03002_006E,B03002_007E,B03002_008E,B03002_010E,B03002_011E,B03002_013E,B03002_014E,B03002_015E,B03002_016E,B03002_017E,B03002_018E,B03002_020E,B03002_021E,B03002_003M,B03002_004M,B03002_005M,B03002_006M,B03002_007M,B03002_008M,B03002_010M,B03002_011M,B03002_013M,B03002_014M,B03002_015M,B03002_016M,B03002_017M,B03002_018M,B03002_020M,B03002_021M&for={}&key={}', 
                                   'https://api.census.gov/data/{}/acs/acs{}?get=B03002_003E,B03002_004E,B03002_005E,B03002_006E,B03002_007E,B03002_008E,B03002_010E,B03002_011E,B03002_013E,B03002_014E,B03002_015E,B03002_016E,B03002_017E,B03002_018E,B03002_020E,B03002_021E,B03002_003M,B03002_004M,B03002_005M,B03002_006M,B03002_007M,B03002_008M,B03002_010M,B03002_011M,B03002_013M,B03002_014M,B03002_015M,B03002_016M,B03002_017M,B03002_018M,B03002_020M,B03002_021M&for={}&key={}&in=state:{}'],
    'acs_ygo_tenure': ['https://api.census.gov/data/{}/acs/acs{}?get=B25003_002E,B25003_003E,B25003_002M,B25003_003M&for={}&key={}', 
                       'https://api.census.gov/data/{}/acs/acs{}?get=B25003_002E,B25003_003E,B25003_002M,B25003_003M&for={}&key={}&in=state:{}'],
    'acs_ygmt_mortgage_status_by_real_estate_taxes': ['https://api.census.gov/data/{}/acs/acs{}?get=B25102_003E,B25102_004E,B25102_005E,B25102_006E,B25102_007E,B25102_008E,B25102_010E,B25102_011E,B25102_012E,B25102_013E,B25102_014E,B25102_015E,B25102_003M,B25102_004M,B25102_005M,B25102_006M,B25102_007M,B25102_008M,B25102_010M,B25102_011M,B25102_012M,B25102_013M,B25102_014M,B25102_015M&for={}&key={}', 
                                                      'https://api.census.gov/data/{}/acs/acs{}?get=B25102_003E,B25102_004E,B25102_005E,B25102_006E,B25102_007E,B25102_008E,B25102_010E,B25102_011E,B25102_012E,B25102_013E,B25102_014E,B25102_015E,B25102_003M,B25102_004M,B25102_005M,B25102_006M,B25102_007M,B25102_008M,B25102_010M,B25102_011M,B25102_012M,B25102_013M,B25102_014M,B25102_015M&for={}&key={}&in=state:{}'],
    'acs_ygh_occupied_households_lacking_plumbing': ['https://api.census.gov/data/{}/acs/acs{}?get=B25048_002E,B25048_003E,B25048_002M,B25048_003M&for={}&key={}', 
                                                     'https://api.census.gov/data/{}/acs/acs{}?get=B25048_002E,B25048_003E,B25048_002M,B25048_003M&for={}&key={}&in=state:{}'],
    'acs_ygh_occupied_households_lacking_kitchen': ['https://api.census.gov/data/{}/acs/acs{}?get=B25052_002E,B25052_003E,B25052_002M,B25052_003M&for={}&key={}', 
                                                    'https://api.census.gov/data/{}/acs/acs{}?get=B25052_002E,B25052_003E,B25052_002M,B25052_003M&for={}&key={}&in=state:{}'],
    'acs_ygh_households_with_no_internet_2016': ['https://api.census.gov/data/{}/acs/acs{}?get=B28002_002E,B28002_012E,B28002_013E,B28002_002M,B28002_012M,B28002_013M&for={}&key={}', 
                                                 'https://api.census.gov/data/{}/acs/acs{}?get=B28002_002E,B28002_012E,B28002_013E,B28002_002M,B28002_012M,B28002_013M&for={}&key={}&in=state:{}']
}
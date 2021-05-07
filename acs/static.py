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
                    'https://api.census.gov/data/{}/acs/acs{}?get=B19083_001E,B19083_001M&for={}&key={}&in=state:{}']
}
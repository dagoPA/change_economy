import sys

from pathlib import Path
import pandas as pd
import ee
import geeTools as geet

# Begin Params
municipio = sys.argv[1]
export_result = bool(sys.argv[2])
export = bool(sys.argv[3])
sum_values = bool(sys.argv[4])

orbits = ['ASCENDING', 'DESCENDING']
gdrive_folder = 'changes_cdmx_1m'
start_date = '2017-01-01'
end_date = '2021-12-01'
frequency = '1M'
local_data_dir = 'data'
# End Params

# Get list of dates
dates = pd.date_range(start_date, end_date, freq=frequency) - pd.offsets.MonthBegin(1)
dates = dates.strftime("%Y-%m-%d").values.tolist()

# Get the list of municipios
capitales = ee.FeatureCollection("projects/ee-vulnerability-gee4geo/assets/capitales")

for orbit_ in orbits:
    my_file = Path('data/changes_municipios_2/' + municipio + '_' + orbit_ + '_' + '.csv')
    if not my_file.is_file():
        # Filter municipio and convert it to geometry in case it's needed
        filter_ee = ee.Filter.inList('NOMGEO', [municipio])
        capital = capitales.filter(filter_ee).first().geometry()

        if capital.name() != 'Geometry':
            capital = capital.geometries().get(1)

        changes = []
        # Calculate changes, comparing each month against the next one
        for i in range(2, len(dates)):
            sum = geet.calculate_monthly_changes(dates[i - 2], dates[i - 1], dates[i], capital, orbit_, 'test_SAR',
                                                 export=export, export_result=export_result, sum_values=sum_values)
            changes.append(sum)

        dict = {municipio + '_' + orbit_: changes}
        df = pd.DataFrame(dict)
        df.to_csv(local_data_dir + '/' + municipio + '_' + orbit_ + '_' + '.csv')

print('end of file')

__author__ = 'wangchao'
import sys
sys.path.append('./pycast-master/')

import pycast

from pycast.common.timeseries import TimeSeries
from pycast.methods import HoltWintersMethod
from pycast.optimization import GridSearch
from pycast.errors import SymmetricMeanAbsolutePercentageError as SMAPE

data_list = [1.1, 2.1, 3.3, 4.4, 5.5, 1.1, 2.2, 3.3]

orig = TimeSeries(isNormalized=True)
for i in range(len(data_list)):
    orig.add_entry(i, data_list[i]) #offset to first data entry in line

seasonLength = int(5)
season_values = []
for i in range(seasonLength):
    season_values.append(float(1.0))
#print season_values

hwm = HoltWintersMethod(seasonLength = seasonLength, valuesToForecast = 3)
hwm.set_parameter("seasonValues", season_values)


gridSearch = GridSearch(SMAPE)
optimal_forecasting, error, optimal_params = gridSearch.optimize(orig, [hwm])
predicted = optimal_forecasting.execute(orig)

print str(orig)

print str(predicted)


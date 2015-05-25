__author__ = 'wangchao'

from money_flow_predictor import *

sys.path.append('./pycast/')

from pycast.common.timeseries import TimeSeries
from pycast.methods import ExponentialSmoothing,HoltMethod,HoltWintersMethod
from pycast.optimization import GridSearch
#from pycast.errors import SymmetricMeanAbsolutePercentageError as SMAPE
from pycast.errors import MeanSquaredError as SMAPE

class ExponentialSmoothingPredictor(Predictor):
    def __init__(self, data_container, train_series_length=120):
        Predictor.__init__(self, data_container)
        self.init_param_list = [0.1]
        self.max_train_case_num = train_series_length

    def build_time_series_data_list(self, target_date_str, index, back_trace_day_num):
        feature_begin_date = add_day(target_date_str, -1 * (back_trace_day_num))
        if not self.data.purchase_redeem_map.has_key(feature_begin_date):
            return None
        feature_list = []
        feature_date = feature_begin_date
        i = 0
        while i < back_trace_day_num:
            feature_list.append([i, self.math_log(float(self.data.purchase_redeem_map[feature_date][index]))])
            feature_date = add_day(feature_date)
            i += 1
        return feature_list

    def train_target(self, data_list, model_list):# data_list: [date, value]
        orig = TimeSeries(isNormalized=True)
        for i in range(len(data_list)):
            orig.add_entry(data_list[i][0], data_list[i][1])
        gridSearch = GridSearch(SMAPE)
        optimal_forecasting, error, optimal_params = gridSearch.optimize(orig, model_list)
        #print "======" + str(optimal_forecasting._parameters)
        return optimal_forecasting

    def train_purchase(self):
        pass

    def train_redeem(self):
        pass

    def train_spc_model(self, index, begin_date, day_length):
        data_list = self.build_time_series_data_list(begin_date, index, self.max_train_case_num)
        model_list = []
        for param_value in self.init_param_list:
            model_list.append(ExponentialSmoothing(smoothingFactor=param_value, valuesToForecast=day_length))
        best_model = self.train_target(data_list, model_list)
        predict_series = best_model.execute(data_list)
        predict_data_list = predict_series.to_twodim_list()
        ret_list = []
        for i in range(-1 * day_length, 0):
            ret_list.append(predict_data_list[i][1])
        return ret_list

    def predict(self, begin_date_str, end_date_str):
        predict_map = {}
        c_date = begin_date_str
        while int(c_date) < int(end_date_str):
            begin_date = c_date
            end_date = add_day(c_date, MAX_PREDICT_DAY_NUM)
            if int(end_date) > int(end_date_str):
                end_date = end_date_str
            day_length = 0
            c_date = begin_date
            while c_date != end_date:
                day_length += 1
                c_date = add_day(c_date)
            purchase_results = self.train_spc_model(0, begin_date, day_length)
            redeem_results = self.train_spc_model(1, begin_date, day_length)
            predict_date = begin_date
            i = 0
            while predict_date != end_date:
                predict_map[predict_date] = [0, 0]
                predict_map[predict_date][0] = int(self.math_exp(purchase_results[i]))
                predict_map[predict_date][1] = int(self.math_exp(redeem_results[i]))
                predict_date = add_day(predict_date)
                i += 1
        return predict_map

class HoltMethodPredictor(Predictor):
    def __init__(self, data_container, train_series_length=120):
        Predictor.__init__(self, data_container)
        self.init_alpha_list = [0.1]
        self.init_beta_list = [0.5]
        self.max_train_case_num = train_series_length

    def build_time_series_data_list(self, target_date_str, index, back_trace_day_num):
        feature_begin_date = add_day(target_date_str, -1 * (back_trace_day_num))
        if not self.data.purchase_redeem_map.has_key(feature_begin_date):
            return None
        feature_list = []
        feature_date = feature_begin_date
        i = 0
        while i < back_trace_day_num:
            feature_list.append([i, self.math_log(float(self.data.purchase_redeem_map[feature_date][index]))])
            #feature_list.append([i, float(self.data.purchase_redeem_map[feature_date][index])])
            feature_date = add_day(feature_date)
            i += 1
        return feature_list

    def train_target(self, data_list, model_list):# data_list: [date, value]
        orig = TimeSeries(isNormalized=True)
        for i in range(len(data_list)):
            orig.add_entry(data_list[i][0], data_list[i][1])
        gridSearch = GridSearch(SMAPE)
        optimal_forecasting, error, optimal_params = gridSearch.optimize(orig, model_list)
        #print "======" + str(optimal_params)
        return optimal_forecasting

    def train_purchase(self):
        pass

    def train_redeem(self):
        pass

    def train_spc_model(self, index, begin_date, day_length):
        data_list = self.build_time_series_data_list(begin_date, index, self.max_train_case_num)
        model_list = []
        for a in self.init_alpha_list:
            for b in self.init_beta_list:
                model_list.append(HoltMethod(smoothingFactor=a, trendSmoothingFactor=b, valuesToForecast=day_length))
        best_model = self.train_target(data_list, model_list)
        predict_series = best_model.execute(data_list)
        predict_data_list = predict_series.to_twodim_list()
        ret_list = []
        for i in range(-1 * day_length, 0):
            ret_list.append(predict_data_list[i][1])
        return ret_list

    def predict(self, begin_date_str, end_date_str):
        predict_map = {}
        c_date = begin_date_str
        while int(c_date) < int(end_date_str):
            begin_date = c_date
            end_date = add_day(c_date, MAX_PREDICT_DAY_NUM)
            if int(end_date) > int(end_date_str):
                end_date = end_date_str
            day_length = 0
            c_date = begin_date
            while c_date != end_date:
                day_length += 1
                c_date = add_day(c_date)
            purchase_results = self.train_spc_model(0, begin_date, day_length)
            redeem_results = self.train_spc_model(1, begin_date, day_length)
            predict_date = begin_date
            i = 0
            while predict_date != end_date:
                predict_map[predict_date] = [0, 0]
                predict_map[predict_date][0] = int(self.math_exp(purchase_results[i]))
                predict_map[predict_date][1] = int(self.math_exp(redeem_results[i]))
                predict_date = add_day(predict_date)
                i += 1
        return predict_map


class HoltWintersPredictor(Predictor):
    def __init__(self, data_container, train_series_length=120, season_length=7):
        Predictor.__init__(self, data_container)
        self.init_alpha_list = [0.1]
        self.init_beta_list = [0.5]
        self.init_gamma_list = [0.5]
        self.season_length = season_length
        self.max_train_case_num = train_series_length

    def build_time_series_data_list(self, target_date_str, index, back_trace_day_num):
        feature_begin_date = add_day(target_date_str, -1 * (back_trace_day_num))
        if not self.data.purchase_redeem_map.has_key(feature_begin_date):
            return None
        feature_list = []
        feature_date = feature_begin_date
        i = 0
        while i < back_trace_day_num:
            feature_list.append([i, self.math_log(float(self.data.purchase_redeem_map[feature_date][index]))])
            feature_date = add_day(feature_date)
            i += 1
        return feature_list

    def train_target(self, data_list, model_list):# data_list: [date, value]
        orig = TimeSeries(isNormalized=True)
        for i in range(len(data_list)):
            orig.add_entry(data_list[i][0], data_list[i][1])
        gridSearch = GridSearch(SMAPE)
        optimal_forecasting, error, optimal_params = gridSearch.optimize(orig, model_list)
        #print "======" + str(optimal_params)
        return optimal_forecasting

    def train_purchase(self):
        pass

    def train_redeem(self):
        pass

    def train_spc_model(self, index, begin_date, day_length):
        data_list = self.build_time_series_data_list(begin_date, index, self.max_train_case_num)
        model_list = []
        for a in self.init_alpha_list:
            for b in self.init_beta_list:
                for g in self.init_gamma_list:
                    model_list.append(HoltWintersMethod(smoothingFactor=a, trendSmoothingFactor=b, seasonSmoothingFactor=g, seasonLength=self.season_length, valuesToForecast=day_length))
        best_model = self.train_target(data_list, model_list)
        predict_series = best_model.execute(data_list)
        predict_data_list = predict_series.to_twodim_list()
        ret_list = []
        for i in range(-1 * day_length, 0):
            ret_list.append(predict_data_list[i][1])
        return ret_list

    def predict(self, begin_date_str, end_date_str):
        predict_map = {}
        c_date = begin_date_str
        while int(c_date) < int(end_date_str):
            begin_date = c_date
            end_date = add_day(c_date, MAX_PREDICT_DAY_NUM)
            if int(end_date) > int(end_date_str):
                end_date = end_date_str
            day_length = 0
            c_date = begin_date
            while c_date != end_date:
                day_length += 1
                c_date = add_day(c_date)
            purchase_results = self.train_spc_model(0, begin_date, day_length)
            redeem_results = self.train_spc_model(1, begin_date, day_length)
            predict_date = begin_date
            i = 0
            while predict_date != end_date:
                predict_map[predict_date] = [0, 0]
                predict_map[predict_date][0] = int(self.math_exp(purchase_results[i]))
                predict_map[predict_date][1] = int(self.math_exp(redeem_results[i]))
                predict_date = add_day(predict_date)
                i += 1
        return predict_map


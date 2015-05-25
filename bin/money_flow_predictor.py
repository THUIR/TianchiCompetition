__author__ = 'wangchao'

import numpy as np

from wc_competition_common import *

from wc_config import *

from sklearn.linear_model import Lasso

from sklearn import svm




class DataContainer():
    def __init__(self, u_list, pr_map, up_map, td_map, bd_map):
        self.user_day_item_list = u_list
        self.purchase_redeem_map = pr_map
        self.user_profile_map = up_map
        self.taobao_day_map = td_map
        self.bank_day_map = bd_map

class Predictor():
    def __init__(self, data_container):
        self.purchase_rate = 0.45
        self.redeem_rate = 0.55
        self.max_predict_day_num = 31
        self.data = data_container
        self.train_valid_date = "" # train_valid_date - 1 is the last valid date in training process

    def math_log(self, x):
        return math.log10(1.0 + x)

    def math_exp(self, x):
        return (10.0 ** x) - 1.0

    def train_purchase(self):
        pass

    def train_redeem(self):
        pass

    def train(self, tv_date):
        self.train_valid_date = tv_date
        self.train_purchase()
        self.train_redeem()

    def predict_purchase(self, begin_date, end_date):
        pass

    def predict_redeem(self, begin_date, end_date):
        pass

    def predict(self, begin_date, end_date):
        predict_map = {}
        purchase_predict_map = self.data.predict_purchase(begin_date, end_date)
        redeem_predict_map = self.data.predict_purchase(begin_date, end_date)
        predict_date = end_date
        while predict_date != begin_date:
            predict_date = add_day(predict_date, -1)
            predict_map[predict_date] = [0, 0]
            predict_map[predict_date][0] = purchase_predict_map[predict_date]
            predict_map[predict_date][1] = redeem_predict_map[predict_date]
        return predict_map

    def test_performance(self, begin_date, end_date):
        predict_results = self.predict(begin_date, end_date)
        p_score_list = []
        r_score_list = []
        s_list = []
        date_str = begin_date
        while date_str != end_date:
            p_value = predict_results[date_str][0]
            r_value = predict_results[date_str][1]
            p_real = self.data.purchase_redeem_map[date_str][0]
            r_real = self.data.purchase_redeem_map[date_str][1]
            p_score_list.append([date_str, p_value, p_real, self.calculate_purchase_score(p_value, p_real)])
            r_score_list.append([date_str, r_value, r_real, self.calculate_purchase_score(r_value, r_real)])
            s_list.append([date_str, self.calculate_score(p_value, p_real, r_value, r_real)])
            date_str = add_day(date_str)
        ret_str = ""
        ret_str += result_arr("Total Score: ", s_list) + "\n"
        ret_str += result_arr("Purchase Score: ", p_score_list) + "\n"
        ret_str += result_arr("Redeem Score: ", r_score_list) + "\n"
        print ret_str
        return ret_str

    def calculate_purchase_score(self, predict_value, real_value):
        purchase = 1.0 * abs(predict_value - real_value) / real_value
        score = max(0.0, (0.3 - purchase)) / 0.3 * 10
        return score

    def calculate_redeem_score(self, predict_value, real_value):
        redeem = 1.0 * abs(predict_value - real_value) / real_value
        score = max(0.0, (0.3 - redeem)) / 0.3 * 10
        return score

    def calculate_score(self, p_predict, p_real, r_predict, r_real):
        return self.purchase_rate * self.calculate_purchase_score(p_predict, p_real) + self.redeem_rate * self.calculate_redeem_score(r_predict, r_real)

class NaivePredictor(Predictor):
    def predict(self, begin_date, end_date):
        predict_map = {}
        predict_date = end_date
        source_date = begin_date
        while predict_date != begin_date:
            predict_date = add_day(predict_date, -1)
            source_date = add_day(source_date, -1)
            predict_map[predict_date] = [0, 0]
            predict_map[predict_date][0] = self.data.purchase_redeem_map[source_date][0]
            predict_map[predict_date][1] = self.data.purchase_redeem_map[source_date][1]
        return predict_map

class SimpleRegressionPredictor(Predictor):
    def __init__(self, data_container, mtc_num = 120, fbt_num = 15):
        Predictor.__init__(self, data_container)
        self.purchase_model = svm.SVR()
        self.redeem_model = svm.SVR()
        self.feature_back_trace_day_num = fbt_num
        self.max_train_case_num = mtc_num

    def build_feature(self, target_date_str):
        feature_begin_date = add_day(target_date_str, -1 * (self.feature_back_trace_day_num))
        if not self.data.purchase_redeem_map.has_key(feature_begin_date):
            return None
        feature_list = []
        feature_date = feature_begin_date
        i = 0
        while i < self.feature_back_trace_day_num:
            feature_list.append(self.data.purchase_redeem_map[feature_date][0])#purchase value
            feature_list.append(self.data.purchase_redeem_map[feature_date][1])#redeem value
            #for k in range(1, 3):
            #    feature_list.append(self.data.taobao_day_map[feature_date][k])
            #for k in range(1, 9):
            #    feature_list.append(self.data.bank_day_map[feature_date][k])
            feature_date = add_day(feature_date)
            i += 1
        #print "feature: " + str(feature_list)
        return feature_list

    def train_target_index(self, index, model):
        train_x_map = {}
        train_x_list = []
        train_y = []
        #init data
        date_str = self.train_valid_date
        train_case_count = 0
        while True:
            date_str = add_day(date_str, -1)
            feature_list = self.build_feature(date_str)
            if not feature_list:
                break
            train_y.append(self.data.purchase_redeem_map[date_str][index])
            train_x_map[date_str] = feature_list
            train_case_count += 1
            if train_case_count >= self.max_train_case_num:
                break
        sorted_key_list = sorted(train_x_map.keys(), key= lambda x: x, reverse=False)
        for key in sorted_key_list:
            train_x_list.append(train_x_map[key])
        model.fit(train_x_list, train_y)

    def train_purchase(self):
        self.train_target_index(0, self.purchase_model)

    def train_redeem(self):
        self.train_target_index(1, self.redeem_model)

    def predict(self, begin_date, end_date):
        predict_map = {}
        predict_date = begin_date
        feature_list = self.build_feature(begin_date)
        while predict_date != end_date:
            predict_map[predict_date] = [0, 0]
            predict_map[predict_date][0] = int(self.purchase_model.predict(feature_list))
            predict_map[predict_date][1] = int(self.redeem_model.predict(feature_list))
            #update feature for next date
            feature_list.pop(1)
            feature_list.pop(0)
            feature_list.append(predict_map[predict_date][0])
            feature_list.append(predict_map[predict_date][1])
            predict_date = add_day(predict_date)
        return predict_map

class EqualFeatureRegressionPredictor(Predictor):
    def __init__(self, data_container, mtc_num = 180, fbt_num = 21):
        Predictor.__init__(self, data_container)
        #self.purchase_model_list = [Lasso(alpha=a1) for i in xrange(MAX_PREDICT_DAY_NUM)]
        #self.redeem_model_list = [Lasso(alpha=a2) for i in xrange(MAX_PREDICT_DAY_NUM)]
        self.purchase_model_list = [svm.SVR() for i in xrange(MAX_PREDICT_DAY_NUM)]
        self.redeem_model_list = [svm.SVR() for i in xrange(MAX_PREDICT_DAY_NUM)]
        self.feature_back_trace_day_num = fbt_num
        self.max_train_case_num = mtc_num

    def get_map_feature_latest(self, m, date_str):
        count = 0
        sub_str = date_str
        while True:
            if m.has_key(sub_str):
                return m[sub_str]
            sub_str = add_day(sub_str, -1)
            count += 1
            if count > 10:
                break
        return None

    def build_feature(self, target_date_str, back_day_num = 0):
        feature_begin_date = add_day(target_date_str, -1 * (self.feature_back_trace_day_num + back_day_num))
        if not self.data.purchase_redeem_map.has_key(feature_begin_date):
            return None
        feature_list = []
        feature_date = feature_begin_date
        i = 0
        while i < self.feature_back_trace_day_num:
            feature_list.append(self.math_log(self.data.purchase_redeem_map[feature_date][0]))#purchase value
            feature_list.append(self.math_log(self.data.purchase_redeem_map[feature_date][1]))#redeem value
            taobao_list = self.get_map_feature_latest(self.data.taobao_day_map, feature_date)
            bank_list = self.get_map_feature_latest(self.data.bank_day_map, feature_date)
            for k in range(1, 3):
                feature_list.append(float(taobao_list[k]))
            for k in range(1, 9):
                feature_list.append(float(bank_list[k]))
            feature_date = add_day(feature_date)
            i += 1
        #print "feature: " + str(feature_list)
        return feature_list

    def train_target_index(self, index, model_list):
        date_str = self.train_valid_date
        #build init feature
        date_feature_map = {}
        train_case_count = 0
        while True:
            date_str = add_day(date_str, -1)
            feature_list = self.build_feature(date_str)
            if not feature_list:
                break
            date_feature_map[date_str] = feature_list
            train_case_count += 1
            if train_case_count >= self.max_train_case_num:
                break
        for model_index in range(0, MAX_PREDICT_DAY_NUM):
            if model_index > 0:
                #update feature
                for case_date in date_feature_map.keys():
                    new_feature_value = model_list[model_index - 1].predict(date_feature_map[case_date])
                    date_feature_map[case_date].append(new_feature_value)
            train_x_list = []
            train_y = []
            for d in date_feature_map.keys():
                t_date = add_day(d, model_index)
                if int(t_date) >= int(self.train_valid_date):
                    continue
                train_x_list.append(date_feature_map[d])
                train_y.append(self.math_log(self.data.purchase_redeem_map[t_date][index]))
            model_list[model_index].fit(train_x_list, train_y)

    def train_purchase(self):
        self.train_target_index(0, self.purchase_model_list)

    def train_redeem(self):
        self.train_target_index(1, self.redeem_model_list)

    def predict(self, begin_date_str, end_date_str):
        predict_map = {}
        c_date = begin_date_str
        while int(c_date) < int(end_date_str):
            predict_date = c_date
            end_date = add_day(c_date, MAX_PREDICT_DAY_NUM)
            if int(end_date) > int(end_date_str):
                end_date = end_date_str
            purchase_feature_list = self.build_feature(predict_date)
            redeem_feature_list = self.build_feature(predict_date)
            model_index = 0
            while predict_date != end_date:
                predict_map[predict_date] = [0, 0]
                purchase_p = self.purchase_model_list[model_index].predict(purchase_feature_list)
                redeem_p = self.redeem_model_list[model_index].predict(redeem_feature_list)
                predict_map[predict_date][0] = int(self.math_exp(purchase_p))
                predict_map[predict_date][1] = int(self.math_exp(redeem_p))
                purchase_feature_list.append(purchase_p)
                redeem_feature_list.append(redeem_p)
                predict_date = add_day(predict_date)
                model_index += 1
                if model_index >= MAX_PREDICT_DAY_NUM:
                    break
            c_date = add_day(c_date, MAX_PREDICT_DAY_NUM)
        return predict_map


class FrequencyRegressionPredictor(Predictor):
    def __init__(self, data_container, mtc_num = 180, fbt_num = 21, fft_num = 21):
        Predictor.__init__(self, data_container)
        #self.purchase_model_list = [Lasso(alpha=a1) for i in xrange(MAX_PREDICT_DAY_NUM)]
        #self.redeem_model_list = [Lasso(alpha=a2) for i in xrange(MAX_PREDICT_DAY_NUM)]
        self.purchase_model_list = [svm.SVR() for i in xrange(MAX_PREDICT_DAY_NUM)]
        self.redeem_model_list = [svm.SVR() for i in xrange(MAX_PREDICT_DAY_NUM)]
        self.feature_back_trace_day_num = fbt_num
        self.max_train_case_num = mtc_num
        self.max_fft_day_num = fft_num

    def get_map_feature_latest(self, m, date_str):
        count = 0
        sub_str = date_str
        while True:
            if m.has_key(sub_str):
                return m[sub_str]
            sub_str = add_day(sub_str, -1)
            count += 1
            if count > 10:
                break
        return None

    def get_fft_list(self, feature_list, max_num = -1):
        if max_num > 0 and max_num < len(feature_list):
            feature_list = feature_list[len(feature_list) - max_num:]
        N = len(feature_list)
        ori_list = np.array(feature_list)
        fft_list = np.fft.fft(ori_list)/N
        ret_list = []
        for i in range(0, N):
            ret_list.append(plural_to_real(fft_list[i]))
        return ret_list

    def build_time_feature(self, target_date_str, index):
        feature_begin_date = add_day(target_date_str, -1 * (self.max_fft_day_num))
        if not self.data.purchase_redeem_map.has_key(feature_begin_date):
            return None
        feature_list = []
        feature_date = feature_begin_date
        i = 0
        while i < self.max_fft_day_num:
            feature_list.append(self.math_log(self.data.purchase_redeem_map[feature_date][index]))
            feature_date = add_day(feature_date)
            i += 1
        return feature_list

    def build_normal_feature(self, target_date_str, back_day_num = 0):
        feature_begin_date = add_day(target_date_str, -1 * (self.feature_back_trace_day_num + back_day_num))
        if not self.data.purchase_redeem_map.has_key(feature_begin_date):
            return None
        feature_list = []
        feature_date = feature_begin_date
        i = 0
        while i < self.feature_back_trace_day_num:
            feature_list.append(self.math_log(self.data.purchase_redeem_map[feature_date][0]))#purchase value
            feature_list.append(self.math_log(self.data.purchase_redeem_map[feature_date][1]))#redeem value
            taobao_list = self.get_map_feature_latest(self.data.taobao_day_map, feature_date)
            bank_list = self.get_map_feature_latest(self.data.bank_day_map, feature_date)
            for k in range(1, 3):
                feature_list.append(float(taobao_list[k]))
            for k in range(1, 9):
                feature_list.append(float(bank_list[k]))
            feature_date = add_day(feature_date)
            i += 1
        #print "feature: " + str(feature_list)
        return feature_list

    def train_target_index(self, index, model_list):
        date_str = self.train_valid_date
        #build init feature
        date_feature_map = {}
        time_feature_map = {}
        train_case_count = 0
        while True:
            date_str = add_day(date_str, -1)
            feature_list = self.build_normal_feature(date_str)
            time_feature_list = self.build_time_feature(date_str, index)
            if (not feature_list) or (not time_feature_list):
                break
            time_feature_map[date_str] = time_feature_list
            date_feature_map[date_str] = feature_list
            train_case_count += 1
            if train_case_count >= self.max_train_case_num:
                break
        for model_index in range(0, MAX_PREDICT_DAY_NUM):
            if model_index > 0:
                #update feature
                for case_date in date_feature_map.keys():
                    new_l = date_feature_map[case_date] + self.get_fft_list(time_feature_map[case_date], self.max_fft_day_num)
                    new_feature_value = model_list[model_index - 1].predict(new_l)
                    date_feature_map[case_date].append(new_feature_value)
                    time_feature_map[case_date].append(new_feature_value)
            train_x_list = []
            train_y = []
            for d in date_feature_map.keys():
                t_date = add_day(d, model_index)
                if int(t_date) >= int(self.train_valid_date):
                    continue
                use_feature = date_feature_map[d] + self.get_fft_list(time_feature_map[d], self.max_fft_day_num)
                train_x_list.append(use_feature)
                train_y.append(self.math_log(self.data.purchase_redeem_map[t_date][index]))
            model_list[model_index].fit(train_x_list, train_y)

    def train_purchase(self):
        self.train_target_index(0, self.purchase_model_list)

    def train_redeem(self):
        self.train_target_index(1, self.redeem_model_list)

    def predict(self, begin_date_str, end_date_str):
        predict_map = {}
        c_date = begin_date_str
        while int(c_date) < int(end_date_str):
            predict_date = c_date
            end_date = add_day(c_date, MAX_PREDICT_DAY_NUM)
            if int(end_date) > int(end_date_str):
                end_date = end_date_str
            purchase_feature_list = self.build_normal_feature(predict_date)
            redeem_feature_list = self.build_normal_feature(predict_date)
            purchase_time_list = self.build_time_feature(predict_date, 0)
            redeem_time_list = self.build_time_feature(predict_date, 1)
            model_index = 0
            while predict_date != end_date:
                predict_map[predict_date] = [0, 0]
                use_p = purchase_feature_list + self.get_fft_list(purchase_time_list, self.max_fft_day_num)
                use_r = redeem_feature_list + self.get_fft_list(redeem_time_list, self.max_fft_day_num)
                purchase_p = self.purchase_model_list[model_index].predict(use_p)
                redeem_p = self.redeem_model_list[model_index].predict(use_r)
                predict_map[predict_date][0] = int(self.math_exp(purchase_p))
                predict_map[predict_date][1] = int(self.math_exp(redeem_p))
                purchase_feature_list.append(purchase_p)
                redeem_feature_list.append(redeem_p)
                purchase_time_list.append(purchase_p)
                redeem_time_list.append(redeem_p)
                predict_date = add_day(predict_date)
                model_index += 1
                if model_index >= MAX_PREDICT_DAY_NUM:
                    break
            c_date = add_day(c_date, MAX_PREDICT_DAY_NUM)
        return predict_map

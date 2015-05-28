__author__ = 'wangchao'


from money_flow_predictor import *

ZERO_USER_ITEM = UserDayItem(-1, "20010101","0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0")

class UniformUserSumPredictor(Predictor):
    def __init__(self, data_container, mtc_num = 180, fbt_num = 21):
        Predictor.__init__(self, data_container)
        self.feature_back_trace_day_num = fbt_num
        self.max_train_case_num = mtc_num
        #self.user_model_map = {}
        #for uid in self.data.user_list:
        #    self.user_model_map[uid] = [[svm.SVR() for i in range(0, MAX_PREDICT_DAY_NUM)] for j in range(0, 2)]
        self.user_model = [svm.SVR() for j in range(0, 2)]
        self.purchase_model_list = [svm.SVR() for i in xrange(MAX_PREDICT_DAY_NUM)]
        self.redeem_model_list = [svm.SVR() for i in xrange(MAX_PREDICT_DAY_NUM)]

    def get_user_item_feature(self, m, date_str):
        uitem = ZERO_USER_ITEM
        if m.has_key(date_str):
            uitem = m[date_str]
        u_feature_list = []
        for i in range(2, len(uitem)):
            u_feature_list.append(math_log(float(uitem[i])))
        return u_feature_list

    def build_feature_for_user(self, uid, target_date_str, back_day_num = 0):
        feature_begin_date = add_day(target_date_str, -1 * (self.feature_back_trace_day_num + back_day_num))
        feature_list = []
        feature_date = feature_begin_date
        i = 0
        while i < self.feature_back_trace_day_num:
            feature_list.append(get_week(feature_date))
            u_feature_list = self.get_user_item_feature(self.data.user_action_map[uid], feature_date)
            for f in u_feature_list:
                feature_list.append(f)
            taobao_list = get_map_feature_latest(self.data.taobao_day_map, feature_date)
            bank_list = get_map_feature_latest(self.data.bank_day_map, feature_date)
            for k in range(1, 3):
                feature_list.append(float(taobao_list[k]))
            for k in range(1, 9):
                feature_list.append(float(bank_list[k]))
            feature_date = add_day(feature_date)
            i += 1
        return feature_list


    def train_purchase(self):
        self.train_target_index(0, self.purchase_model_list)

    def train_redeem(self):
        self.train_target_index(1, self.redeem_model_list)

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

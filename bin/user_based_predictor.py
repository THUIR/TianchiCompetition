__author__ = 'wangchao'


from money_flow_predictor import *

ZERO_USER_ITEM = UserDayItem(-1, "20010101","0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0")

class UniformUserSumPredictor(Predictor):
    def __init__(self, data_container, mtc_num = 60, fbt_num = 21):
        Predictor.__init__(self, data_container)
        self.feature_back_trace_day_num = fbt_num
        self.max_train_case_num = mtc_num
        #self.user_model_map = {}
        #for uid in self.data.user_list:
        #    self.user_model_map[uid] = [[svm.SVR() for i in range(0, MAX_PREDICT_DAY_NUM)] for j in range(0, 2)]
        #self.user_model = [svm.SVR() for j in range(0, 2)]
        self.purchase_model_list = [svm.SVR() for i in xrange(MAX_PREDICT_DAY_NUM)]
        self.redeem_model_list = [svm.SVR() for i in xrange(MAX_PREDICT_DAY_NUM)]

    def get_user_item_feature(self, m, date_str):
        uitem = ZERO_USER_ITEM
        if m.has_key(date_str):
            uitem = m[date_str]
        u_feature_list = []
        #print str(uitem)
        for i in range(2, len(uitem)):
            u_feature_list.append(math_log(safe_float(uitem[i])))
        return u_feature_list

    def is_valid_user_item_date(self, uid, date_str):
        return self.data.user_action_map.has_key(uid) and self.data.user_action_map[uid].has_key(date_str)

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
        user_date_feature_map = {}
        for uid in self.data.user_list:
            user_date_feature_map[uid] = {}
        train_case_count = 0
        print "process user feature map"
        while True:
            date_str = add_day(date_str, -1)
            for uid in self.data.user_list:
                feature_list = self.build_feature_for_user(uid, date_str)
                user_date_feature_map[uid][date_str] = feature_list
            train_case_count += 1
            print "train_case_count: " + str(train_case_count)
            if train_case_count >= self.max_train_case_num:
                break
        for model_index in range(0, MAX_PREDICT_DAY_NUM):
            print "train model_index " + str(model_index)
            if model_index > 0:
                #update feature
                for uid in self.data.user_list:
                    for case_date in user_date_feature_map[uid].keys():
                        new_l = user_date_feature_map[uid][case_date]
                        new_feature_value = model_list[model_index - 1].predict(new_l)
                        user_date_feature_map[uid][case_date].append(new_feature_value)
            train_x_list = []
            train_y = []
            for uid in self.data.user_list:
                for d in user_date_feature_map[uid].keys():
                    t_date = add_day(d, model_index)
                    if int(t_date) >= int(self.train_valid_date):
                        continue
                    use_feature = user_date_feature_map[uid][d]
                    if self.is_valid_user_item_date(uid, t_date):
                        train_x_list.append(use_feature)
                        if index == 0:
                            train_y.append(self.math_log(self.data.user_action_map[uid][t_date].total_purchase_amt))
                        else:
                            train_y.append(self.math_log(self.data.user_action_map[uid][t_date].total_redeem_amt))
            model_list[model_index].fit(train_x_list, train_y)

    def predict(self, begin_date_str, end_date_str):
        predict_map = {}
        c_date = begin_date_str
        while int(c_date) < int(end_date_str):
            predict_date = c_date
            end_date = add_day(c_date, MAX_PREDICT_DAY_NUM)
            if int(end_date) > int(end_date_str):
                end_date = end_date_str
            for uid in self.data.user_list:
                purchase_feature_list = self.build_feature_for_user(uid, predict_date)
                redeem_feature_list = self.build_feature_for_user(uid, predict_date)
                model_index = 0
                tmp_date = predict_date
                while tmp_date != end_date:
                    if not predict_map.has_key(tmp_date):
                        predict_map[tmp_date] = [0, 0]
                    use_p = purchase_feature_list
                    use_r = redeem_feature_list
                    purchase_p = self.purchase_model_list[model_index].predict(use_p)
                    redeem_p = self.redeem_model_list[model_index].predict(use_r)
                    predict_map[tmp_date][0] += int(self.math_exp(purchase_p))
                    predict_map[tmp_date][1] += int(self.math_exp(redeem_p))
                    purchase_feature_list.append(purchase_p)
                    redeem_feature_list.append(redeem_p)
                    tmp_date = add_day(tmp_date)
                    model_index += 1
                    if model_index >= MAX_PREDICT_DAY_NUM:
                        break
            c_date = add_day(c_date, MAX_PREDICT_DAY_NUM)
        return predict_map
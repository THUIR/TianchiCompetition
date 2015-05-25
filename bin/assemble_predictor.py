__author__ = 'wangchao'

from money_flow_predictor import *

from pycast_predictor import ExponentialSmoothingPredictor,HoltMethodPredictor,HoltWintersPredictor

class SimpleAssemblePredictor(Predictor):
    def __init__(self, data_container, assemble_case_num = 90):
        Predictor.__init__(self, data_container)
        #self.purchase_model_list = [SimpleRegressionPredictor(data_container), FrequencyRegressionPredictor(data_container), EqualFeatureRegressionPredictor(data_container), ExponentialSmoothingPredictor(data_container), HoltMethodPredictor(data_container), HoltWintersPredictor(data_container)]
        #self.redeem_model_list = [SimpleRegressionPredictor(data_container), FrequencyRegressionPredictor(data_container), EqualFeatureRegressionPredictor(data_container), ExponentialSmoothingPredictor(data_container), HoltMethodPredictor(data_container), HoltWintersPredictor(data_container)]
        self.purchase_model_list = [SimpleRegressionPredictor(data_container), FrequencyRegressionPredictor(data_container), EqualFeatureRegressionPredictor(data_container), ExponentialSmoothingPredictor(data_container)]
        self.redeem_model_list = [SimpleRegressionPredictor(data_container), FrequencyRegressionPredictor(data_container), EqualFeatureRegressionPredictor(data_container), ExponentialSmoothingPredictor(data_container)]

        self.assemble_case_num = assemble_case_num
        self.purchase_model_fit = svm.SVR()
        self.redeem_model_fit = svm.SVR()
        #self.purchase_model_fit = Lasso(alpha=0.05)
        #self.redeem_model_fit = Lasso(alpha=0.05)

    def train_target_index(self, index, model_list, fit_model):
        end_date_str = self.train_valid_date
        begin_date_str = add_day(self.train_valid_date, -1 * self.assemble_case_num)
        results_list = self.generate_results_list(model_list, begin_date_str, end_date_str)
        train_x = []
        train_y = []
        c_date = begin_date_str
        while not c_date == end_date_str:
            feature_list = []
            for i in range(0, len(results_list)):
                feature_list.append(self.math_log(results_list[i][c_date][index]))
            #print "feature: " + str(feature_list) + str(self.math_log(self.data.purchase_redeem_map[c_date][index]))
            train_x.append(feature_list)
            train_y.append(self.math_log(self.data.purchase_redeem_map[c_date][index]))
            c_date = add_day(c_date)
        fit_model.fit(train_x, train_y)
        #print "model param: " + str(fit_model.coef_)

    def generate_results_list(self, model_list, begin_date_str, end_date_str):
        results_list = []
        for model in model_list:
            results_list.append(model.predict(begin_date_str, end_date_str))
        return results_list

    def train_purchase(self):
        for sub_model in self.purchase_model_list:
            #sub_model.train(add_day(self.train_valid_date, -1 * self.assemble_case_num))
            sub_model.train(add_day(self.train_valid_date, 0))
        self.train_target_index(0, self.purchase_model_list, self.purchase_model_fit)

    def train_redeem(self):
        for sub_model in self.redeem_model_list:
            #sub_model.train(add_day(self.train_valid_date, -1 * self.assemble_case_num))
            sub_model.train(add_day(self.train_valid_date, 0))
        self.train_target_index(1, self.redeem_model_list, self.redeem_model_fit)

    def predict(self, begin_date, end_date):
        purchase_results_list = self.generate_results_list(self.purchase_model_list, begin_date, end_date)
        redeem_results_list = self.generate_results_list(self.redeem_model_list, begin_date, end_date)
        predict_map = {}
        predict_date = begin_date
        while predict_date != end_date:
            predict_map[predict_date] = [0, 0]
            purchase_feature_list = []
            for i in range(0, len(self.purchase_model_list)):
                purchase_feature_list.append(self.math_log(purchase_results_list[i][predict_date][0]))
            #print "predict: " + str(purchase_feature_list)
            redeem_feature_list = []
            for i in range(0, len(self.redeem_model_list)):
                redeem_feature_list.append(self.math_log(redeem_results_list[i][predict_date][1]))
            predict_map[predict_date][0] = int(self.math_exp(self.purchase_model_fit.predict(purchase_feature_list)))
            predict_map[predict_date][1] = int(self.math_exp(self.redeem_model_fit.predict(redeem_feature_list)))
            predict_date = add_day(predict_date)
        return predict_map
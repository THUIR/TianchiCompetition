__author__ = 'wangchao'

from wc_competition_common import *

from assemble_predictor import *


def wc_test_model(data_container, model_name, begin_date, day_length, save_output_file_name = None):
    end_date = add_day(begin_date, day_length)
    choose_model = getattr(sys.modules["__main__"], model_name)(data_container)
    print "training..."
    choose_model.train(begin_date)
    print "testing..."
    result_str = choose_model.test_performance(begin_date, end_date)
    if save_output_file_name:
        out_file = open(save_output_file_name, "w")
        out_file.write(result_str)
        out_file.close()

def wc_use_model(data_container, model_name, begin_date, day_length, save_file_name):
    end_date = add_day(begin_date, day_length)
    choose_model = getattr(sys.modules["__main__"], model_name)(data_container)
    print "training..."
    choose_model.train(begin_date)
    print "predicting..."
    predict_results = choose_model.predict(begin_date, end_date)
    save_map(predict_results, None, save_file_name)

if __name__ == '__main__':
    data_dir = "../data"
    data_begin_date = "20130701"
    data_end_date = "20140901"
    #user_day_item_list = load_items(data_dir + "/sample_user_balance.csv", "UserDayItem")
    user_day_item_list = load_items(data_dir + "/user_balance_table.csv", "UserDayItem")
    user_profile_map = load_map_items(load_items(data_dir + "/user_profile_table_gbk.csv", "UserProfileItem"))
    taobao_day_map = load_map_items(load_items(data_dir + "/mfd_day_share_interest.csv", "TaobaoDayItem"))
    bank_day_map = load_map_items(load_items(data_dir + "/mfd_bank_shibor.csv", "BankDayItem"))

    #pr_map = build_purchase_redeem_map(data_begin_date, data_end_date, user_day_item_list)
    #save_map(pr_map, ["date", "total_purchase", "total_redeem"], data_dir + "/wc_total_pr.csv")
    pr_map = load_map_list(data_dir + "/wc_total_pr.csv")

    data_container = DataContainer(user_day_item_list, pr_map, user_profile_map, taobao_day_map, bank_day_map)

    day_length = 30
    test_begin_date = "20140801"
    test_month = 4

    for i in range(0, test_month):
        #wc_test_model(data_container, "NaivePredictor", test_begin_date, day_length)
        #wc_test_model(data_container, "SimpleRegressionPredictor", test_begin_date, day_length)
        #wc_test_model(data_container, "EqualFeatureRegressionPredictor", test_begin_date, day_length, data_dir + "/test_efr_" + test_begin_date +".txt")
        #wc_test_model(data_container, "SimpleAssemblePredictor", test_begin_date, day_length, data_dir + "/test_sa_w_" + test_begin_date +".txt")
        #wc_test_model(data_container, "FrequencyRegressionPredictor", test_begin_date, day_length, data_dir + "/test_frp_m_" + test_begin_date +".txt")
        #wc_test_model(data_container, "ExponentialSmoothingPredictor", test_begin_date, day_length, data_dir + "/test_esp_e_" + test_begin_date +".txt")
        #wc_test_model(data_container, "HoltMethodPredictor", test_begin_date, day_length, data_dir + "/test_hmp_mape_" + test_begin_date +".txt")
        #wc_test_model(data_container, "HoltWintersPredictor", test_begin_date, day_length, data_dir + "/test_hwp_i" + test_begin_date +".txt")
        test_begin_date = add_month(test_begin_date, -1)

    use_predict_begin_date = "20140901"
    #wc_use_model(data_container, "SimpleRegressionPredictor", use_predict_begin_date, day_length, data_dir + "/wc_simple_regression_prediction2.csv")
    #wc_use_model(data_container, "EqualFeatureRegressionPredictor", use_predict_begin_date, day_length, data_dir + "/wc_EqualFeatureRegressionPredictor.csv")
    wc_use_model(data_container, "SimpleAssemblePredictor", use_predict_begin_date, day_length, data_dir + "/wc_SimpleAssemblePredictor_i.csv")
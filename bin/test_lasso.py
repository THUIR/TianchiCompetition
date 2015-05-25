__author__ = 'wangchao'


from sklearn.linear_model import Lasso

model = Lasso(alpha=0.1)

train_x = [[1, 2, 3], [2, 3, 4], [3, 4, 5]]
train_y = [6.6, 7.3, 8.9]

model.fit(train_x, train_y)

#test_x = [[1.5, 2.5, 3.5], [2.5, 3.5, 4.5]]
test_x = [1.5, 2.5, 3.5]
test_y = model.predict(test_x)

print str(test_y)
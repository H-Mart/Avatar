from src.training import compile_sklearn_model
from itertools import product

if __name__ == '__main__':
    data = compile_sklearn_model.ready_data()
    estimators = [5, 10, 20, 50, 75, 100]
    depth = [1, 2, 4, 8, 16, 32]
    for e, d in product(estimators, depth):
        compile_sklearn_model.train_model(data, e, d)

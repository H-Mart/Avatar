from src.training import compile_sklearn_model, evaluate_models
from itertools import product


def train_models(data):
    estimators = [20, 50, 75, 100, 200, 400, 800]
    depth = [16, 20, 24, 28, 32, 64, 128, None]
    criteria = ['gini', 'entropy', 'log_loss']
    for e, d, c in product(estimators, depth, criteria):
        compile_sklearn_model.train_model(data, e, d, c)


if __name__ == '__main__':
    data = compile_sklearn_model.ready_data()

    train_models(data)
    evaluate_models.evaluate(data)
    evaluate_models.plot_heatmaps()

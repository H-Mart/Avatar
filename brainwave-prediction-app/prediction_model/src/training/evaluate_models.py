import pickle
import matplotlib.pyplot as plt
import numpy as np
import colorsys

from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, log_loss, confusion_matrix

from .compile_sklearn_model import ready_data, load_model
from ..data_processing import config


def get_contrasting_color(rgb, as_hex=False):
    # chatGPT fueled experiment

    # Convert RGB to [0, 1] range
    r, g, b = [x / 255.0 for x in rgb]

    # Convert RGB to HSV
    h, s, v = colorsys.rgb_to_hsv(r, g, b)

    # Adjust hue by 180 degrees (0.5 in [0, 1] range) to get complementary color
    h = (h + 0.5) % 1.0

    # Convert back to RGB
    r2, g2, b2 = colorsys.hsv_to_rgb(h, s, v)

    # Convert [0, 1] range back to [0, 255]
    if as_hex:
        return f'#{int(r2 * 255):02X}{int(g2 * 255):02X}{int(b2 * 255):02X}'
    else:
        return tuple(int(x * 255) for x in (r2, g2, b2))


def load_models():
    models = [load_model(p) for p in config.model_save_dir_path.iterdir()]
    return models


def evaluate_model(model: RandomForestClassifier, data, normalize_cm='all') -> tuple[
    int, int, float, float, np.ndarray, str]:
    estimator_count = model.get_params()['n_estimators']
    max_depth = model.get_params()['max_depth'] or 0  # max_depth can be None but not 0
    criterion = model.get_params()['criterion']

    y_pred = model.predict(data.X_test)
    y_proba = model.predict_proba(data.X_test)

    accuracy = accuracy_score(data.y_test, y_pred)
    loss = log_loss(data.y_test, y_proba)
    cm = confusion_matrix(data.y_test, y_pred, normalize=normalize_cm)

    return estimator_count, max_depth, accuracy, loss, cm, criterion


def save_stats(stats: dict):
    stats_data_dir = config.model_stats_path / 'stats_data'
    stats_data_dir.mkdir(parents=True, exist_ok=True)

    # pickle the data
    with (stats_data_dir / 'stats.pkl').open('wb') as f:
        pickle.dump(stats, f)


def load_saved() -> tuple[dict[str, dict[str, np.ndarray]], np.ndarray, np.ndarray, np.ndarray, list]:
    with (config.model_stats_path / 'stats_data' / 'stats.pkl').open('rb') as f:
        stats = pickle.load(f)

    stats_by_criteria = stats['stats_by_criteria']
    estimator_counts = stats['estimator_counts']
    max_depths = stats['max_depths']
    labels = stats['labels']
    criteria = stats['criteria']

    return stats_by_criteria, estimator_counts, max_depths, labels, criteria


def plot_accuracy_heatmap(acc, estimator_counts, max_depths, criterion):
    fig, ax = plt.subplots()
    cmap = plt.get_cmap("inferno")
    cmap.set_under("white")

    cax = ax.imshow(acc, cmap=cmap, interpolation='nearest',
                    vmin=.8, vmax=1, origin='lower',
                    extent=(0, len(max_depths), 0, len(estimator_counts)))

    fig.colorbar(cax)
    for i in range(acc.shape[0]):  # rows (estimators)
        for j in range(acc.shape[1]):  # columns (depths)
            value = acc[i, j]
            text_color = get_contrasting_color(cmap(value, bytes=True)[:3], as_hex=True) \
                if value > .8 else 'black'

            ax.text(j + .5, i + .5, f"{value:.4f}",
                    ha="center", va="center", color=text_color)

    ax.set_title(f'Accuracy vs Number of Estimators and Max Depth with Criterion: {criterion}', fontsize=8, pad=2)
    ax.set_xlabel('Max Depth')
    ax.set_ylabel('Number of Estimators')
    ax.set_xticks(np.arange(len(max_depths)) + .5, max_depths)
    ax.set_yticks(np.arange(len(estimator_counts)) + .5, estimator_counts)

    plot_save_path = config.model_stats_path / 'plots' / criterion / f'{criterion}_accuracy_heatmap.png'
    plot_save_path.parent.mkdir(parents=True, exist_ok=True)

    plt.savefig(plot_save_path)


def plot_loss_heatmap(loss, estimator_counts, max_depths, criterion):
    fig, ax = plt.subplots()
    cmap = plt.get_cmap("inferno").reversed()
    cmap.set_over("white")

    cax = ax.imshow(loss, cmap=cmap, interpolation='nearest',
                    vmin=0, vmax=.2, origin='lower',
                    extent=(0, len(max_depths), 0, len(estimator_counts)))

    fig.colorbar(cax)
    for i in range(loss.shape[0]):  # rows (estimators)
        for j in range(loss.shape[1]):  # columns (depths)
            value = loss[i, j]
            text_color = get_contrasting_color(cmap(value, bytes=True)[:3], as_hex=True) \
                if value < .2 else 'black'

            ax.text(j + .5, i + .5, f"{value:.4f}",
                    ha="center", va="center", color=text_color)

    ax.set_title(f'Loss vs Number of Estimators and Max Depth with Criterion: {criterion}', fontsize=8, pad=2)
    ax.set_xlabel('Max Depth')
    ax.set_ylabel('Number of Estimators')
    ax.set_xticks(np.arange(len(max_depths)) + .5, max_depths)
    ax.set_yticks(np.arange(len(estimator_counts)) + .5, estimator_counts)

    plot_save_path = config.model_stats_path / 'plots' / criterion / f'{criterion}_loss_heatmap.png'
    plot_save_path.parent.mkdir(parents=True, exist_ok=True)

    plt.savefig(plot_save_path)


def plot_confusion_matrix(cm_matrix, labels, criterion):
    m, n, k, _ = cm_matrix.shape

    fig, axes = plt.subplots(m, n, figsize=(20, 20))

    for i in range(m):  # rows (estimators)
        for j in range(n):  # columns (depths)
            cm = cm_matrix[i, j, :, :]
            ax = axes[i, j]

            cax = ax.imshow(cm, cmap='viridis', interpolation='nearest',
                            extent=(0, len(labels), 0, len(labels)),
                            origin='upper')

            for x in range(cm.shape[0]):  # rows (true labels)
                for y in range(cm.shape[1]):  # columns (predicted labels)
                    value = cm[y, x]
                    text_color = get_contrasting_color(cax.cmap(value, bytes=True)[:3], as_hex=True)

                    # imshow's upper left corner has coordinates (0, k), so we need to flip the y-axis
                    ax.text(y + .5, k - (x + .5), f"{value:.5f}",
                            ha="center", va="center", color=text_color, fontsize=4)

            ax.set_yticks(k - (np.arange(len(labels)) + .5), labels, fontsize=4)
            ax.set_xticks(np.arange(len(labels)) + .5, labels, fontsize=4, )
            ax.set_xlabel('Predicted', fontsize=6)
            ax.set_ylabel('True', fontsize=6)
            ax.set_title(f'E:{i}, D:{j}', fontsize=8, pad=2, y=-.1)
            ax.xaxis.tick_top()
            ax.xaxis.set_label_position('top')

    plt.tight_layout(pad=3)
    fig.colorbar(cax, ax=axes.ravel().tolist())

    plot_save_path = config.model_stats_path / 'plots' / criterion / f'{criterion}_confusion_matrix.png'
    plot_save_path.parent.mkdir(parents=True, exist_ok=True)

    plt.savefig(plot_save_path)


def plot_heatmaps():
    stats, estimator_counts, max_depths, labels, criteria = load_saved()

    for c in criteria:
        plot_accuracy_heatmap(stats[c]['accuracy_matrix'], estimator_counts, max_depths, c)
        plot_loss_heatmap(stats[c]['loss_matrix'], estimator_counts, max_depths, c)
        plot_confusion_matrix(stats[c]['cm_matrix'], labels, c)


def evaluate(data=None):
    models = load_models()
    data = data or ready_data()

    estimator_counts = sorted(list({model.get_params()['n_estimators'] for model in models}))
    max_depths = sorted(list({(model.get_params()['max_depth'] or 0) for model in models}))
    criteria = {model.get_params()['criterion'] for model in models}

    labels = np.array(list(data.label_map.values()))

    stats_by_criteria = {c: {} for c in criteria}

    for c in criteria:
        stats_by_criteria[c]['accuracy_matrix'] = np.zeros((len(estimator_counts), len(max_depths)))
        stats_by_criteria[c]['loss_matrix'] = np.zeros((len(estimator_counts), len(max_depths)))
        stats_by_criteria[c]['cm_matrix'] = np.zeros(
            (len(estimator_counts), len(max_depths), len(labels), len(labels)))  # lmao

    for model in models:
        estimator_count, max_depth, accuracy, loss, cm, criterion = evaluate_model(model, data)
        estimator_index = estimator_counts.index(estimator_count)
        depth_index = max_depths.index(max_depth)

        stats_by_criteria[criterion]['accuracy_matrix'][estimator_index, depth_index] = accuracy
        stats_by_criteria[criterion]['loss_matrix'][estimator_index, depth_index] = loss
        stats_by_criteria[criterion]['cm_matrix'][estimator_index, depth_index, :, :] = cm

    stats = {
        'estimator_counts': estimator_counts,
        'max_depths': max_depths,
        'labels': labels,
        'stats_by_criteria': stats_by_criteria,
        'criteria': criteria
    }

    save_stats(stats)


if __name__ == '__main__':
    evaluate()

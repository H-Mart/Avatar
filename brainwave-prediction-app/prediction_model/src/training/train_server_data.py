from ..brain_reading import receiver
from ..data_processing import config, load_data

from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import GroupKFold, cross_validate

import pandas as pd
import numpy as np


def split_on_trial(df: pd.DataFrame, frac):
    saved_rounds = pd.DataFrame(columns=['label', 'trial'])
    for label, group in df.groupby('label', sort=False):
        # select 10% of the rounds to take out of the training set
        label_rounds_to_take_out = pd.DataFrame(columns=['label', 'trial'])
        label_rounds_to_take_out['trial'] = group.trial.drop_duplicates().sample(frac=frac)
        label_rounds_to_take_out['label'] = label
        saved_rounds = pd.concat([saved_rounds, label_rounds_to_take_out])
    return saved_rounds


def split_on_session(df: pd.DataFrame, frac):
    saved_rounds = pd.DataFrame(columns=['label', 'trial'])
    for label, group in df.groupby('label', sort=False):
        # select 10% of the rounds to take out of the training set
        sessions_to_take_out = group.session.drop_duplicates().sample(frac=frac)
        session_rounds_to_take_out = pd.DataFrame(columns=['label', 'round'])
        session_rounds_to_take_out['trial'] = group[group.session.isin(sessions_to_take_out)].trial.drop_duplicates()
        session_rounds_to_take_out['label'] = label
        saved_rounds = pd.concat([saved_rounds, session_rounds_to_take_out])
    return saved_rounds


def train_test_split(dataframe: pd.DataFrame, split_on: str = 'round', frac: float = 0.1):
    if split_on == 'round':
        saved_rounds = split_on_trial(dataframe, frac=frac)
    elif split_on == 'session':
        saved_rounds = split_on_session(dataframe, frac=frac)
    else:
        raise ValueError('split_on must be either "round" or "session"')

    training_set = dataframe[~dataframe.trial.isin(saved_rounds.trial)]
    testing_set = dataframe[dataframe.trial.isin(saved_rounds.trial)]

    return training_set, testing_set


def main():
    df = load_data.load_data('#todo add path')
    df.sort_values(by=['session', 'round', ' Timestamp'], inplace=True)

    labels = ['left', 'right', 'takeoff', 'land', 'forward', 'backward']
    cols = [str(x) for x in df.columns if x.startswith(' EXG')]

    # filtered_df = filter_rounds(df)
    # filtered_df = remove_outliers(filtered_df)
    # filtered_df = make_freq_df(filtered_df, cols)
    group = 'round'

    training_set, testing_set = train_test_split(df, split_on=group, frac=0.2)

    X = training_set[cols].to_numpy().astype(np.float64)
    y = training_set['label'].map(lambda x: labels.index(x)).to_numpy()
    groups = training_set[group].to_numpy()

    gkf = GroupKFold(n_splits=5)
    clf = RandomForestClassifier(n_estimators=50)
    scoring = {'accuracy': 'accuracy'}
    cv_results = cross_validate(clf, X, y, groups=groups, cv=gkf, scoring=scoring, return_train_score=True, verbose=2,
                                n_jobs=-1, return_estimator=True)

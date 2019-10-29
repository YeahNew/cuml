#
# Copyright (c) 2019, NVIDIA CORPORATION.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#


def fit_kneighbors(m, x):
    m.fit(x)
    m.kneighbors(x)


def fit(m, x, y=None):
    m.fit(x) if y is None else m.fit(x, y)


def fit_transform(m, x):
    m.fit_transform(x)


def predict(m, x, y=None):
    m.predict(x) if y is None else m.predict(x, y)


def _fil_classification_setup(m, data, arg={}):
    from cuml.utils.import_utils import has_xgboost
    if has_xgboost():
        import xgboost as xgb
    else:
        raise ImportError("No XGBoost package found which is required for benchmarking FIL")
    import os 

    tmp_path = "./fil_models"
    if not os.path.exists(tmp_path):
        os.makedirs(tmp_path)

    # use maximum 1e6 rows to train the model 
    train_size = min(data[0].shape[0], 1000000)
    dtrain = xgb.DMatrix(data[0][:train_size, :], label=data[1][:train_size])
    params = {"silent": 1, "eval_metric": "error", "objective": "binary:logistic"}
    params.update(arg)

    max_depth = arg["max_depth"]
    num_rounds = arg["num_rounds"]
    n_features = data[0].shape[1]
    model_name = "xgb_" + str(max_depth) + "_" + str(num_rounds) + "_" + str(n_features) + "_" + str(train_size) + ".model"
    model_path = os.path.join(tmp_path, model_name)

    from pathlib import Path
    if Path(model_path).is_file():
        return m.load(model_path, algo=arg["algo"], output_class=arg["output_class"], threshold=arg["threshold"])

    bst = xgb.train(params, dtrain, num_rounds)
    bst.save_model(model_path)
    return m.load(model_path, algo=arg["algo"], output_class=arg["output_class"], threshold=arg["threshold"])

from typing import Any

import numpy as np
from sklearn.cluster import KMeans
from sklearn.ensemble import IsolationForest, RandomForestClassifier
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.metrics import accuracy_score, mean_squared_error, silhouette_score
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier

from app.modules.modeling.schemas import ModelRunRequest, ModelRunResponse


class ModelRunner:
    """受控算法注册表，不接受或执行用户提交的任意 Python 代码。"""

    def run(self, request: ModelRunRequest) -> ModelRunResponse:
        x = np.asarray(request.features, dtype=float)
        if x.ndim != 2 or not np.isfinite(x).all():
            raise ValueError("features 必须是无缺失的二维数值数组")
        algorithm = request.algorithm
        if algorithm == "kmeans":
            clusters = int(request.parameters.get("n_clusters", 2))
            if clusters < 2 or clusters >= len(x):
                raise ValueError("n_clusters 必须大于1且小于样本数")
            labels = KMeans(n_clusters=clusters, random_state=42, n_init="auto").fit_predict(x)
            score = silhouette_score(x, labels)
            return self._response(request, labels.tolist(), {"silhouette_score": float(score)}, "聚类轮廓系数越接近1，分组结构越清晰。")
        if algorithm == "isolation_forest":
            contamination = float(request.parameters.get("contamination", 0.05))
            labels = IsolationForest(contamination=contamination, random_state=42).fit_predict(x)
            anomaly_count = int(np.sum(labels == -1))
            return self._response(request, labels.tolist(), {"anomaly_count": float(anomaly_count), "anomaly_rate": anomaly_count / len(x)}, "预测值-1表示异常，1表示正常。")
        if request.target is None or len(request.target) != len(x):
            raise ValueError("监督学习算法必须提供与样本数一致的 target")
        y = np.asarray(request.target)
        if len(x) >= 6:
            x_train, x_test, y_train, y_test = train_test_split(
                x,
                y,
                test_size=request.test_size,
                random_state=42,
            )
        else:
            x_train = x_test = x
            y_train = y_test = y
        if algorithm == "linear_regression":
            model: Any = LinearRegression()
            model.fit(x_train, y_train)
            predictions = model.predict(x_test)
            metrics = {
                "rmse": float(mean_squared_error(y_test, predictions) ** 0.5),
                "r2": float(model.score(x_test, y_test)) if len(y_test) > 1 else 0.0,
            }
            importance = self._importance(request, model.coef_)
            return self._response(
                request,
                predictions.tolist(),
                metrics,
                "指标基于独立测试集评估；R²越接近1，回归预测效果越好。",
                len(x_train),
                len(x_test),
                importance,
            )
        classifiers = {
            "logistic_regression": LogisticRegression(max_iter=1000, random_state=42),
            "decision_tree": DecisionTreeClassifier(max_depth=int(request.parameters.get("max_depth", 5)), random_state=42),
            "random_forest": RandomForestClassifier(n_estimators=int(request.parameters.get("n_estimators", 100)), random_state=42),
        }
        model = classifiers[algorithm]
        model.fit(x_train, y_train)
        predictions = model.predict(x_test)
        raw_importance = getattr(model, "feature_importances_", getattr(model, "coef_", [[]]))
        if np.asarray(raw_importance).ndim > 1:
            raw_importance = np.mean(np.abs(raw_importance), axis=0)
        importance = self._importance(request, raw_importance)
        return self._response(
            request,
            predictions.tolist(),
            {"accuracy": float(accuracy_score(y_test, predictions))},
            "分类准确率基于独立测试集计算，并返回可用的特征重要性。",
            len(x_train),
            len(x_test),
            importance,
        )

    @staticmethod
    def _importance(request: ModelRunRequest, values: Any) -> dict[str, float]:
        flattened = np.asarray(values, dtype=float).reshape(-1)
        names = request.feature_names or [f"feature_{index + 1}" for index in range(len(flattened))]
        if len(names) != len(flattened):
            raise ValueError("feature_names 数量必须与特征列数一致")
        return {
            name: float(abs(value))
            for name, value in zip(names, flattened, strict=True)
        }

    @staticmethod
    def _response(
        request: ModelRunRequest,
        predictions: list,
        metrics: dict[str, float],
        explanation: str,
        train_count: int = 0,
        test_count: int = 0,
        feature_importance: dict[str, float] | None = None,
    ) -> ModelRunResponse:
        return ModelRunResponse(
            algorithm=request.algorithm,
            sample_count=len(request.features),
            metrics=metrics,
            predictions=predictions,
            train_count=train_count,
            test_count=test_count,
            feature_importance=feature_importance or {},
            explanation=explanation,
        )

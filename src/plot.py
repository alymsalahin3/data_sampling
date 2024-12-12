#
# SPDX-FileCopyrightText: Copyright (c) 1993-2023 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

import numpy as np
import matplotlib.pyplot as plt
from typing import Dict, Union

try:
    from cuml import TSNE
except ImportError:
    from sklearn.manifold import TSNE


def plot_tsne(
    x: np.ndarray,
    y: np.ndarray,
    counts: np.ndarray,
    min_size: int = 100,
    figsize: tuple = (20, 20),
    legend: bool = True,
    title: str = "",
):
    """
    Plot a t-SNE visualization of data points.

    Args:
        x (numpy.ndarray): 2D array containing t-SNE coordinates.
        y (numpy.ndarray): Array of cluster labels.
        counts (numpy.ndarray): Array of cluster counts.
        min_size (int, optional): Minimum size threshold for highlighting clusters. Defaults to 100.
        figsize (tuple, optional): Figure size. Defaults to (20, 20).
        legend (bool, optional): Whether to show the legend. Defaults to True.
        title (str, optional): Title for the plot. Defaults to "".
    """
    for label in np.unique(y):
        kept = np.where(y == label)[0]

        if label == -1:
            plt.scatter(x[kept, 0], x[kept, 1], s=0.1, c="gray")
        else:
            if counts[label + 1] > min_size:
                plt.scatter(x[kept, 0], x[kept, 1], s=10, label=f"Cluster {label}")
            else:
                plt.scatter(x[kept, 0], x[kept, 1], s=1)

    if legend:
        lgd = plt.legend(fontsize=10)
        for i in range(len(lgd.legend_handles)):
            lgd.legend_handles[i]._sizes = [30]

    plt.axis(False)

    if title:
        plt.title(title, fontsize=15)


def plot_dbscan_results(
    embeds: np.ndarray,
    y: np.ndarray,
    counts: np.ndarray,
    min_size: int = 100,
    tsne_params: Dict[str, Union[int, float]] = {}
) -> None:
    """
    Plot the results of DBScan clustering using t-SNE visualization.
    Note that data has to be subsampled to ~10000 points for t-SNE to converge.

    Args:
        embeds (numpy.ndarray): 2D array containing embeddings.
        y (numpy.ndarray): Array of cluster labels.
        counts (numpy.ndarray): Array of cluster counts.
        min_size (int, optional): Minimum size threshold for highlighting clusters. Defaults to 100.
        tsne_params (dict, optional): t-SNE parameters. Defaults to {}.
    """
    # S = len(embeds) // 100
    S = max(len(embeds) // 100, 1)

    tsne = TSNE(n_components=2, **tsne_params)

    X_embedded = tsne.fit_transform(embeds[::S])

    try:
        X_embedded = X_embedded.values.get()
    except AttributeError:
        pass

    plt.figure(figsize=(20, 20))
    plot_tsne(X_embedded, y[::S], counts, min_size=min_size)
    plt.show()


def plot_coreset_results(
    embeds: np.ndarray,
    y: np.ndarray,
    counts: np.ndarray,
    coreset_ids: np.ndarray,
    min_size: int = 100,
    tsne_params: Dict[str, Union[int, float]] = {},
):
    """
    Plot the results before and after applying a Coreset sampling using t-SNE visualization.

    Args:
        embeds (numpy.ndarray): 2D array containing embeddings.
        y (numpy.ndarray): Array of cluster labels.
        counts (numpy.ndarray): Array of cluster counts.
        coreset_ids (list): List of coreset sample indices.
        min_size (int, optional): Minimum size threshold for highlighting clusters. Defaults to 100.
        tsne_params (dict, optional): t-SNE parameters. Defaults to {}.
    """
    S = max(len(embeds) // 100, 1)

    # Subsample
    kept_tsne = np.concatenate([np.arange(len(embeds))[::S], coreset_ids])
    kept_tsne = np.sort(np.unique(kept_tsne))
    kept_coreset = np.array(
        [idx for idx, v in enumerate(kept_tsne) if v in coreset_ids]
    )

    # T-SNE
    tsne = TSNE(n_components=2, **tsne_params)
    X_embedded = tsne.fit_transform(embeds[kept_tsne])

    try:
        X_embedded = X_embedded.values.get()
    except AttributeError:
        pass

    # Plot results
    plt.figure(figsize=(20, 10))

    plt.subplot(1, 2, 1)
    plot_tsne(
        X_embedded,
        y[kept_tsne],
        counts,
        min_size=min_size,
        legend=False,
        title="Before Coreset",
    )

    plt.subplot(1, 2, 2)
    plot_tsne(
        X_embedded[kept_coreset],
        y[kept_tsne][kept_coreset],
        counts,
        min_size=min_size,
        legend=False,
        title="After Coreset",
    )

    plt.show()

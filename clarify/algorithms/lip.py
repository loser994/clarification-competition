# SPDX-FileCopyrightText: 2026 Yang Zhang <zhangy2256@mail2.sysu.edu.cn>
# SPDX-License-Identifier: MIT

"""IntentBridgeClarifier.

Registration stub. The competition algorithm is under development.

Team: lip
Team Members: Yang Zhang (Sun Yat-sen University)
Main Contact: Yang Zhang <zhangy2256@mail2.sysu.edu.cn>
"""

from clarify.baselines import ClarificationAlgorithmBase


class IntentBridgeClarifier(ClarificationAlgorithmBase):
    """Placeholder for team lip's competition implementation."""

    DEFAULT_CONFIG = {}

    def __init__(self, config=None):
        settings = dict(self.DEFAULT_CONFIG)
        if config is not None:
            settings.update(config)
        super().__init__(settings)

    def run(self, env, problem) -> str:
        raise NotImplementedError(
            "Registration stub only. The algorithm is not implemented yet."
        )

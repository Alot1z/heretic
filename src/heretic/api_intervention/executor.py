# SPDX-License-Identifier: AGPL-3.0-or-later

from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass

from .types import ApiCaller, BranchResponse


@dataclass(slots=True)
class BranchExecutor:
    """Parallel branch dispatcher for API calls."""

    max_workers: int = 3

    def execute(self, prompts: list[str], call_api: ApiCaller) -> list[BranchResponse]:
        if not prompts:
            return []

        # Keep the returned list aligned with the input prompt order for
        # deterministic downstream behavior.
        responses: list[BranchResponse | None] = [None] * len(prompts)

        with ThreadPoolExecutor(max_workers=min(self.max_workers, len(prompts))) as pool:
            futures = {
                pool.submit(call_api, prompt): (index, prompt)
                for index, prompt in enumerate(prompts)
            }

            for future in as_completed(futures):
                index, prompt = futures[future]
                try:
                    content = future.result()
                    responses[index] = BranchResponse(prompt=prompt, content=content)
                except Exception as error:  # noqa: BLE001
                    responses[index] = BranchResponse(
                        prompt=prompt,
                        content=None,
                        error=str(error),
                    )

        return [response for response in responses if response is not None]

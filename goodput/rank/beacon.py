"""Progress beacon: step counter + monotonic timestamp pushed to the local node agent."""

from __future__ import annotations

from typing import Protocol


class ProgressBeacon(Protocol):
    """Publishes per-step progress to the node agent.

    Contract:
    * ``tick`` is O(1), non-blocking, and never raises into the training loop; if the
      agent is gone, progress is dropped (design principle 1: out of the data path).
    * Transport is shared memory or a Unix socket, never TCP.
    """

    def tick(self, step: int) -> None: ...

    def close(self) -> None: ...

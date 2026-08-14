"""Product-neutral planning controls.

Product naming, repository layout, and documentation sources are supplied by an
integration adapter.  This package owns only deterministic collection,
validation, marker lifetime, and retry rules.
"""

from acgh.plancore.errors import PlanControlError

__all__ = ["PlanControlError"]

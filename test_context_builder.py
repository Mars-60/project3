from backend.database.db import (
    get_recent_activities
)

from backend.ai.context_builder import (
    build_context
)

activities = get_recent_activities(5)

context = build_context(
    activities
)

print(context)
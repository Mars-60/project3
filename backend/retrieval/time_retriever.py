from datetime import (
    datetime,
    timedelta
)

from backend.database.time_queries import (
    get_activities_between
)


def retrieve_by_time(question):

    question = question.lower()

    if "today" in question:

        today = datetime.now()

        start_time = (
            today.strftime("%Y-%m-%d")
            + "T00:00:00"
        )

        end_time = (
            today.strftime("%Y-%m-%d")
            + "T23:59:59"
        )

        return get_activities_between(
            start_time,
            end_time
        )

    if "yesterday" in question:

        yesterday = (
            datetime.now()
            - timedelta(days=1)
        )

        start_time = (
            yesterday.strftime("%Y-%m-%d")
            + "T00:00:00"
        )

        end_time = (
            yesterday.strftime("%Y-%m-%d")
            + "T23:59:59"
        )

        return get_activities_between(
            start_time,
            end_time
        )

    return []
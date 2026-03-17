def get_daily_lesson(level, day):

    if level == "beginner":
        return {
            "reading": "My name is Anna. I like apples.",
            "task": "Read this aloud and explain it."
        }

    elif level == "intermediate":
        return {
            "reading": "Technology is changing the world rapidly.",
            "task": "Summarize this paragraph."
        }

    else:
        return {
            "reading": "Artificial Intelligence is transforming industries globally.",
            "task": "Give your opinion."
        }
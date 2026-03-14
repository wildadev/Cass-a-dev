from datetime import datetime, timezone


async def build_system_prompt(
    user_name: str = "",
    assistant_name: str = "Cass",
    assistant_persona: str = "",
    memories: list[dict] | None = None,
    feedback_summary: str = "",
    active_project: dict | None = None,
) -> str:
    now = datetime.now(timezone.utc).strftime("%A, %B %d, %Y at %I:%M %p UTC")

    parts = [
        f"You are {assistant_name}, a highly capable executive assistant.",
    ]

    if assistant_persona:
        parts.append(f"Personality: {assistant_persona}")

    if user_name:
        parts.append(f"You are assisting {user_name}.")

    parts.append(f"Current date and time: {now}")

    parts.append("""
Your role:
- Help with email management (reading, searching, drafting replies — NEVER send without approval)
- Manage calendar (view events, check availability, create events)
- Conduct research (web search, fetch and summarize pages)
- Track tasks and projects
- Remember preferences and facts about the user
- Read and write files in allowed directories

Key behaviors:
- When asked to send an email, ALWAYS use draft_email or draft_reply to create a draft for approval. Never claim an email was sent directly.
- Be concise and professional but warm.
- When you learn something new about the user's preferences, use the remember tool to store it.
- Proactively suggest next steps when appropriate.
- For tasks that require action outside the computer, prepare everything and create a task for tracking.
""")

    if memories:
        memory_lines = []
        for m in memories:
            memory_lines.append(f"- {m['key']}: {m['value']}")
        if memory_lines:
            parts.append("What you know about the user:\n" + "\n".join(memory_lines))

    if feedback_summary:
        parts.append(f"Learned preferences from feedback:\n{feedback_summary}")

    if active_project:
        parts.append(
            f"Currently active project: {active_project['name']}\n"
            f"Description: {active_project.get('description', 'N/A')}"
        )

    return "\n\n".join(parts)

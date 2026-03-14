from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from cass.models.db_models import Memory


async def store_memory(db: AsyncSession, key: str, value: str, category: str = "general"):
    existing = await db.execute(select(Memory).where(Memory.key == key))
    memory = existing.scalar_one_or_none()
    if memory:
        memory.value = value
        memory.category = category
    else:
        memory = Memory(key=key, value=value, category=category)
        db.add(memory)
    await db.commit()


async def recall_memories(db: AsyncSession, query: str = "", category: str = "") -> list[dict]:
    stmt = select(Memory)
    if category:
        stmt = stmt.where(Memory.category == category)
    result = await db.execute(stmt)
    memories = result.scalars().all()

    if query:
        query_lower = query.lower()
        memories = [
            m for m in memories if query_lower in m.key.lower() or query_lower in m.value.lower()
        ]

    return [{"key": m.key, "value": m.value, "category": m.category} for m in memories]


async def get_all_memories(db: AsyncSession) -> list[dict]:
    result = await db.execute(select(Memory))
    return [{"key": m.key, "value": m.value, "category": m.category} for m in result.scalars()]

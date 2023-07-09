from sqlalchemy import Column, ForeignKey, Integer, String, Text, TIMESTAMP, Table
from auth.models import user
from database import metadata



post = Table(
    "post",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("user_name", String, ForeignKey(user.c.name)),
    Column("created_at", TIMESTAMP()),
    Column("title", String(100), nullable=False),
    Column("content", Text(), nullable=False),
    Column("like", Integer, default=0)
)


like = Table(
    "like",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("post_id", Integer, ForeignKey(post.c.id), nullable=False),
    Column("user_name", String, ForeignKey(user.c.name), nullable=False)
)
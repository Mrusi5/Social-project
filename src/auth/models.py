from sqlalchemy import Column, Integer, String, Table, Boolean
from src.database import metadata



user = Table(
    "user",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("email", String(40), unique=True, index=True),
    Column("name", String(100)),
    Column("hashed_password", String()),
    Column("disabled", Boolean, default=False),
)


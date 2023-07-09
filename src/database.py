from typing import AsyncGenerator
from sqlalchemy import TIMESTAMP, Boolean, Column, ForeignKey, Integer, MetaData, String, Text
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.orm import relationship

from src.config import DB_HOST, DB_NAME, DB_PASS, DB_PORT, DB_USER


DATABASE_URL = f'postgresql+asyncpg://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}'
Base = declarative_base()

engine = create_async_engine(DATABASE_URL, echo=True)
async_session_maker = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

metadata = MetaData()

async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session


class User(Base):
    __tablename__ = "user"
    
    id = Column("id", Integer, primary_key=True)
    email = Column("email", String(40), unique=True, index=True)
    name = Column("name", String(100))
    hashed_password = Column("hashed_password", String())
    disabled = Column("disabled", Boolean, default=False)

    posts = relationship("Post", back_populates="user")


class Post(Base):
    __tablename__ = "post"

    id = Column("id", Integer, primary_key=True)
    user_name = Column("user_name", String, ForeignKey("user.name"))
    created_at = Column("created_at", TIMESTAMP())
    title = Column("title", String(100), nullable=False)
    content = Column("content", Text(), nullable=False)
    like = Column("like", Integer, default=0)

    user = relationship("User", back_populates="posts")
 

class Like(Base):
    __tablename__ = "like" 

    id = Column("id", Integer, primary_key=True)
    post_id = Column("post_id", Integer, ForeignKey("post.id"), nullable=False)
    user_name = Column("user_name", String, ForeignKey("user.name"), nullable=False)

    post = relationship('Post', primaryjoin=post_id==Post.id)
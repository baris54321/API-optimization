from sqlalchemy import BigInteger, Column, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import DeclarativeBase, relationship


class Base(DeclarativeBase):
    pass


class AppUser(Base):
    __tablename__ = "app_user"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    username = Column(String(150), nullable=False)
    email = Column(String(254), nullable=False)
    password = Column(String(128), nullable=False)
    first_name = Column(String(150), nullable=False, default="")
    last_name = Column(String(150), nullable=False, default="")
    is_superuser = Column(nullable=False, default=False)
    is_staff = Column(nullable=False, default=False)
    is_active = Column(nullable=False, default=True)
    date_joined = Column(DateTime(timezone=True), nullable=False)
    last_login = Column(DateTime(timezone=True), nullable=True)

    posts = relationship("AppPost", back_populates="author")


class AppPost(Base):
    __tablename__ = "app_post"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    title = Column(String(255), nullable=False)
    body = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False)
    updated_at = Column(DateTime(timezone=True), nullable=False)
    author_id = Column(BigInteger, ForeignKey("app_user.id"), nullable=False, index=True)

    author = relationship("AppUser", back_populates="posts")
    comments = relationship("AppComment", back_populates="post")


class AppComment(Base):
    __tablename__ = "app_comment"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    text = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False)
    author_id = Column(BigInteger, ForeignKey("app_user.id"), nullable=False, index=True)
    post_id = Column(BigInteger, ForeignKey("app_post.id"), nullable=False, index=True)

    author = relationship("AppUser")
    post = relationship("AppPost", back_populates="comments")

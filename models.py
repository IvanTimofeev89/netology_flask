import atexit
import datetime
import os

from dotenv import load_dotenv
from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, create_engine, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker

load_dotenv()

POSTGRES_USER = os.getenv("POSTGRES_USER")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")
POSTGRES_DB = os.getenv("POSTGRES_DB")
POSTGRES_PORT = os.getenv("POSTGRES_PORT")
POSTGRES_HOST = os.getenv("POSTGRES_HOST")

PG_DSN = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"

engine = create_engine(PG_DSN)
atexit.register(engine.dispose)

Session = sessionmaker(bind=engine)


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    password: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(
        String(100), nullable=False, index=True, unique=True
    )
    registration_time: Mapped[datetime.datetime] = mapped_column(
        DateTime, server_default=func.now()
    )

    @property
    def dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "registration_time": self.registration_time.isoformat(),
        }


class Ad(Base):
    __tablename__ = "ads"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    header: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime, server_default=func.now()
    )
    owner_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"))

    @property
    def dict(self):
        return {
            "id": self.id,
            "header": self.header,
            "description": self.description,
            "created_at": self.created_at.isoformat(),
        }


# Base.metadata.drop_all(engine)
Base.metadata.create_all(engine)

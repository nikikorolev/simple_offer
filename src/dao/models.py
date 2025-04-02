from sqlalchemy import BigInteger, String, Float, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from dao.database import Base


class User(Base):
    __tablename__ = "users"

    telegram_id: Mapped[int] = mapped_column(
        BigInteger, unique=True, nullable=False)

    def __repr__(self):
        return f"<User(id={self.id}, telegram_id={self.telegram_id}')>"


class Location(Base):
    __tablename__ = "locations"

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"), nullable=False)
    location: Mapped[str] = mapped_column(String, nullable=False)

    user: Mapped['User'] = relationship(
        "User", backref="locations")


class Grade(Base):
    __tablename__ = "grades"

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"), nullable=False)
    grade: Mapped[str] = mapped_column(String, nullable=False)

    user: Mapped['User'] = relationship(
        "User", backref="grades")


class Salary(Base):
    __tablename__ = "salaries"

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"), nullable=False)
    salary: Mapped[float] = mapped_column(Float, nullable=False)

    user: Mapped['User'] = relationship(
        "User", backref="salaries")


class Speciality(Base):
    __tablename__ = "specialities"

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"), nullable=False)
    speciality: Mapped[str] = mapped_column(String, nullable=False)

    user: Mapped['User'] = relationship(
        "User", backref="specialities")


class SentVacanciesHeadhunter(Base):
    __tablename__ = "sent_vacancies_headhunter"

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"), nullable=False)
    vacancy_id: Mapped[int] = mapped_column(
        BigInteger, nullable=False)

    user: Mapped['User'] = relationship(
        "User", backref="sent_vacancies_headhunter")

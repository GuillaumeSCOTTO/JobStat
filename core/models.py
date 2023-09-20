from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column

from core import engine


class Base(DeclarativeBase):
    pass


class JobStat(Base):
    __tablename__ = "jobs_stats"

    date: Mapped[str] = mapped_column(primary_key=True)
    source: Mapped[str] = mapped_column(primary_key=True)
    job_title: Mapped[str] = mapped_column(primary_key=True)
    location: Mapped[str] = mapped_column(primary_key=True)
    nb_of_jobs: Mapped[int]
    delta_vs_previous: Mapped[int]
    delta_vs_previous_percent: Mapped[float]

    def __repr__(self) -> str:
        return f"JobStat(date={self.date!r}, source={self.source!r}, job_title={self.job_title!r}, " \
               f"location={self.location!r}, nb_of_jobs={self.nb_of_jobs!r}, " \
               f"delta_vs_previous={self.delta_vs_previous!r}, " \
               f"delta_vs_previous_percent={self.delta_vs_previous_percent!r})"


# Create the database schema
Base.metadata.create_all(engine)

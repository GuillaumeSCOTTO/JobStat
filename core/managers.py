from sqlalchemy import select

from core import Session
from core.models import JobStat
from core.scrappers import JobsScrapperFactory
from datetime import date


class JobsStatsManager:
    def __init__(self):
        self.stats = list()
        self.scrappers_factory = JobsScrapperFactory.get_instance()
        self.scrappers = self.scrappers_factory.get_scrappers()

        self.searches = dict()

        self.searches["LinkedIn"] = [
            ("Data Engineer", "France"),
            ("Data Scientist", "France"),
            ("Tech lead", "France"),
            ("Architecte IT", "France"),
            ("Software Architect", "France"),
            ("Data Engineer", "United States"),
            ("Data Scientist", "United States"),
            ("Tech lead", "United States"),
            ("IS Architect", "United States"),
            ("Software Architect", "United States"),
        ]

        self.searches["WelcomeToTheJungle"] = [
            ("Data Engineer", "France"),
            ("Data Scientist", "France"),
            ("Tech lead", "France"),
            ("Architecte IT", "France"),
            ("Software Architect", "France"),
        ]

    def collect_data(self):
        search_date = date.today().strftime("%Y-%m-%d")

        for web_source in self.searches:
            for job_search in self.searches[web_source]:
                job_title = job_search[0]
                location = job_search[1]
                print("Searching {job_title} in {location} on {website}".format(job_title=job_title,
                                                                                location=location, website=web_source))
                nb_of_jobs = self.scrappers[web_source].get_nb_of_jobs(job_title, location)
                job_stat = JobStat(date=search_date, source=web_source, job_title=job_title, location=location,
                                   nb_of_jobs=nb_of_jobs)
                job_stat.delta_vs_previous, job_stat.delta_vs_previous_percent = self._compute_variations(job_stat)
                self._save_stat(job_stat)

    @staticmethod
    def _compute_variations(job_stat: JobStat) -> tuple:
        delta_vs_previous = 0
        delta_vs_previous_percent = 0
        with Session.begin() as session:
            statement = select(JobStat).where(JobStat.date != job_stat.date,
                                              JobStat.source == job_stat.source,
                                              JobStat.job_title == job_stat.job_title,
                                              JobStat.location == job_stat.location) \
                .order_by(JobStat.date.desc())
            result_row = session.execute(statement).first()

            if result_row is not None:
                print("There is a previous entry")
                previous_job_stat = result_row[0]
                print("Current stat : {}".format(job_stat))
                print("Previous stat : {}".format(previous_job_stat))
                delta_vs_previous = job_stat.nb_of_jobs - previous_job_stat.nb_of_jobs
                delta_vs_previous_percent = round((job_stat.nb_of_jobs / previous_job_stat.nb_of_jobs) - 1, 2)

        return delta_vs_previous, delta_vs_previous_percent

    @staticmethod
    def _save_stat(job_stat: JobStat):
        with Session.begin() as session:
            statement = select(JobStat).filter_by(date=job_stat.date, source=job_stat.source,
                                                  job_title=job_stat.job_title, location=job_stat.location)
            job_stat_obj = session.execute(statement).scalar_one_or_none()
            if job_stat_obj is None:
                session.add(job_stat)
            else:
                job_stat_obj.nb_of_jobs = job_stat.nb_of_jobs
                job_stat_obj.delta_vs_previous = job_stat.delta_vs_previous
                job_stat_obj.delta_vs_previous_percent = job_stat.delta_vs_previous_percent

    @staticmethod
    def get_stat(stat_date: str, source: str, job_title: str, location: str) -> JobStat:
        with Session.begin() as session:
            # Set expire_on_commit to False to avoid DetachedInstanceError when the get_stat result is used by
            # a caller. When it is set to True, access to an attribute will lead to access the database; if it
            # is performed outside of a Session, then DetachedInstanceError is raised
            # I may have a design issue, because normally, it is feasible to avoid closing a Session "too early"
            # (here, the session is automatically close at the end of the with block)
            # Regarding DetachedInstanceError: https://docs.sqlalchemy.org/en/20/errors.html#error-bhk3
            # Regarding expire_on_commit: https://docs.sqlalchemy.org/en/20/orm/session_api.html#sqlalchemy.orm.Session.params.expire_on_commit
            session.expire_on_commit = False
            statement = select(JobStat).where(JobStat.date == stat_date,
                                              JobStat.source == source,
                                              JobStat.job_title == job_title,
                                              JobStat.location == location)
            job_stat = session.execute(statement).scalar_one_or_none()
            return job_stat

    @staticmethod
    def get_all_stats() -> list:
        with Session.begin() as session:
            # Set expire_on_commit to False to avoid DetachedInstanceError when the get_stat result is used by
            # a caller. When it is set to True, access to an attribute will lead to access the database; if it
            # is performed outside of a Session, then DetachedInstanceError is raised
            # I may have a design issue, because normally, it is feasible to avoid closing a Session "too early"
            # (here, the session is automatically close at the end of the with block)
            # Regarding DetachedInstanceError: https://docs.sqlalchemy.org/en/20/errors.html#error-bhk3
            # Regarding expire_on_commit: https://docs.sqlalchemy.org/en/20/orm/session_api.html#sqlalchemy.orm.Session.params.expire_on_commit
            session.expire_on_commit = False
            statement = select(JobStat)
            job_stat_list = session.execute(statement).all()
            return job_stat_list



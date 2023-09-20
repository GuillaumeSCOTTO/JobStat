import unittest
from datetime import date
from unittest.mock import patch

from sqlalchemy import delete, create_engine

import core
from core import Session
from core.managers import JobsStatsManager
from core.models import JobStat


class TestJobsStatsManager(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.searches = dict()
        cls.searches["LinkedIn"] = [
            ("Data Scientist", "France"),
            ("Architecte", "France")
        ]
        cls.searches["WelcomeToTheJungle"] = [
            ("Data Scientist", "France"),
            ("Architecte", "France")
        ]

    @patch('core.engine', create_engine("sqlite+pysqlite:///:memory:", echo=True))
    def setUp(self) -> None:
        with Session.begin() as session:
            statement = delete(JobStat)
            session.execute(statement)

    @patch('core.engine', create_engine("sqlite+pysqlite:///:memory:", echo=True))
    def test_save_and_get_stat(self):
        jobstats_mgr = JobsStatsManager()

        # Save a first stat
        search_date = "2023-02-19"
        web_source = "LinkedIn"
        job_title = "Data Scientist"
        location = "France"
        nb_of_jobs = 1100
        delta_vs_previous = 100
        delta_vs_previous_percent = 0.1
        job_stat = JobStat(date=search_date, source=web_source, job_title=job_title, location=location,
                           nb_of_jobs=nb_of_jobs, delta_vs_previous=delta_vs_previous,
                           delta_vs_previous_percent=delta_vs_previous_percent)
        jobstats_mgr._save_stat(job_stat)
        job_stat_obj = jobstats_mgr.get_stat(search_date, web_source, job_title, location)
        self.assertIsNotNone(job_stat_obj)
        self.assertEqual(job_stat_obj.date, search_date)
        self.assertEqual(job_stat_obj.source, web_source)
        self.assertEqual(job_stat_obj.job_title, job_title)
        self.assertEqual(job_stat_obj.location, location)
        self.assertEqual(job_stat_obj.nb_of_jobs, nb_of_jobs)
        self.assertEqual(job_stat_obj.delta_vs_previous, delta_vs_previous)
        self.assertEqual(job_stat_obj.delta_vs_previous_percent, delta_vs_previous_percent)

        # Save a second stat
        search_date = "2023-02-19"
        web_source = "Welcome To The Jungle"
        job_title = "Data Engineer"
        location = "United States"
        nb_of_jobs = 20
        delta_vs_previous = 10
        delta_vs_previous_percent = 1
        job_stat = JobStat(date=search_date, source=web_source, job_title=job_title, location=location,
                           nb_of_jobs=nb_of_jobs, delta_vs_previous=delta_vs_previous,
                           delta_vs_previous_percent=delta_vs_previous_percent)
        jobstats_mgr._save_stat(job_stat)
        job_stat_list = jobstats_mgr.get_all_stats()
        self.assertEqual(len(job_stat_list), 2)
        job_stat_obj = jobstats_mgr.get_stat(search_date, web_source, job_title, location)
        self.assertEqual(job_stat_obj.nb_of_jobs, nb_of_jobs)

        # Update a stat
        search_date = "2023-02-19"
        web_source = "LinkedIn"
        job_title = "Data Scientist"
        location = "France"
        nb_of_jobs = 1500
        delta_vs_previous = 500
        delta_vs_previous_percent = 0.5
        job_stat = JobStat(date=search_date, source=web_source, job_title=job_title, location=location,
                           nb_of_jobs=nb_of_jobs, delta_vs_previous=delta_vs_previous,
                           delta_vs_previous_percent=delta_vs_previous_percent)
        jobstats_mgr._save_stat(job_stat)
        job_stat_list = jobstats_mgr.get_all_stats()
        self.assertEqual(len(job_stat_list), 2)
        job_stat_obj = jobstats_mgr.get_stat(search_date, web_source, job_title, location)
        self.assertEqual(job_stat_obj.nb_of_jobs, nb_of_jobs)

    @patch('core.engine', create_engine("sqlite+pysqlite:///:memory:", echo=True))
    def test_compute_variations(self):
        jobstats_mgr = JobsStatsManager()
        web_source = "LinkedIn"
        job_title = "Data Scientist"
        location = "France"

        job_stat1 = JobStat(date="2023-02-19", source=web_source, job_title=job_title, location=location,
                           nb_of_jobs=1000)
        job_stat1.delta_vs_previous, job_stat1.delta_vs_previous_percent = jobstats_mgr._compute_variations(job_stat1)
        self.assertEqual(job_stat1.delta_vs_previous, 0)
        self.assertEqual(job_stat1.delta_vs_previous_percent, 0.0)
        jobstats_mgr._save_stat(job_stat1)

        job_stat2 = JobStat(date="2023-02-20", source=web_source, job_title=job_title, location=location,
                           nb_of_jobs=1100)
        job_stat2.delta_vs_previous, job_stat2.delta_vs_previous_percent = jobstats_mgr._compute_variations(job_stat2)
        self.assertEqual(job_stat2.delta_vs_previous, 100)
        self.assertEqual(job_stat2.delta_vs_previous_percent, 0.10)
        jobstats_mgr._save_stat(job_stat2)

        job_stat3 = JobStat(date="2023-02-21", source=web_source, job_title=job_title, location=location,
                           nb_of_jobs=1100)
        job_stat3.delta_vs_previous, job_stat3.delta_vs_previous_percent = jobstats_mgr._compute_variations(job_stat3)
        self.assertEqual(job_stat3.delta_vs_previous, 0)
        self.assertEqual(job_stat3.delta_vs_previous_percent, 0.0)
        jobstats_mgr._save_stat(job_stat3)

    @patch('core.engine', create_engine("sqlite+pysqlite:///:memory:", echo=True))
    @patch('core.scrappers.WelcomeToTheJungleJobsScrapper', autospec=True)
    @patch('core.scrappers.LinkedinJobsScrapper', autospec=True)
    def test_collect_data(self, mock_linkedin_scrapper, mock_wtjungle_scrapper):
        mock_linkedin_scrapper_instance = mock_linkedin_scrapper.return_value
        mock_linkedin_scrapper_instance.get_nb_of_jobs.side_effect = [1000, 2000]

        mock_wtjungle_scrapper_instance = mock_wtjungle_scrapper.return_value
        mock_wtjungle_scrapper_instance.get_nb_of_jobs.side_effect = [10, 20]

        jobstats_mgr = JobsStatsManager()

        # Add a first item, corresponding to the first LinkedIn search, with data older than today
        # It will then be used to check if the compute_variation has been called by collect_data
        web_source = "LinkedIn"
        job_title = self.searches[web_source][0][0]
        location = self.searches[web_source][0][1]

        job_stat = JobStat(date="2000-01-01", source=web_source, job_title=job_title, location=location,
                           nb_of_jobs=700)
        job_stat.delta_vs_previous, job_stat.delta_vs_previous_percent = jobstats_mgr._compute_variations(job_stat)
        jobstats_mgr._save_stat(job_stat)

        # Do the searches using the searches idct defined in this test class
        with patch.object(jobstats_mgr, 'searches', self.searches):
            jobstats_mgr.collect_data()
            job_stat_list = jobstats_mgr.get_all_stats()

            # We expect to have N rows in the database, N being equal to the number of searches + the first item
            # added at the beginning of this function
            expected_rows = 1
            for key in self.searches.keys():
                expected_rows += len(self.searches[key])
            self.assertEqual(len(job_stat_list), expected_rows)

            # Assert that a variation has been well computed for the first LinkedIn search in the searches dict
            search_date = date.today().strftime("%Y-%m-%d")
            job_stat_obj = jobstats_mgr.get_stat(search_date, web_source, job_title, location)
            self.assertEqual(job_stat_obj.delta_vs_previous, 300)


if __name__ == '__main__':
    unittest.main()

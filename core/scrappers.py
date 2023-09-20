from abc import ABC, abstractmethod
from bs4 import BeautifulSoup
from urllib import parse
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
import re
import time
import weakref


class AbcJobsScrapper(ABC):

    def __init__(self):
        # mettre son chemin vers le webdriver
        path2 = 'C:\\Users\\GuillaumeScotto\\Documents\\code\\support\\chromedriver.exe'
        
        service = Service(executable_path=path2)

        Myoptions = webdriver.ChromeOptions()
        print("Init driver")
        print(Myoptions)
        print(service)
        Myoptions.add_argument('--ignore-certificate-errors')
        Myoptions.add_argument('--incognito')
        Myoptions.add_argument('--headless')
        
        

        #spath = 'C:\Users\GuillaumeScotto\OneDrive - NDA Partners\Documents\Logiciels\chromedriver.exe'
        #self.driver = webdriver.Chrome('C:\\Users\\Loic\\Dev\\chrome_driver\\chromedriver109_win32\\chromedriver.exe',
        #                               options=options)
        self.driver = webdriver.Chrome(service = service, options=Myoptions)
        # https://stackoverflow.com/questions/35915624/destructor-in-metaclass-singleton-object
        # https://docs.python.org/3.8/library/weakref.html
        weakref.finalize(self, self._quit)

    def _get_soup(self, url: str):
        self.driver.get(url)
        time.sleep(5)
        page_source = self.driver.page_source
        soup = BeautifulSoup(page_source, 'html.parser')
        return soup

    @abstractmethod
    def get_nb_of_jobs(self, job_title: str, location: str):
        pass

    def _quit(self):
        print("Close driver")
        self.driver.quit()


class LinkedinJobsScrapper(AbcJobsScrapper):
    def get_nb_of_jobs(self, job_title: str, location: str):
        params = {'keywords': job_title, 'location': location}
        url_params = parse.urlencode(params, quote_via=parse.quote)
        url = "https://www.linkedin.com/jobs/search?" + url_params
        soup = self._get_soup(url)
        raw_data = soup.title.text
        print(raw_data)
        interesting_data = re.findall(r'([\d+\s]*\d+)', raw_data)
        # print(interesting_data)
        nb_of_jobs = interesting_data[0].replace(u'\xa0', u'')
        return int(nb_of_jobs)


class WelcomeToTheJungleJobsScrapper(AbcJobsScrapper):
    def get_nb_of_jobs(self, job_title: str, location: str):
        params = {'query': job_title, 'aroundQuery': location}
        url_params = parse.urlencode(params, quote_via=parse.quote)
        #print(url_params)
        url = "https://www.welcometothejungle.com/fr/jobs?groupBy=job&page=1&" + url_params
        # print(url)
        soup = self._get_soup(url)
        # print(soup.prettify())
        nb_of_jobs = soup.find(string="Jobs").parent.next_sibling.text
        #print("rsulst",nb_of_jobs)
        return int(nb_of_jobs)


class JobsScrapperFactory:
    __instance = None

    def __init__(self):
        self.scrappers_instances = dict()
        self.scrappers_instances['LinkedIn'] = LinkedinJobsScrapper()
        self.scrappers_instances['WelcomeToTheJungle'] = WelcomeToTheJungleJobsScrapper()

    @staticmethod
    def get_instance():
        if JobsScrapperFactory.__instance is None:
            print("Instantiate JobsScrapperFactory")
            JobsScrapperFactory.__instance = JobsScrapperFactory()
        return JobsScrapperFactory.__instance

    def get_scrappers(self):
        return self.scrappers_instances

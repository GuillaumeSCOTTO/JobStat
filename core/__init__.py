from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Set echo to True in order to see the logs of all the statements
# https://docs.sqlalchemy.org/en/20/core/engines.html
#path = 'C:\Users\GuillaumeScotto\Documents\code\databases\jobstats.db'
path = 'C:\\Users\\GuillaumeScotto\\Documents\\code\\database\\jobstats.db'


engine = create_engine(r"sqlite:///" + path, echo=False)
#engine = create_engine(r"sqlite:///C:\Users\Loic\Dev\jobsstats\jobstats.db", echo=False)
Session = sessionmaker(engine)

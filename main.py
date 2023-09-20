# This is a sample Python script.

# Press Maj+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.

import core

# Press the green button in the gutter to run the script.
from core.managers import JobsStatsManager

if __name__ == '__main__':
    jobs_stats = JobsStatsManager()
    jobs_stats.collect_data()
    for stat in jobs_stats.get_all_stats():
        print(stat)


# See PyCharm help at https://www.jetbrains.com/help/pycharm/

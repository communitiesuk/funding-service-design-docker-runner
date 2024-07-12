from invoke import task

from tasks.db_tasks import create_test_data
from tasks.db_tasks import init_migrations
from tasks.db_tasks import recreate_local_dbs

task.auto_dash_names = True

__all__ = [recreate_local_dbs, create_test_data, init_migrations]

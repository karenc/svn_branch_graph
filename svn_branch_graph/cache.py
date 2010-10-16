import datetime
import sqlite3

TIME_FORMAT = '%Y-%m-%d %H:%M:%S'

def now():
    return datetime.datetime.now().strftime(TIME_FORMAT)

def readtime(time):
    return datetime.datetime.strptime(time, TIME_FORMAT)


class CacheSqlite3Database(object):
    """Cache things into a sqlite3 database
    """

    def __init__(self, database_path, refresh):
        self.database_path = database_path
        self.refresh = datetime.timedelta(minutes=refresh)

    def dbinit(self):
        conn = sqlite3.connect(self.database_path)
        c = conn.cursor()
        try:
            c.execute('''create table svn_branch_graph_cache (
            key text, date text, value text)''')
            conn.commit()
        except sqlite3.OperationalError:
            pass
        c.close()

    def is_expired(self, cached_time):
        now = datetime.datetime.now()
        return (now - readtime(cached_time)) > self.refresh

    def cache(self, key, value):
        conn = sqlite3.connect(self.database_path)
        c = conn.cursor()
        if isinstance(key, str):
            key = unicode(key, 'utf-8')
        if isinstance(value, str):
            value = unicode(value, 'utf-8')
        c.execute('insert into svn_branch_graph_cache VALUES (?, ?, ?)',
                (key, now(), value))
        conn.commit()
        c.close()

    def get(self, key):
        conn = sqlite3.connect(self.database_path)
        c = conn.cursor()
        if isinstance(key, str):
            key = unicode(key, 'utf-8')
        c.execute('select * from svn_branch_graph_cache where key=?', (key,))
        for row in c:
            if not self.is_expired(row[1]):
                if isinstance(row[2], unicode):
                    return row[2].encode('utf-8')
                return row[2]

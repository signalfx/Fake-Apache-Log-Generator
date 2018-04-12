import datetime
from tzlocal import get_localzone
from . import log_generator
import numpy


class Generator(log_generator.Generator):
    def __init__(self):
        # log levels for apache 2.4+
        self.log_level = ["Error", "Warning", "Note"]
        self.log_level_p = [0.3, 0.3, 0.4]
        # mysql error log messages
        self.start_stmts = [
            "mysqld_safe Logging to '/var/log/mysql/error.log'.",
            "mysqld_safe Starting mysqld daemon with databases from /var/lib/mysql",
            ("0 [Warning] TIMESTAMP with implicit DEFAULT value is deprecated. Please use "
             "--explicit_defaults_for_timestamp server option (see documentation for more details)."),
            "0 [Note] /usr/sbin/mysqld (mysqld 5.7.21-0ubuntu0.16.04.1-log) starting as process 600 ...",
            "0 [Note] InnoDB: PUNCH HOLE support available",
            "0 [Note] InnoDB: Mutexes and rw_locks use GCC atomic builtins",
            "0 [Note] InnoDB: Uses event mutexes",
            "0 [Note] InnoDB: GCC builtin __atomic_thread_fence() is used for memory barrier",
            "0 [Note] InnoDB: Compressed tables use zlib 1.2.8",
            "0 [Note] InnoDB: Using Linux native AIO",
            "0 [Note] InnoDB: Number of pools: 1",
            "0 [Note] InnoDB: Using CPU crc32 instructions",
            "0 [Note] InnoDB: Initializing buffer pool, total size = 128M, instances = 1, chunk size = 128M",
            "0 [Note] InnoDB: Completed initialization of buffer pool",
            ("0 [Note] InnoDB: If the mysqld execution user is authorized, page cleaner thread priority can be "
             "changed. See the man page of setpriority()."),
            "0 [Note] InnoDB: Highest supported file format is Barracuda.",
            "0 [Note] InnoDB: Creating shared tablespace for temporary tables",
            ("0 [Note] InnoDB: Setting file './ibtmp1' size to 12 MB. Physically writing the file full; "
             "Please wait ..."),
            "0 [Note] InnoDB: File './ibtmp1' size is now 12 MB.",
            "0 [Note] InnoDB: 96 redo rollback segment(s) found. 96 redo rollback segment(s) are active.",
            "0 [Note] InnoDB: 32 non-redo rollback segment(s) are active.",
            "0 [Note] InnoDB: 5.7.21 started; log sequence number 2551607",
            "0 [Note] InnoDB: Loading buffer pool(s) from /var/lib/mysql/ib_buffer_pool",
            "0 [Note] Plugin 'FEDERATED' is disabled.",
            "0 [Note] InnoDB: Buffer pool(s) load completed at 180327 13:50:19",
            ("0 [Warning] Failed to set up SSL because of the following SSL library error: SSL context is not usable "
             "without certificate and private key"),
            "0 [Note] Server hostname (bind-address): '127.0.0.1'; port: 3306",
            "0 [Note]   - '127.0.0.1' resolves to '127.0.0.1';",
            "0 [Note] Server socket created on IP: '127.0.0.1'.",
            "0 [Note] Event Scheduler: Loaded 0 events",
            "0 [Note] /usr/sbin/mysqld: ready for connections.",
            "Version: '5.7.21-0ubuntu0.16.04.1-log'  socket: '/var/run/mysqld/mysqld.sock'  port: 3306  (Ubuntu)"
        ]

        self.stop_stmts = [
            "0 [Note] Giving 0 client threads a chance to die gracefully",
            "0 [Note] Shutting down slave threads",
            "0 [Note] Forcefully disconnecting 0 remaining clients",
            "0 [Note] Event Scheduler: Purging the queue. 0 events",
            "0 [Note] Binlog end",
            "0 [Note] Shutting down plugin 'ngram'",
            "0 [Note] Shutting down plugin 'partition'",
            "0 [Note] Shutting down plugin 'BLACKHOLE'",
            "0 [Note] Shutting down plugin 'ARCHIVE'",
            "0 [Note] Shutting down plugin 'MyISAM'",
            "0 [Note] Shutting down plugin 'PERFORMANCE_SCHEMA'",
            "0 [Note] Shutting down plugin 'MEMORY'",
            "0 [Note] Shutting down plugin 'MRG_MYISAM'",
            "0 [Note] Shutting down plugin 'CSV'",
            "0 [Note] Shutting down plugin 'INNODB_SYS_VIRTUAL'",
            "0 [Note] Shutting down plugin 'INNODB_SYS_DATAFILES'",
            "0 [Note] Shutting down plugin 'INNODB_SYS_TABLESPACES'",
            "0 [Note] Shutting down plugin 'INNODB_SYS_FOREIGN_COLS'",
            "0 [Note] Shutting down plugin 'INNODB_SYS_FOREIGN'",
            "0 [Note] Shutting down plugin 'INNODB_SYS_FIELDS'",
            "0 [Note] Shutting down plugin 'INNODB_SYS_COLUMNS'",
            "0 [Note] Shutting down plugin 'INNODB_SYS_INDEXES'",
            "0 [Note] Shutting down plugin 'INNODB_SYS_TABLESTATS'",
            "0 [Note] Shutting down plugin 'INNODB_SYS_TABLES'",
            "0 [Note] Shutting down plugin 'INNODB_FT_INDEX_TABLE'",
            "0 [Note] Shutting down plugin 'INNODB_FT_INDEX_CACHE'",
            "0 [Note] Shutting down plugin 'INNODB_FT_CONFIG'",
            "0 [Note] Shutting down plugin 'INNODB_FT_BEING_DELETED'",
            "0 [Note] Shutting down plugin 'INNODB_FT_DELETED'",
            "0 [Note] Shutting down plugin 'INNODB_FT_DEFAULT_STOPWORD'",
            "0 [Note] Shutting down plugin 'INNODB_METRICS'",
            "0 [Note] Shutting down plugin 'INNODB_TEMP_TABLE_INFO'",
            "0 [Note] Shutting down plugin 'INNODB_BUFFER_POOL_STATS'",
            "0 [Note] Shutting down plugin 'INNODB_BUFFER_PAGE_LRU'",
            "0 [Note] Shutting down plugin 'INNODB_BUFFER_PAGE'",
            "0 [Note] Shutting down plugin 'INNODB_CMP_PER_INDEX_RESET'",
            "0 [Note] Shutting down plugin 'INNODB_CMP_PER_INDEX'",
            "0 [Note] Shutting down plugin 'INNODB_CMPMEM_RESET'",
            "0 [Note] Shutting down plugin 'INNODB_CMPMEM'",
            "0 [Note] Shutting down plugin 'INNODB_CMP_RESET'",
            "0 [Note] Shutting down plugin 'INNODB_CMP'",
            "0 [Note] Shutting down plugin 'INNODB_LOCK_WAITS'",
            "0 [Note] Shutting down plugin 'INNODB_LOCKS'",
            "0 [Note] Shutting down plugin 'INNODB_TRX'",
            "0 [Note] Shutting down plugin 'InnoDB'",
            "0 [Note] InnoDB: FTS optimize thread exiting.",
            "0 [Note] InnoDB: Starting shutdown...",
            "0 [Note] InnoDB: Dumping buffer pool(s) to /var/lib/mysql/ib_buffer_pool",
            "0 [Note] InnoDB: Buffer pool(s) dump completed at 180327 13:50:20",
            "0 [Note] InnoDB: Shutdown completed; log sequence number 2562116",
            "0 [Note] InnoDB: Removed temporary tablespace data file: \"ibtmp1\"",
            "0 [Note] Shutting down plugin 'sha256_password'",
            "0 [Note] Shutting down plugin 'mysql_native_password'",
            "0 [Note] Shutting down plugin 'binlog'",
            "0 [Note] /usr/sbin/mysqld: Shutdown complete",
            "",
            "mysqld_safe mysqld from pid file /var/run/mysqld/mysqld.pid ended"
        ]
        super(Generator, self).__init__("mysql_error")

    def _format_statements(self, stmts, otime=datetime.datetime.now(), local=get_localzone()):
        time_fmt = '%Y-%m-%d %H:%M:%S'  # 2015-10-27 07:33:42
        dt = otime.strftime(time_fmt)
        outgoing = []
        for stmt in stmts:
            if stmt == '':
                outgoing.append('\n')
            else:
                otime = datetime.datetime.now()
                dt = otime.strftime(time_fmt)
                outgoing.append('{0} {1}\n'.format(dt, stmt))
        return outgoing

    def getStartStatement(self, otime=datetime.datetime.now(), local=get_localzone(), state={}):
        return self._format_statements(self.start_stmts)

    def getStopStatement(self, otime=datetime.datetime.now(), local=get_localzone(), state={}):
        return self._format_statements(self.stop_stmts)

    def getLogStatement(self, otime=datetime.datetime.now(), local=get_localzone(), state={}):
        """
        generate mysql log statements
        """
        time_fmt = '%Y-%m-%d %H:%M:%S'  # 2015-10-27 07:33:42
        dt = otime.strftime(time_fmt)
        level = numpy.random.choice(self.log_level, p=self.log_level_p)
        outgoing = ['%s 0 [%s] seemingly random log message \n' % (dt, level)]

        return outgoing

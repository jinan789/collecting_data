import pymysql
import Error


class MySQL:
    conn = None
    err = Error.Error("err.log")

    def connect(self, host='127.0.0.1', user="root", passwd="Mm781519636.", database="test", char_set="utf8mb4"):
        self.conn = pymysql.connect(host = host, user = user, password = passwd, database = database, charset=char_set, local_infile=True)

    def close(self):
        self.conn.close()

    def execSQL(self, sql, fetch=False):
        try:
            #  sql = sql.encode("utf-8", "replace").decode()
            cs = self.conn.cursor()
            cs.execute(sql)
            if fetch == True:
                res = cs.fetchall()
                return res
            else:
                self.conn.commit()
        except Exception as e:
            self.err.write_err([sql, e])

    def execSQL_para(self, sql, para, fetch=False):
        try:
            cs = self.conn.cursor()
            cs.execute(sql, para)
            if fetch == True:
                res = cs.fetchall()
                return res
            else:
                self.conn.commit()
        except Exception as e:
            self.err.write_err([sql, para, e])
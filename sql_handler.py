import mariadb
import time
import sys
import io
########################################################################################

class SqlHandler:
    def __init__(self, user_access_level=0):
        self.connection_types=[            
            ['dbuser','dbpass']
        ]
        try:
            self.mdconn = mariadb.connect(
                user=self.connection_types[user_access_level][0],
                password=self.connection_types[user_access_level][1],
                host='127.0.0.1',
                port=3306,
                database='pybot'#,
                #charset='utf8mb4'
            )
            self.mdconn.autocommit=True
        except mariadb.Error as e:
            print(f'ERROR: Error connecting to MariaDB Platform: {e}')
            sys.exit(1)
    def connect_as(self, user_access_level):
        return SqlHandler(user_access_level)
    def run_query(self, query):
        print(f'QRY: {query}')
        self.mdcursor = self.mdconn.cursor()    # do not compress to 'self.mdconn.cursor().execute(query)'!!!
        self.mdcursor.execute(query)            # self.mdcursor will be used later!!!
        #print(f'QUERY: {self.mdcursor._executed}')
    def run_query_param_all(self, query, args):
        self.mdcursor = self.mdconn.cursor()    # do not compress to 'self.mdconn.cursor().execute(query)'!!!
        self.mdcursor.execute_many(query, args) # self.mdcursor will be used later!!!
        #print(f'QUERY: {self.mdcursor._executed}')
    @staticmethod
    def escape_invalid_chars(rawstr): # prevents sqli (sql injections)
        return str(rawstr).replace('\\', '\\\\').replace('\'', '\\\'')
    @staticmethod
    def time_week_ago():
        return int(time.time()) - 604800

##########################################################################################
    def get_status(self, tgid):
        query = 'SELECT status FROM users WHERE tgid=\''+str(tgid)+'\';'
        self.run_query(query)
        return self.mdcursor.fetchone()[0]
    def set_status(self, tgid,status):
        query = 'DELETE FROM users WHERE tgid=\''+str(tgid)+'\';'
        self.run_query(query)
        query = 'INSERT INTO users(tgid,status) VALUES (\''+str(tgid)+'\',\''+str(status)+'\');'
        self.run_query(query)
    def flush_statuses(self):
        query = 'UPDATE users SET status=0;'
        self.run_query(query)
    # def get_all_users_ids(self):
        # query = 'SELECT tgid FROM users;'
        # self.run_query(query)
        # return [f[0] for f in self.mdcursor.fetchall()]
    def get_all_users_ids(self):
        query = 'SELECT tgid FROM users;'
        self.run_query(query)
        return [f[0] for f in self.mdcursor.fetchall()]
        
    def note_new(self, tgid, text,_type):
        typeval={'text':1,'file':2}[_type]
        query = 'INSERT INTO note_'+str(_type)+'(tgid,text) VALUES (\''+str(tgid)+'\',\''+str(text)+'\');'
        self.run_query(query)
        query = 'INSERT INTO notes(_type,_group,uid) SELECT '+str(typeval)+',MAX(id),MAX(id) FROM note_'+str(_type)+' WHERE tgid='+str(tgid)+';'
        self.run_query(query)

    # def note_last(self, tgid, _type='text'):
    def note_last(self, tgid, _type):
        query = 'SELECT MAX(id) FROM note_'+str(_type)+' WHERE tgid='+str(tgid)+';'
        self.run_query(query)
        return self.mdcursor.fetchone()[0]
    # def note_setname(self,_id,name, _type='text'):
    def note_setname(self,_id,name, _type):
        query = 'UPDATE note_'+str(_type)+' SET name=\''+str(name)+'\' WHERE id=\''+str(_id)+'\';'
        self.run_query(query)
    # def note_settext(self,_id,text, _type='text'):
    def note_settext(self,_id,text, _type):
        query = 'UPDATE note_'+str(_type)+' SET text=\''+str(text)+'\' WHERE id=\''+str(_id)+'\';'
        self.run_query(query)
    # def note_delete(self, tgid, _id, _type='text'):
    def note_delete(self, tgid, _id, _type):
        query = 'DELETE FROM note_'+str(_type)+' WHERE tgid=\''+str(tgid)+'\' AND id=\''+str(_id)+'\';'
        self.run_query(query)
        typeval={'text':1,'file':2}[_type]
        query = 'DELETE FROM notes WHERE uid=\''+str(_id)+'\' and _type='+str(typeval)+';'
        self.run_query(query)

    def note_text_getnote(self, tgid, _id):
        query = 'SELECT text FROM note_text WHERE tgid='+str(tgid)+' AND id=\''+str(_id)+'\';'
        self.run_query(query)
        return self.mdcursor.fetchone()
    def note_file_getnote(self, tgid, _id):
        query = 'SELECT file,text,filename,extention FROM note_file WHERE tgid='+str(tgid)+' AND id=\''+str(_id)+'\';'
        self.run_query(query)
        return self.mdcursor.fetchone()
    def note_file_upload(self, tgid,_id,file_open, file_name):
        # query='INSERT INTO note_file(tgid,file,filename,extention) VALUES ('+str(tgid)+',%s,%s,%s);'
        query='UPDATE note_file SET file=%s,filename=%s,extention=%s WHERE tgid='+str(tgid)+' AND id='+str(_id)+';'
        # print("QUERY2:",query)
        print("TQR:",query)
        # file_open.seek(0, io.SEEK_END)
        # filesize = file_open.tell()
        file_open.seek(0) # back to where we were
        namearr=file_name.split('.')
        if len(namearr)==1:
            ext='___'
        else:
            ext=namearr[1]
        self.mdconn.cursor().execute(query, (file_open.read(), namearr[0], ext))
        
    def get_notes_ofgroup(self, tg_id, group=1):
        query = 'SELECT uid,_type from notes WHERE _group='+str(group)+' AND tgid='+str(tgid)+';'
        self.run_query(query)
        return self.mdcursor.fetchall()
    def get_notes_all(self, tgid):
        query = 'SELECT id,1 as _type,concat(\'t> \',name) as name FROM note_text WHERE id in(SELECT uid from notes WHERE tgid='+str(tgid)+' AND _type=1) union SELECT id,2 as _type,concat(\'f> \',name) as name FROM note_file WHERE id in(SELECT uid from notes WHERE tgid='+str(tgid)+' AND _type=2);'
        self.run_query(query)
        return self.mdcursor.fetchall()
    # def get_notes_all_nonames(self, tg_id):
        # query = 'SELECT uid,_type from notes WHERE tgid='+str(tgid)+';'
        # self.run_query(query)
        # return self.mdcursor.fetchall()

from app import db

def test_parameter_binding_and_conflict_translation():
    class Connection:
        def execute(self, sql, params):
            self.sql, self.params = sql, params
            return self
    connection=Connection()
    adapter=db.PostgresConnection.__new__(db.PostgresConnection)
    adapter.connection=connection
    value="Robert'); DROP TABLE tasks;--"
    adapter.execute('INSERT OR IGNORE INTO providers VALUES(?,?,?,?,?)',(1,value,'[]','[]',300))
    assert connection.sql=='INSERT INTO providers VALUES(%s,%s,%s,%s,%s) ON CONFLICT DO NOTHING'
    assert connection.params[1]==value
    assert value not in connection.sql

def test_row_named_and_positional_access():
    row=db.Row({'id':4,'name':'Example'})
    assert row[0]==row['id']==4
    assert dict(row)=={'id':4,'name':'Example'}

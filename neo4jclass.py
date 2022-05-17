from neo4j import GraphDatabase

class Neo4jConnection:
    
    def __init__(self, uri, user, pwd):
        self.__uri = uri
        self.__user = user
        self.__pwd = pwd
        self.__driver = None
        try:
            self.__driver = GraphDatabase.driver(self.__uri, auth=(self.__user, self.__pwd))
        except Exception as e:
            print("Failed to create the driver:", e)
        
    def close(self):
        if (self.__driver is not None):
            self.__driver.close()
        
    def query(self, query, parameters=None, db=None):
        assert self.__driver is not None, "Driver not initialized!"
        session = None
        response = None
        try: 
            session = self.__driver.session(database=db) if db is not None else self.__driver.session() 
            response = list(session.run(query, parameters))
        except Exception as e:
            print("Query failed:", e)
        finally: 
            if (session is not None):
                session.close()
        return response

conn = Neo4jConnection(uri="neo4j+s://b0e1e56e.databases.neo4j.io", 
                                user="neo4j",              
                                pwd="PSN0L8RDvYaMAoykJNDve-NO7R3c6KRmhZHxxDnhhi4")


def add_session_graphs(user_id, session_id):
    add_simple_session_statement = "MERGE (s:SimpleSession {session: '" + session_id + "', user: '" + user_id + "' })"
    add_detailed_session_statement = "MERGE (d:DetailedSession {session: '" + session_id + "', user: '" + user_id + "' })"
    conn.query(add_simple_session_statement)
    conn.query(add_detailed_session_statement)

def add_simple_attitude(sbj, obj, comp, pred, polarity, subjectivity, session_id, sentence):
    if polarity >= 0:
        same_sign = ">="
        opposite_sign = "<"
        same_name = "POSITIVE"
    else:
        same_sign = "<"
        opposite_sign = ">="
        same_name = "NEGATIVE"
    add_statement = ("MATCH (s:SimpleSession {session: '" + session_id + "'}) MERGE (n:Attitude {" 
                    + ("subject: '" + sbj + "', " if sbj is not None else "") + ("object: '" + obj 
                    + "', " if obj is not None else "") + ("complement: '" + comp + "', " if comp is not None else "") 
                    + ("predicate: '" + pred + "', " if pred is not None else "") + "polarity: " + str(polarity) 
                    +", subjectivity: " + str(subjectivity) +", input: '" + sentence 
                    + "'})-[:BELONGS_TO]->(s) WITH n, s OPTIONAL MATCH (a:Attitude)-[:BELONGS_TO]->(s) WHERE a.polarity " 
                    + same_sign + " 0 AND a <> n FOREACH (_ IN CASE WHEN a IS NOT NULL THEN [1] ELSE [] END | MERGE (n)-[:" 
                    + same_name + "]->(a)) WITH n, s OPTIONAL MATCH (b:Attitude)-[:BELONGS_TO]->(s) WHERE b.polarity " + opposite_sign 
                    + " 0 FOREACH (_ IN CASE WHEN b IS NOT NULL THEN [1] ELSE [] END | MERGE (n)-[:OPPOSITE]->(b))")
    conn.query(add_statement)
    return add_statement

def add_detailed_attitude(sbj, obj, comp, pred, polarity, session_id):
    if polarity >= 0:
        same_name = "POSITIVE"
    else:
        same_name = "NEGATIVE"
    add_statement = ("MATCH (d:DetailedSession {session: '" + session_id + "'})" + (" MERGE (s:Item {name: '" + sbj 
                    + "'})-[:BELONGS_TO]->(d)" if sbj is not None else "") + (" MERGE (o:Item {name: '" + obj 
                    + "'})-[:BELONGS_TO]->(d)" if obj is not None else "") + (" MERGE (c:Item {name: '" 
                    + comp + "'})-[:BELONGS_TO]->(d)" if comp is not None else "") + (" MERGE (p:Item {name: '" + pred 
                    + "'})-[:BELONGS_TO]->(d)" if pred is not None else "")
                    + (" MERGE (s)-[r1:" + same_name + "]->(o) SET (CASE WHEN r1.Weight IS NOT NULL THEN r1 END).Weight = r1.Weight +"
                    + "1 SET (CASE WHEN r1.Weight IS NULL THEN r1 END).Weight = 1" if sbj is not None and obj is not None else "")
                    + (" MERGE (s)-[r2:" + same_name + "]->(c) SET (CASE WHEN r2.Weight IS NOT NULL THEN r2 END).Weight = r2.Weight +"
                    + "1 SET (CASE WHEN r2.Weight IS NULL THEN r2 END).Weight = 1" if sbj is not None and comp is not None else "")
                    + (" MERGE (s)-[r3:" + same_name + "]->(p) SET (CASE WHEN r3.Weight IS NOT NULL THEN r3 END).Weight = r3.Weight +"
                    + "1 SET (CASE WHEN r3.Weight IS NULL THEN r3 END).Weight = 1" if sbj is not None and pred is not None else "")
                    + (" MERGE (o)-[r4:" + same_name + "]->(c) SET (CASE WHEN r4.Weight IS NOT NULL THEN r4 END).Weight = r4.Weight +"
                    + "1 SET (CASE WHEN r4.Weight IS NULL THEN r4 END).Weight = 1" if obj is not None and comp is not None else "")
                    + (" MERGE (o)-[r5:" + same_name + "]->(p) SET (CASE WHEN r5.Weight IS NOT NULL THEN r5 END).Weight = r5.Weight +"
                    + "1 SET (CASE WHEN r5.Weight IS NULL THEN r5 END).Weight = 1" if obj is not None and pred is not None else "")
                    + (" MERGE (c)-[r6:" + same_name + "]->(p) SET (CASE WHEN r6.Weight IS NOT NULL THEN r6 END).Weight = r6.Weight +"
                    + "1 SET (CASE WHEN r6.Weight IS NULL THEN r6 END).Weight = 1" if comp is not None and pred is not None else ""))
    conn.query(add_statement)
    return add_statement



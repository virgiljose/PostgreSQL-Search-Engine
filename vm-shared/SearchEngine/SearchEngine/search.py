import psycopg2
import re
import string
import sys

_PUNCTUATION = frozenset(string.punctuation)

def _remove_punc(token):
    """Removes punctuation from start/end of token."""
    i = 0
    j = len(token) - 1
    idone = False
    jdone = False
    while i <= j and not (idone and jdone):
        if token[i] in _PUNCTUATION and not idone:
            i += 1
        else:
            idone = True
        if token[j] in _PUNCTUATION and not jdone:
            j -= 1
        else:
            jdone = True
    return "" if i > j else token[i:(j+1)]

def _get_tokens(query):
    rewritten_query = []
    tokens = re.split('[ \n\r]+', query)
    for token in tokens:
        cleaned_token = _remove_punc(token)
        if cleaned_token:
            if "'" in cleaned_token:
                cleaned_token = cleaned_token.replace("'", "''")
            rewritten_query.append(cleaned_token)
    return rewritten_query



def search(query, query_type, offset):

    rewritten_query0 = _get_tokens(query)
    rewritten_query = [x.lower() for x in rewritten_query0]

    query_len = 0
    conn = None
    rows = []

    try:
        conn = psycopg2.connect(user="cs143", password="cs143", host="localhost", database="searchengine")

        print("Connection successful")
        cursor = conn.cursor()

        cursor.execute("CREATE TABLE IF NOT EXISTS search (token VARCHAR(255), isthere INTEGER)")
        cursor.execute("PREPARE getsearchvals (varchar(255)) AS INSERT INTO search (token, isthere) VALUES($1, 1);")
        for i in rewritten_query:
            cursor.execute("EXECUTE getsearchvals((%s));", [i])

        if query_type == "or":
            #cursor.execute("CREATE MATERIALIZED VIEW IF NOT EXISTS results AS SELECT song.song_name, artist.artist_name FROM song LEFT JOIN artist ON artist.artist_id = song.artist_id RIGHT JOIN (SELECT song_id, isthere FROM tfidf JOIN search ON search.token = tfidf.token ORDER BY tfidf.score) newtokens ON song.song_id = newtokens.song_id;")
            cursor.execute("""CREATE MATERIALIZED VIEW IF NOT EXISTS results AS
            SELECT song.song_name, artist.artist_name
            FROM song LEFT JOIN artist ON artist.artist_id = song.artist_id
            RIGHT JOIN (SELECT song_id, SUM(isthere) AS sumt, SUM(tfidf.score)
            FROM tfidf JOIN search ON search.token = tfidf.token
            GROUP BY song_id HAVING SUM(isthere) >= 1
            ORDER BY SUM(tfidf.score) DESC)  newtokens
            ON song.song_id = newtokens.song_id;""")
        elif query_type == "and":
            cursor.execute("""CREATE MATERIALIZED VIEW IF NOT EXISTS results AS
            SELECT song.song_name, artist.artist_name
            FROM song LEFT JOIN artist ON artist.artist_id = song.artist_id
            RIGHT JOIN (SELECT song_id, SUM(isthere) AS sumt, SUM(tfidf.score)
            FROM tfidf JOIN search ON search.token = tfidf.token
            GROUP BY song_id HAVING SUM(isthere) = (SELECT COUNT (*) FROM search)
            ORDER BY SUM(tfidf.score) DESC)  newtokens
            ON song.song_id = newtokens.song_id;""")
     #      3cursor.execute("CREATE MATERIALIZED VIEW IF NOT EXISTS results AS SELECT song.song_name, artist.artist_name FROM song LEFT JOIN artist ON artist.artist_id = song.artist_id RIGHT JOIN (SELECT song_id, SUM(isthere) AS sumt FROM tfidf JOIN search ON search.token = tfidf.token GROUP BY song_id, tfidf.score HAVING SUM(isthere) >= 0 ORDER BY tfidf.score) newtokens ON song.song_id = newtokens.song_id;")

        # cursor.execute("SELECT Count(*) FROM (SELECT * FROM results) R;")
        # query_len = int(cursor.fetchone()[0])

        cursor.execute("SELECT COUNT(*) FROM ( SELECT * FROM results ) R;")
        qlen = int(cursor.fetchone()[0])

        cursor.execute("SELECT * FROM results LIMIT 20 OFFSET %s;", [offset])
        rows = cursor.fetchall()

        ## cursor.execute("DROP MATERIALIZED VIEW IF EXISTS results CASCADE;")
        cursor.execute("DROP TABLE IF EXISTS search CASCADE;")
        cursor.close()

    except(Exception, psycopg2.DatabaseError) as erlog:
        print(erlog)
    finally:
        if conn is not None:
            conn.commit()
            conn.close()
            print("Database is closed")

    return [rows, qlen]

if __name__ == "__main__":
    if len(sys.argv) > 2:
        result = search(' '.join(sys.argv[2:]), sys.argv[1].lower())
        print(result)
    else:
        print("USAGE: python3 search.py [or|and] term1 term2 ...")

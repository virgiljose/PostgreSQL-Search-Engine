#!/usr/bin/python3

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



def search(query, query_type):

    rewritten_query = _get_tokens(query)

    """TODO
    Your code will go here. Refer to the specification for projects 1A and 1B.
    But your code should do the following:
    1. Connect to the Postgres database.
    2. Graciously handle any errors that may occur (look into try/except/finally).
    3. Close any database connections when you're done.
    4. Write queries so that they are not vulnerable to SQL injections.
    5. The parameters passed to the search function may need to be changed for 1B.
    """

    print("Connecting to database")

    # try:
    conn = psycopg2.connect(user="cs143", password="cs143", host="localhost", database="searchengine")
    # except psycopg2.Error as e:
    #     print("Error code ", e.pgcode)
    #     print("Exception: ", e.pgerror)
    #     return None

    print("Connection successful")

    # object to execute queries and fetch their results
    cursor = conn.cursor()

    cursor.execute("CREATE TABLE IF NOT EXISTS search (token VARCHAR(255), isthere INTEGER)")
    for i in rewritten_query:
        cursor.execute("INSERT INTO search (token, isthere) VALUES ((%s),1)", [i])

   if query_type == "or":
       cursor.execute("CREATE MATERIALIZED VIEW IF NOT EXISTS results AS SELECT song.song_name, artist.artist_name FROM song LEFT JOIN artist ON artist.artist_id = song.artist_id RIGHT JOIN (SELECT song_id, isthere FROM tfidf JOIN search ON search.token = tfidf.token ORDER BY tfidf.score) newtokens ON song.song_id = newtokens.song_id;")
   elif query_type == "and":
       cursor.execute("CREATE MATERIALIZED VIEW IF NOT EXISTS results AS SELECT song.song_name, artist.artist_name FROM song LEFT JOIN artist ON artist.artist_id = song.artist_id RIGHT JOIN (SELECT song_id, isthere FROM tfidf JOIN search ON search.token = tfidf.token ORDER BY tfidf.score) newtokens ON song.song_id = newtokens.song_id;")
#       cursor.execute("CREATE MATERIALIZED VIEW IF NOT EXISTS results AS SELECT song.song_name, artist.artist_name FROM song LEFT JOIN artist ON artist.artist_id = song.artist_id RIGHT JOIN (SELECT song_id, SUM(isthere) AS sumt FROM tfidf JOIN search ON search.token = tfidf.token GROUP BY song_id, tfidf.score HAVING SUM(isthere) >= 0 ORDER BY tfidf.score) newtokens ON song.song_id = newtokens.song_id;")
##
    cursor.execute("SELECT * FROM search;")

    # TODO: paginate the results
    rows = cursor.fetchall()
    # close connection
    cursor.execute("DROP MATERIALIZED VIEW IF EXISTS results CASCADE;")
    cursor.execute("DROP TABLE IF EXISTS search CASCADE;")
    cursor.close()
    conn.close()

    return rows

if __name__ == "__main__":
    if len(sys.argv) > 2:
        result = search(' '.join(sys.argv[2:]), sys.argv[1].lower())
        print(result)
    else:
        print("USAGE: python3 search.py [or|and] term1 term2 ...")

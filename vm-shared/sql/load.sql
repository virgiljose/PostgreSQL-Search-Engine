-- \copy artist FROM '~/data/artist.csv' WITH CSV DELIMITER ',' ESCAPE '"';
-- \copy song FROM '~/data/song.csv' WITH CSV DELIMITER ',' ESCAPE '"';
-- \copy token FROM '~/data/token.csv' WITH CSV DELIMITER ',' ESCAPE '"';

-- log(57650 / COUNT(s.song_id))::FLOAT
-- r.count AS tf_score, score AS df_score,

INSERT INTO "tfidf" ("song_id", "token", "score") (
  SELECT r.song_id, r.token, r.count*log(57650/score::FLOAT) AS tfidf_score
  FROM token r LEFT JOIN
    -- innermost query
     (SELECT s.token AS token, COUNT(s.song_id) AS score
      FROM token s
      GROUP BY token
      ORDER BY score DESC) songdf
  ON r.token = songdf.token
  GROUP BY r.token, r.song_id, score
  ORDER BY r.token, r.song_id);

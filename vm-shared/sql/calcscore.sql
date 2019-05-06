INSERT INTO "tfidf" ("song_id", "token", "score")
(
SELECT UNIQUE(r.song_id, r.token), score
FROM token r LEFT JOIN
 (SELECT s.token AS token, s.count AS count, s.count * log(57650 / COUNT(s.song_id))::FLOAT AS score, s.song_id AS song_id
 FROM token s
 GROUP BY token, song_id
  ORDER BY token DESC) songdf
ON r.song_id = songdf.song_id AND r.token = songdf.token

WHERE (r.song_id = 6218 AND songdf.token = 'on') OR (r.song_id = 7704 AND songdf.token = 'everywhere') OR (r.song_id = 12541 AND songdf.token ='over')

GROUP BY r.token, r.song_id, score
ORDER BY r.token, r.song_id);

-- TF is the term (token) frequency of token i in song j
-- this is already given, via in the token relation

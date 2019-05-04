INSERT INTO "tfidf" ("song_id", "token", "score")
--      (124, '24sf',10.2);



(
SELECT r.song_id, r.token, score
FROM token r LEFT JOIN
 (SELECT s.token AS token, s.count AS count, s.count * log(57650 / COUNT(s.song_id))::FLOAT AS score, s.song_id AS song_id
 FROM token s
 GROUP BY token, song_id
  ORDER BY token DESC) songdf
ON r.song_id = songdf.song_id AND r.token = songdf.token
GROUP BY r.token, r.song_id, score
ORDER BY r.token, r.song_id);

-- compute tf-idf score, for each token, in each song_name
-- # songs each token appears in
SELECT token, SUM(count) as counts, COUNT(song_id) as num_songs
FROM token LEFT JOIN song ON (token.song_id = song.song_id
GROUP BY counts;

-- # songs
SELECT COUNT(song_id)
FROM song;

-- TF is the term (token) frequency of token i in song j
-- this is already given, via in the token relation

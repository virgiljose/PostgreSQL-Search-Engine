\copy artist FROM '~/data/artist.csv' WITH CSV DELIMITER ',' ESCAPE '"';
\copy song FROM '~/data/song.csv' WITH CSV DELIMITER ',' ESCAPE '"';
\copy token FROM '~/data/token.csv' WITH CSV DELIMITER ',' ESCAPE '"';

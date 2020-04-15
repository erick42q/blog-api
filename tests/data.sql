INSERT INTO user (username, public_id, password)
VALUES
  ('test', 'f5e1ffe6-6df6-418d-92cd-11c15354afb0', 'pbkdf2:sha256:150000$PxJpAhAC$712d11f8aff4ed4d4e52dd3c739a2bedf2b85c1b26dd3a95aaa97359904a91e5'),
  ('other', '2965ecdd-6d4e-455c-9788-869af0829d3b', 'pbkdf2:sha256:50000$kJPKsz6N$d2d4784f1b030a9761f5ccaeeaca413f27f2ecb76d6168407af962ddce849f79');

INSERT INTO post (title, body, author_id, created)
VALUES
  ('test title', 'test' || x'0a' || 'body', 1, '2018-01-01 00:00:00');

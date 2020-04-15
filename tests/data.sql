INSERT INTO user (username, public_id, password)
VALUES
  ('test', '1ed6a8d3-e69e-4551-85fd-a1ab9625f5d9', 'pbkdf2:sha256:150000$PxJpAhAC$712d11f8aff4ed4d4e52dd3c739a2bedf2b85c1b26dd3a95aaa97359904a91e5'),
  ('test2', '870cdb97-53a3-48f4-9c67-548be36408a3', 'pbkdf2:sha256:150000$6BIM5QjC$214c1bd72e489eefc93f5186401d2fc1110e6e60238cde367e96d2879e7c6922');

INSERT INTO post (title, body, author_id, created)
VALUES
  ('test title', 'test' || x'0a' || 'body', 1, '2018-01-01 00:00:00');

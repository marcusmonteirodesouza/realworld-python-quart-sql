CREATE TABLE IF NOT EXISTS users(
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  username TEXT NOT NULL UNIQUE,
  email TEXT NOT NULL UNIQUE,
  password_hash TEXT NOT NULL,
  bio TEXT,
  image TEXT,
  created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT current_timestamp,
  updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT current_timestamp
);

CREATE TABLE IF NOT EXISTS follows(
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  follower_id UUID references users(id),
  followed_id UUID references users(id),
  created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT current_timestamp,
  deleted_at TIMESTAMP WITH TIME ZONE,
  UNIQUE(follower_id, followed_id),
  CHECK(follower_id <> followed_id)
);

CREATE TABLE IF NOT EXISTS articles(
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  author_id UUID references users(id),
  slug TEXT NOT NULL UNIQUE,
  title TEXT NOT NULL,
  description TEXT NOT NULL,
  body TEXT NOT NULL,
  tags TEXT[],
  created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT current_timestamp,
  updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT current_timestamp,
  deleted_at TIMESTAMP WITH TIME ZONE
);


CREATE TABLE IF NOT EXISTS favorites(
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  article_id UUID references articles(id),
  user_id UUID references users(id),
  created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT current_timestamp,
  deleted_at TIMESTAMP WITH TIME ZONE,
  UNIQUE(article_id, user_id)
);

CREATE TABLE IF NOT EXISTS comments(
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  article_id UUID references articles(id),
  author_id UUID references users(id),
  body TEXT NOT NULL,
  created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT current_timestamp,
  updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT current_timestamp,
  deleted_at TIMESTAMP WITH TIME ZONE
);

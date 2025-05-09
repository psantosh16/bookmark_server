# Database Structure and Optimization Guide

## Database Schema

### Core Tables

```sql
-- Users Table
CREATE TABLE users (
    uid UUID PRIMARY KEY,
    name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    avatar TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Bookmarks Table (Immutable)
CREATE TABLE bookmarks (
    id UUID PRIMARY KEY,
    title TEXT NOT NULL,
    description TEXT,
    image_url TEXT,
    source_url TEXT UNIQUE NOT NULL,
    source_type TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
    -- No updated_at as bookmarks are immutable
    -- No deleted_at as bookmarks cannot be deleted
) PARTITION BY RANGE (created_at);

-- User Bookmarks Junction Table (Mutable)
CREATE TABLE user_bookmarks (
    user_id UUID REFERENCES users(uid),
    bookmark_id UUID REFERENCES bookmarks(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    deleted_at TIMESTAMP WITH TIME ZONE, -- For soft delete of user's bookmark
    PRIMARY KEY (user_id, bookmark_id)
);

-- User Spaces Table (Mutable)
CREATE TABLE user_spaces (
    id UUID PRIMARY KEY,
    space_id TEXT NOT NULL,
    space_name TEXT NOT NULL,
    description TEXT, -- Added description for space
    user_id UUID REFERENCES users(uid),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    deleted_at TIMESTAMP WITH TIME ZONE, -- For soft delete of space
    UNIQUE(user_id, space_name) -- Prevent duplicate space names per user
);

-- Space Bookmarks Junction Table (Mutable)
CREATE TABLE space_bookmarks (
    space_id UUID REFERENCES user_spaces(id),
    bookmark_id UUID REFERENCES bookmarks(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    deleted_at TIMESTAMP WITH TIME ZONE, -- For soft delete of bookmark from space
    PRIMARY KEY (space_id, bookmark_id)
);
```

## Optimizations

### 1. Indexes

-- Core Indexes:
-- These indexes are created to enhance the performance of join operations and lookups.
-- 1. `idx_user_bookmarks_user_bookmark`: This index is on the `user_bookmarks` table for the combination of `user_id` and `bookmark_id`.
-- 2. `idx_space_bookmarks_space_bookmark`: This index is on the `space_bookmarks` table for the combination of `space_id` and `bookmark_id`.
-- 3. `idx_bookmarks_source_url`: This unique index is on the `bookmarks` table for the `source_url` column to ensure uniqueness and fast lookups.



-- Partial Indexes for Active Records:
-- These indexes are created to improve query performance for active records, i.e., records that have not been soft-deleted.
-- 1. `idx_active_user_bookmarks`: This index is on the `user_bookmarks` table for `user_id` where `deleted_at` is NULL.
-- 2. `idx_active_user_spaces`: This index is on the `user_spaces` table for `user_id` where `deleted_at` is NULL.
-- 3. `idx_active_space_bookmarks`: This index is on the `space_bookmarks` table for `space_id` where `deleted_at` is NULL.



-- Space Name Index:
-- This index is created to optimize queries that involve searching for spaces by name.
-- 1. `idx_user_spaces_name`: This index is on the `user_spaces` table for the combination of `user_id` and `space_name`.


```sql
-- Core Indexes
CREATE INDEX idx_user_bookmarks_user_bookmark ON user_bookmarks(user_id, bookmark_id);
CREATE INDEX idx_space_bookmarks_space_bookmark ON space_bookmarks(space_id, bookmark_id);
CREATE UNIQUE INDEX idx_bookmarks_source_url ON bookmarks(source_url);

-- Partial Indexes for Active Records
CREATE INDEX idx_active_user_bookmarks ON user_bookmarks(user_id) 
WHERE deleted_at IS NULL;
CREATE INDEX idx_active_user_spaces ON user_spaces(user_id) 
WHERE deleted_at IS NULL;
CREATE INDEX idx_active_space_bookmarks ON space_bookmarks(space_id) 
WHERE deleted_at IS NULL;

-- Space Name Index
CREATE INDEX idx_user_spaces_name ON user_spaces(user_id, space_name);
```

### 2. Materialized Views

The materialized view `user_bookmarks_with_spaces` is designed to provide a comprehensive overview of a user's active bookmarks along with the spaces they are associated with. It aggregates data from multiple tables, including `users`, `user_bookmarks`, `bookmarks`, `space_bookmarks`, and `user_spaces`. The view includes details such as the bookmark's title, description, source URL, source type, and image URL. Additionally, it compiles a JSON array of spaces, each containing the space ID, name, and description, where the bookmark is currently active. This view is optimized for performance by precomputing and storing the results, which can be refreshed using the `refresh_bookmark_views` function to ensure the data remains up-to-date.


```sql
-- User's Active Bookmarks with Spaces View
CREATE MATERIALIZED VIEW user_bookmarks_with_spaces AS
SELECT 
    u.uid as user_id,
    b.id as bookmark_id,
    b.title,
    b.description,
    b.source_url,
    b.source_type,
    b.image_url,
    json_agg(DISTINCT jsonb_build_object(
        'space_id', us.id,
        'space_name', us.space_name,
        'description', us.description
    )) FILTER (WHERE us.id IS NOT NULL) as spaces
FROM users u
JOIN user_bookmarks ub ON u.uid = ub.user_id
JOIN bookmarks b ON b.id = ub.bookmark_id
LEFT JOIN space_bookmarks sb ON b.id = sb.bookmark_id AND sb.deleted_at IS NULL
LEFT JOIN user_spaces us ON sb.space_id = us.id AND us.deleted_at IS NULL
WHERE ub.deleted_at IS NULL
GROUP BY u.uid, b.id, b.title, b.description, b.source_url, b.source_type, b.image_url;

-- Refresh function
CREATE OR REPLACE FUNCTION refresh_bookmark_views()
RETURNS void AS $$
BEGIN
    REFRESH MATERIALIZED VIEW user_bookmarks_with_spaces;
END;
$$ LANGUAGE plpgsql;
```

## Common Queries

-- This section provides common SQL queries that can be used to interact with the database schema described above. 
-- These queries are designed to help you retrieve and manipulate data efficiently.

-- 1. Get User's Active Bookmarks with Spaces
-- This query retrieves all active bookmarks for a specific user, along with the spaces they are associated with.
-- It uses a materialized view for optimized performance, ensuring that the data is precomputed and quickly accessible.

-- 2. Add Bookmark to User's Collection
-- This query allows you to add a new bookmark to a user's collection.
-- It first attempts to insert a new bookmark into the bookmarks table.
-- If a bookmark with the same source URL already exists, it avoids duplication by using the existing bookmark ID.

-- 3. Add Bookmark to Space
-- This query enables you to associate an existing bookmark with a specific space.
-- It ensures that the bookmark is linked to the space, allowing for organized categorization and retrieval.

-- These queries are essential for managing user bookmarks and spaces, providing a robust framework for data interaction.


### 1. Get User's Active Bookmarks with Spaces

```sql
-- Using Materialized View
SELECT * FROM user_bookmarks_with_spaces
WHERE user_id = 'user123';

-- Using CTEs
WITH user_active_bookmarks AS (
    SELECT b.* 
    FROM bookmarks b
    JOIN user_bookmarks ub ON b.id = ub.bookmark_id
    WHERE ub.user_id = 'user123'
    AND ub.deleted_at IS NULL
),
bookmark_spaces AS (
    SELECT b.id, json_agg(jsonb_build_object(
        'space_id', us.id,
        'space_name', us.space_name,
        'description', us.description
    )) as spaces
    FROM user_active_bookmarks b
    LEFT JOIN space_bookmarks sb ON b.id = sb.bookmark_id AND sb.deleted_at IS NULL
    LEFT JOIN user_spaces us ON sb.space_id = us.id AND us.deleted_at IS NULL
    GROUP BY b.id
)
SELECT b.*, bs.spaces
FROM user_active_bookmarks b
LEFT JOIN bookmark_spaces bs ON b.id = bs.id;
```

### 2. Add Bookmark to User's Collection

```sql
WITH new_bookmark AS (
    INSERT INTO bookmarks (title, description, source_url, source_type, image_url)
    VALUES ('My Bookmark', 'Description', 'https://example.com', 'article', 'https://image.com')
    ON CONFLICT (source_url) DO NOTHING
    RETURNING id
)
INSERT INTO user_bookmarks (user_id, bookmark_id)
SELECT 'user123', COALESCE(
    (SELECT id FROM new_bookmark),
    (SELECT id FROM bookmarks WHERE source_url = 'https://example.com')
);
```

### 3. Add Bookmark to Space

```sql
INSERT INTO space_bookmarks (space_id, bookmark_id)
VALUES ('space123', 'bookmark123')
ON CONFLICT (space_id, bookmark_id) 
WHERE deleted_at IS NULL
DO NOTHING;
```

### 4. Remove Bookmark from Space (Soft Delete)

```sql
UPDATE space_bookmarks
SET deleted_at = NOW()
WHERE space_id = 'space123' 
AND bookmark_id = 'bookmark123'
AND deleted_at IS NULL;
```

### 5. Remove Bookmark from User's Collection (Soft Delete)

```sql
UPDATE user_bookmarks
SET deleted_at = NOW()
WHERE user_id = 'user123' 
AND bookmark_id = 'bookmark123'
AND deleted_at IS NULL;
```

## Maintenance

### 1. Regular Maintenance Function

```sql
CREATE OR REPLACE FUNCTION maintain_bookmarks()
RETURNS void AS $$
BEGIN
    -- Update statistics
    ANALYZE bookmarks;
    ANALYZE user_bookmarks;
    
    -- Refresh materialized views
    REFRESH MATERIALIZED VIEW user_bookmarks_with_spaces;
END;
$$ LANGUAGE plpgsql;
```

## Security

### 1. Row Level Security (RLS)

```sql
-- Enable RLS
ALTER TABLE bookmarks ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_bookmarks ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_spaces ENABLE ROW LEVEL SECURITY;
ALTER TABLE space_bookmarks ENABLE ROW LEVEL SECURITY;

-- Create policies
CREATE POLICY "Users can view their own bookmarks"
    ON bookmarks FOR SELECT
    USING (EXISTS (
        SELECT 1 FROM user_bookmarks
        WHERE user_bookmarks.bookmark_id = bookmarks.id
        AND user_bookmarks.user_id = auth.uid()
        AND user_bookmarks.deleted_at IS NULL
    ));

CREATE POLICY "Users can manage their own spaces"
    ON user_spaces FOR ALL
    USING (user_id = auth.uid());

CREATE POLICY "Users can manage bookmarks in their spaces"
    ON space_bookmarks FOR ALL
    USING (EXISTS (
        SELECT 1 FROM user_spaces
        WHERE user_spaces.id = space_bookmarks.space_id
        AND user_spaces.user_id = auth.uid()
    ));
```

## Performance Optimization Tips

1. **Query Optimization**:
   - Use CTEs for complex queries
   - Implement LATERAL joins for better performance
   - Use appropriate indexes
   - Monitor query performance

2. **Data Management**:
   - Partitioning for bookmarks table
   - Materialized views for common queries
   - Soft delete implementation for user_bookmarks and spaces

3. **Monitoring**:
   - Regular statistics updates
   - Index usage monitoring
   - Table size monitoring
   - Query performance tracking

4. **Caching Strategy**:
   - Use Redis for frequently accessed data
   - Cache user's active bookmarks
   - Cache space contents
   - Cache materialized views
   - Use appropriate cache invalidation strategies 
from graphviz import Digraph

def create_erd():
    dot = Digraph(comment='Database ERD')
    dot.attr(rankdir='LR')  # Left to Right direction
    
    # Node styling
    dot.attr('node', shape='rectangle', style='rounded')
    
    # Users table
    dot.node('users', '''Users
    uid (PK)
    name
    email
    avatar
    created_at
    updated_at''')
    
    # Bookmarks table (Immutable)
    dot.node('bookmarks', '''Bookmarks [Immutable]
    id (PK)
    title
    description
    image_url
    source_url (UQ)
    source_type
    created_at
    [Partitioned]''')
    
    # User Bookmarks junction table (Mutable)
    dot.node('user_bookmarks', '''User Bookmarks [Mutable]
    user_id (FK)
    bookmark_id (FK)
    created_at
    updated_at
    deleted_at
    [Indexed]''')
    
    # User Spaces table (Mutable)
    dot.node('user_spaces', '''User Spaces [Mutable]
    id (PK)
    space_id
    space_name
    description
    user_id (FK)
    created_at
    updated_at
    deleted_at
    [UQ: user_id, space_name]''')
    
    # Space Bookmarks junction table (Mutable)
    dot.node('space_bookmarks', '''Space Bookmarks [Mutable]
    space_id (FK)
    bookmark_id (FK)
    created_at
    deleted_at
    [Indexed]''')
    
    # Materialized View
    dot.node('user_bookmarks_view', '''User Bookmarks View
    [Materialized View]
    user_id
    bookmark_id
    title
    description
    source_url
    source_type
    image_url
    spaces''', style='dashed')
    
    # Relationships
    dot.edge('users', 'user_bookmarks', '1:N')
    dot.edge('bookmarks', 'user_bookmarks', '1:N')
    dot.edge('users', 'user_spaces', '1:N')
    dot.edge('user_spaces', 'space_bookmarks', '1:N')
    dot.edge('bookmarks', 'space_bookmarks', '1:N')
    dot.edge('user_bookmarks_view', 'users', 'View', style='dashed')
    dot.edge('user_bookmarks_view', 'bookmarks', 'View', style='dashed')
    
    # Save the diagram
    dot.render('database_erd', format='png', cleanup=True)

if __name__ == '__main__':
    create_erd() 
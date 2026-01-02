
@router.get("/books/search")
async def search_books(
    query: str = None,
    availability: str = None,
    category: str = None,
    current_user: dict = Depends(get_student_user)
):
    """
    Search books by title, author, or subject with filters
    """
    try:
        supabase = get_supabase_client()
        
        # Base query
        db_query = supabase.table("books").select("*")
        
        # Apply search query
        if query:
            # PostgreSQL ilike syntax for multiple columns needs OR logic which Supabase checks via 'or' filter
            # syntax: .or_('title.ilike.%query%,author.ilike.%query%,subject.ilike.%query%')
            search_param = f"title.ilike.%{query}%,author.ilike.%{query}%,subject.ilike.%{query}%"
            db_query = db_query.or_(search_param)
        
        # Apply availability filter
        if availability == "available":
            db_query = db_query.gt("available_copies", 0)
        elif availability == "unavailable":
            db_query = db_query.eq("available_copies", 0)
            
        # Apply category/subject filter
        if category and category != "all-categories":
            # Mapping frontend values to DB values if needed, or assuming direct match
            # The frontend uses 'cs', 'programming' etc. We might need to map them or just use generic ilike
            if category == "cs":
                db_query = db_query.ilike("subject", "%Computer Science%")
            elif category == "programming":
                 db_query = db_query.ilike("subject", "%Programming%")
            elif category == "se":
                 db_query = db_query.ilike("subject", "%Software Engineering%")
            else:
                 db_query = db_query.ilike("subject", f"%{category}%")

        response = db_query.execute()
        
        books = []
        if response.data:
            for book in response.data:
                books.append({
                    "id": book["id"],
                    "title": book["title"],
                    "author": book["author"],
                    "subject": book["subject"],
                    "available": book["available_copies"],
                    "total": book["total_copies"],
                    "description": book.get("description", "")
                })
                
        return {"books": books}

    except Exception as e:
        logger.error(f"Search books error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/books/{book_id}")
async def get_book_details(
    book_id: str,
    current_user: dict = Depends(get_student_user)
):
    """
    Get detailed information for a specific book
    """
    try:
        supabase = get_supabase_client()
        
        response = supabase.table("books")\
            .select("*")\
            .eq("id", book_id)\
            .single()\
            .execute()
            
        if not response.data:
            raise HTTPException(status_code=404, detail="Book not found")
            
        return {"book": response.data}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get book details error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

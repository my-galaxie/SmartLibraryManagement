# Database Setup - Step by Step Guide

## You Got This Error!

```
Error: Failed to run sql query: ERROR: 42703: column "subject" does not exist
```

This means the **schema.sql** wasn't fully executed. Let's fix it!

---

## ✅ Correct Steps (Follow These Exactly)

### Step 1: Clear Any Partial Setup

In Supabase SQL Editor, run this **first** to clean up:

```sql
-- Drop all tables if they exist (this is safe)
DROP TABLE IF EXISTS public.availability_subscriptions CASCADE;
DROP TABLE IF EXISTS public.fines CASCADE;
DROP TABLE IF EXISTS public.notifications CASCADE;
DROP TABLE IF EXISTS public.borrows CASCADE;
DROP TABLE IF EXISTS public.book_copies CASCADE;
DROP TABLE IF EXISTS public.books CASCADE;
DROP TABLE IF EXISTS public.user_profiles CASCADE;
DROP TABLE IF EXISTS public.resources CASCADE;
DROP TABLE IF EXISTS public.system_config CASCADE;
```

1. **Copy the SQL above**
2. **Paste into Supabase SQL Editor**
3. **Click "Run"**
4. Should say "Success"

---

### Step 2: Execute the Complete Schema

Now execute the **FULL** schema.sql file:

1. **Open**: `backend/database/schema.sql` in VS Code (you already have it open!)
2. **Select ALL** the contents (Ctrl+A)
3. **Copy** (Ctrl+C)
4. **Go back to Supabase SQL Editor**
5. **Clear the editor** (delete the previous query)
6. **Paste** the schema.sql contents (Ctrl+V)
7. **Click "Run"**

**Expected Result**: Should say "Success. No rows returned" - this is GOOD!

The query will take ~10 seconds to run. Be patient!

---

### Step 3: Verify Tables Were Created

Run this to check:

```sql
SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'public' 
ORDER BY table_name;
```

You should see these tables:
- `availability_subscriptions`
- `book_copies`
- `books`
- `borrows`
- `fines`
- `notifications`
- `resources`
- `system_config`
- `user_profiles`

---

### Step 4: Add Sample Data (Optional)

Once the schema is successful, you can add test books:

1. **Open**: `backend/database/seed.sql`
2. **Copy ALL contents**
3. **Paste into Supabase SQL Editor**
4. **Click "Run"**

This adds ~10 sample books for testing.

---

## 📸 Screenshot Guide

![Screenshot showing setup](file:///C:/Users/Sahana/.gemini/antigravity/brain/92637a3e-2994-4c0b-8464-2bd860b6ad59/uploaded_image_1766927745756.png)

In your screenshot, I see you're in the SQL Editor. Make sure to:
1. **Clear the current query** (the one that errored)
2. **Paste the FULL schema.sql** (all ~400 lines)
3. **Run it**

---

## Common Mistakes to Avoid

❌ **Don't run seed.sql first** - Run schema.sql first!  
❌ **Don't run partial SQL** - Copy the ENTIRE file  
❌ **Don't skip the cleanup step** if you had errors  

✅ **Do run schema.sql completely**  
✅ **Do wait for "Success" message**  
✅ **Do check that tables were created**  

---

## After Successful Schema Execution

Once you see "Success. No rows returned":

1. **Tell me "done"** or **"schema executed"**
2. I'll start the backend server for you
3. Then you can test the app!

---

## Need Help?

If you still get errors:
1. Take a screenshot of the error
2. Share it with me
3. I'll help you fix it

The most important thing is to copy the **ENTIRE schema.sql file** and run it completely!

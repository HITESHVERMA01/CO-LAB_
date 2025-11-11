# Supabase Setup Guide for CO:LAB

## Required Tables

You need to create two tables in your Supabase database:

### 1. **profiles** Table

Create a table named `profiles` with the following columns:

| Column Name | Type | Settings |
|------------|------|----------|
| email | text | Primary Key |
| name | text | |
| class | text | |
| skills | text | |
| goals | text | |
| created_at | timestamptz | Default: now() |

**Steps:**
1. Go to https://supabase.com and sign in
2. Open your project
3. Click "SQL Editor" in the left sidebar
4. Click "New Query"
5. Paste this SQL:

```sql
CREATE TABLE profiles (
  email TEXT PRIMARY KEY,
  name TEXT NOT NULL,
  class TEXT NOT NULL,
  skills TEXT,
  goals TEXT,
  created_at TIMESTAMPTZ DEFAULT now()
);
```

6. Click "Run"

---

### 2. **messages** Table

Create a table named `messages` with the following columns:

| Column Name | Type | Settings |
|------------|------|----------|
| id | bigint | Primary Key, Auto-increment |
| sender_email | text | |
| receiver_email | text | |
| message | text | |
| created_at | timestamptz | Default: now() |

**Steps:**
1. Go to SQL Editor again
2. Click "New Query"
3. Paste this SQL:

```sql
CREATE TABLE messages (
  id BIGSERIAL PRIMARY KEY,
  sender_email TEXT NOT NULL,
  receiver_email TEXT NOT NULL,
  message TEXT NOT NULL,
  created_at TIMESTAMPTZ DEFAULT now()
);
```

4. Click "Run"

---

## Verify Tables Were Created

1. Go to the "Table Editor" in the left sidebar
2. You should see both `profiles` and `messages` tables listed

---

## Set Row-Level Security (RLS) - Optional but Recommended

For security, enable RLS on both tables:

1. Click on the `profiles` table
2. Click "RLS" (Row Level Security)
3. Enable RLS
4. Add policies as needed (allow all for now if testing)
5. Repeat for `messages` table

---

## Test the Connection

Run your CO:LAB app:
```bash
python -m streamlit run co_lab.py
```

If you see "Could not connect to Supabase" error, double-check:
- ✅ Your SUPABASE_URL is correct in `.streamlit/secrets.toml`
- ✅ Your SUPABASE_KEY is correct in `.streamlit/secrets.toml`
- ✅ Both `profiles` and `messages` tables exist in Supabase

---

## Testing Chat

1. Create Profile 1:
   - Email: user1@example.com
   - Name: User One
   - Other fields: fill as you like

2. Create Profile 2:
   - Email: user2@example.com
   - Name: User Two
   - Other fields: fill as you like

3. Find matches as User 1
4. Start chat with User 2
5. Send a message
6. Check if the message appears in the "All Members" tab by viewing the messages table in Supabase

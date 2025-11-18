# FastAPI + SQLModel BookStore API

This project is a **lab-style FastAPI application** that demonstrates how to build
a simple Bookstore REST API using:

- **FastAPI** for the web/API framework
- **SQLModel** (SQLAlchemy + Pydantic) for data models and ORM
- **SQLite or MySQL** as the database
- **Environment variables** for configuration (title, version, root path, DB URL)

It is based on your step‑by‑step experiment and also includes the **errors you faced**
and how to fix them, so that future you (or any learner) can follow without confusion.

---

## 1. Project Structure

```bash
fastapi-sqlmodel-app/
├── app/
│   ├── __init__.py
│   ├── api.py          # FastAPI router with /books endpoints
│   ├── crud.py         # Create/Read/Update/Delete functions
│   ├── database.py     # Engine, session dependency, create tables
│   ├── main.py         # FastAPI app, ROOT_PATH config, startup
│   ├── models.py       # SQLModel ORM models (Book table)
│   └── schemas.py      # Pydantic/SQLModel schemas for requests/responses
│
├── .env.example        # Example environment variables
├── requirements.txt    # Python dependencies
├── Dockerfile          # Docker image configuration
├── docker-compose.yml   # Docker Compose configuration
├── .dockerignore       # Files to exclude from Docker build
└── README.md           # This guide
```

---

## 2. Python Environment Setup (Poridhi / Ubuntu)

### 2.1. Install `python3-pip` (if not installed)

```bash
sudo apt update
sudo apt install -y python3-pip
```

### 2.2. Create a virtual environment

You originally got this error:

> The virtual environment was not created successfully because ensurepip is not  
> available. On Debian/Ubuntu systems, you need to install the python3-venv package

The fix is:

```bash
sudo apt install -y python3.12-venv
rm -rf venv
python3 -m venv venv
```

Then activate it:

```bash
source venv/bin/activate
```

Verify:

```bash
python --version
pip --version
```

---

## 3. Install Dependencies

From inside the project root (`fastapi-sqlmodel-app/`):

```bash
pip install -r requirements.txt
```

---

## 4. Database Options

### 4.1. Default: SQLite (no extra setup)

If you do nothing, the app will use:

```text
DATABASE_URL=sqlite:///./test.db
```

defined as the default in `app/database.py`.  
This creates a file named `test.db` in the project root.

---

### 4.2. MySQL via Docker Compose (Recommended)

When using `docker-compose up`, MySQL is automatically configured and connected. The database connection string is set in `docker-compose.yml`:

```text
DATABASE_URL=mysql+pymysql://bookstore_user:bookstore_password@db:3306/bookstore_db
```

### 4.3. MySQL via Docker (Standalone - Optional)

If you want to run MySQL separately:

```bash
docker run --name fastapi-mysql \
  -e MYSQL_ROOT_PASSWORD=<your_root_password> \
  -e MYSQL_DATABASE=fastapi_db \
  -p 3306:3306 \
  -v mysql_data:/var/lib/mysql \
  -d mysql:latest
```

Then set in your `.env`:

```text
DATABASE_URL="mysql+pymysql://root:<your_root_password>@127.0.0.1:3306/fastapi_db"
```

---

## 5. Environment Variables (`.env`)

Copy the example and adjust:

```bash
cp .env.example .env
```

Open `.env` and configure:

```text
ROOT_PATH=/api
API_TITLE=BookStore API
API_VERSION=1.0.0

# Keep SQLite or switch to MySQL URL
DATABASE_URL=sqlite:///./test.db
```

### 🔍 ROOT_PATH, Swagger and URLs

You faced a **NameError: ROOT_PATH is not defined** when `main.py` contained:

```python
app = FastAPI(root_path=ROOT_PATH, title=API_TITLE, version=API_VERSION)
```

without defining `ROOT_PATH`.

The fix implemented here is:

```python
ROOT_PATH = os.getenv("ROOT_PATH", "/")
app = FastAPI(root_path=ROOT_PATH, title=API_TITLE, version=API_VERSION)
```

With your `.env`:

```text
ROOT_PATH=/api
```

the final URLs are:

- Swagger UI: `http://127.0.0.1:8000/api/docs`
- Root endpoint: `http://127.0.0.1:8000/api/`
- Books list: `http://127.0.0.1:8000/api/api/v1/books/`

> Note: the "double" `/api/api/v1` comes from
> `ROOT_PATH=/api` + router prefix `/api/v1`.

If you want cleaner URLs, you can change the router prefix to `/v1` in `app/api.py`
usage in `main.py`:

```python
app.include_router(router, prefix="/v1")
```

Then list books would be: `http://127.0.0.1:8000/api/v1/books/`.

---

## 6. Application Code Overview

### 6.1. Database (`app/database.py`)

- Loads `DATABASE_URL` from `.env`
- Creates SQLModel engine
- Defines `get_session()` for FastAPI dependency injection
- Defines `create_db_and_tables()` to create tables on startup

### 6.2. Models (`app/models.py`)

- `BookBase`: common fields (title, author, year, price, in_stock, description,
  created_at, updated_at)
- `Book`: extends `BookBase` and sets `table=True` and primary key `id`

`update_timestamp()` is used on update to bump `updated_at`.

### 6.3. Schemas (`app/schemas.py`)

- `BookCreate`: payload for POST `/books/`
- `BookRead`: response model when reading from API
- `BookUpdate`: partial update payload for PUT `/books/{id}`
- `BookSearchResults`: future helper for paginated responses

### 6.4. CRUD (`app/crud.py`)

Implements the core DB operations:

- `create_book`
- `get_book`
- `get_books`
- `update_book`
- `delete_book`

Key parts:

```python
db_book = Book.from_orm(book)
for key, value in book_data.dict(exclude_unset=True).items():
    setattr(db_book, key, value)
```

- `from_orm` converts `BookCreate` to a `Book` ORM object.
- `exclude_unset=True` ensures only provided fields are updated.

### 6.5. API Router (`app/api.py`)

Registers five endpoints:

- `POST /books/` → create
- `GET /books/` → list with `offset` / `limit`
- `GET /books/{book_id}` → get one
- `PUT /books/{book_id}` → update
- `DELETE /books/{book_id}` → delete

This router is included in `main.py` with a prefix:

```python
app.include_router(router, prefix="/api/v1")
```

---

### 6.6. Main Application (`app/main.py`)

- Loads `.env`
- Reads `API_TITLE`, `API_VERSION`, `ROOT_PATH`
- Creates FastAPI app with `root_path=ROOT_PATH`
- Defines a small `/` endpoint to show config
- On startup, calls `create_db_and_tables()`
- Includes the book router under `/api/v1`

---

## 7. Running the Application

### 7.1. Using Docker Compose (Recommended)

The easiest way to run the application with MySQL database:

```bash
# Build and start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down

# Stop and remove volumes (clean slate)
docker-compose down -v
```

Once running, access:
- Root: `http://127.0.0.1:8000/`
- Swagger UI: `http://127.0.0.1:8000/docs`
- List books: `http://127.0.0.1:8000/api/v1/books/`

### 7.2. Using Docker (Standalone)

Build the Docker image:

```bash
docker build -t fastapi-bookstore .
```

Run the container (with SQLite):

```bash
docker run -p 8000:8000 \
  -e DATABASE_URL=sqlite:///./test.db \
  -e API_TITLE="BookStore API" \
  -e API_VERSION="1.0.0" \
  fastapi-bookstore
```

### 7.3. Local Development (Without Docker)

From the project root with the virtualenv activated:

```bash
uvicorn app.main:app --reload
```

If `ROOT_PATH=/api` in `.env`, then:

- Root: `http://127.0.0.1:8000/api/`
- Swagger UI: `http://127.0.0.1:8000/api/docs`
- List books: `http://127.0.0.1:8000/api/api/v1/books/`

---

## 8. Testing the API with `curl`

Make sure the server is running.

### 8.1. List all books

```bash
curl -X GET "http://127.0.0.1:8000/api/api/v1/books/" \
  -H "accept: application/json"
```

### 8.2. Create a new book

```bash
curl -X POST "http://127.0.0.1:8000/api/api/v1/books/" \
  -H "accept: application/json" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "The Great Gatsby",
    "author": "F. Scott Fitzgerald",
    "year": 1925,
    "price": 10.99,
    "in_stock": true,
    "description": "A novel set in the 1920s."
  }'
```

### 8.3. Get a specific book (e.g. ID = 1)

```bash
curl -X GET "http://127.0.0.1:8000/api/api/v1/books/1" \
  -H "accept: application/json"
```

### 8.4. Update a book

```bash
curl -X PUT "http://127.0.0.1:8000/api/api/v1/books/1" \
  -H "accept: application/json" \
  -H "Content-Type: application/json" \
  -d '{
    "price": 20.99,
    "in_stock": false
  }'
```

### 8.5. Delete a book

```bash
curl -X DELETE "http://127.0.0.1:8000/api/api/v1/books/1" \
  -H "accept: application/json"
```

---

## 9. Testing via Swagger UI

Open in your browser:

```text
http://127.0.0.1:8000/api/docs
```

- Try `GET /api/v1/books/`
- Try `POST /api/v1/books/`
- Try `GET /api/v1/books/{book_id}`
- Try `PUT /api/v1/books/{book_id}`
- Try `DELETE /api/v1/books/{book_id}`

Swagger uses the same schemas (`BookCreate`, `BookRead`, etc.) to validate input
and document responses.

---

## 10. Verifying the Database

### 10.1. SQLite

You should see a `test.db` file in the project root.  
You can inspect it using tools like `sqlite3` or a GUI browser.

### 10.2. MySQL

Check container:

```bash
docker ps
```

Enter MySQL shell:

```bash
docker exec -it fastapi-mysql mysql -uroot -p
```

Then:

```sql
SHOW DATABASES;
USE fastapi_db;
SHOW TABLES;
SELECT * FROM book;
```

You should see rows corresponding to the books you created via the API.

---

## 11. Troubleshooting Summary

### 11.1. Virtualenv error – `ensurepip is not available`

**Cause:** `python3-venv` not installed.  
**Fix:**

```bash
sudo apt install -y python3.12-venv
rm -rf venv
python3 -m venv venv
source venv/bin/activate
```

---

### 11.2. `NameError: name 'ROOT_PATH' is not defined`

**Cause:** Using `root_path=ROOT_PATH` before defining `ROOT_PATH`.

**Fix implemented in this project:**

```python
from dotenv import load_dotenv

load_dotenv()
ROOT_PATH = os.getenv("ROOT_PATH", "/")
app = FastAPI(root_path=ROOT_PATH, ...)
```

---

### 11.3. Swagger 404 or wrong URL

**Cause:** `ROOT_PATH` and actual URL mismatched.

**Rule:**

```text
Swagger URL = http://<host>:<port> + ROOT_PATH + /docs
```

With:

```text
ROOT_PATH=/api
```

Swagger is at:

```text
http://127.0.0.1:8000/api/docs
```

---

You can now use this project as a base template for any small FastAPI + SQLModel
lab and extend it with new models (Users, Orders, etc.), authentication, and more.

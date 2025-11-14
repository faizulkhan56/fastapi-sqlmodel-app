# FastAPI-SQLModel Application Architecture

## Project Overview

This is a **FastAPI** application using **SQLModel** for database operations. It implements a BookStore API with CRUD operations following a clean, layered architecture pattern.

---

## File-by-File Component Connections

### 1. **`app/main.py`** - Application Entry Point

**Purpose**: Initializes the FastAPI application and wires all components together.

**Key Responsibilities**:
- Creates the FastAPI app instance
- Loads environment variables using `python-dotenv`
- Registers the API router
- Sets up database tables on startup

**Connections**:
```
main.py
├── imports from app.database → create_db_and_tables()
├── imports from app.api → router
└── includes router at /api/v1 prefix
```

**Flow**:
1. On application startup → calls `create_db_and_tables()` from `database.py`
2. Registers all API routes → includes `router` from `api.py` at `/api/v1`

---

### 2. **`app/database.py`** - Database Configuration

**Purpose**: Manages database connection and session lifecycle.

**Key Responsibilities**:
- Creates SQLModel/SQLAlchemy engine
- Provides database session dependency for FastAPI
- Creates database tables from models

**Connections**:
```
database.py
├── uses SQLModel.metadata → from models.py (implicitly)
├── creates engine → connects to database (SQLite/MySQL)
└── get_session() → used as FastAPI dependency in api.py
```

**Key Components**:
- `engine`: SQLAlchemy engine created from `DATABASE_URL`
- `create_db_and_tables()`: Creates all tables defined in `models.py`
- `get_session()`: FastAPI dependency that yields database sessions

---

### 3. **`app/models.py`** - Database Models

**Purpose**: Defines the database table structure using SQLModel.

**Key Responsibilities**:
- Defines `BookBase`: Base class with shared fields
- Defines `Book`: Database table model (inherits from `BookBase`)

**Connections**:
```
models.py
├── Book model → used by database.py (metadata.create_all)
├── Book model → used by crud.py (all CRUD operations)
└── BookBase → base for Book table
```

**Key Components**:
- `BookBase`: SQLModel base with fields (title, author, year, price, etc.)
- `Book`: Database table model with `id` as primary key
- `update_timestamp()`: Method to update `updated_at` field

---

### 4. **`app/schemas.py`** - Request/Response Models

**Purpose**: Defines Pydantic schemas for API request/response validation.

**Key Responsibilities**:
- Validates incoming request data
- Shapes outgoing response data
- Provides type safety

**Connections**:
```
schemas.py
├── BookCreate → used in api.py (POST /books/)
├── BookRead → used in api.py (response_model for all endpoints)
├── BookUpdate → used in api.py (PUT /books/{id})
└── All schemas → used in crud.py (function parameters)
```

**Key Components**:
- `BookCreate`: Schema for creating new books (no id, timestamps)
- `BookRead`: Schema for API responses (includes id, timestamps)
- `BookUpdate`: Schema for partial updates (all fields optional)
- `BookSearchResults`: Schema for paginated results (not yet implemented)

---

### 5. **`app/crud.py`** - Business Logic Layer

**Purpose**: Contains all database operations (Create, Read, Update, Delete).

**Key Responsibilities**:
- Implements CRUD operations
- Handles database transactions
- Converts between schemas and models

**Connections**:
```
crud.py
├── imports Book from models.py
├── imports BookCreate, BookUpdate from schemas.py
├── uses Session from database.py (passed as parameter)
└── functions called by api.py
```

**Functions**:
- `create_book()`: Creates new book from `BookCreate` → returns `Book`
- `get_book()`: Retrieves single book by ID → returns `Book` or `None`
- `get_books()`: Retrieves paginated list → returns `List[Book]`
- `update_book()`: Updates book from `BookUpdate` → returns `Book` or `None`
- `delete_book()`: Deletes book by ID → returns `bool`

---

### 6. **`app/api.py`** - API Routes Layer

**Purpose**: Defines HTTP endpoints and request/response handling.

**Key Responsibilities**:
- Defines REST API endpoints
- Handles HTTP requests/responses
- Validates input using schemas
- Calls CRUD functions

**Connections**:
```
api.py
├── imports router functions from crud.py
├── imports schemas from schemas.py
├── uses get_session from database.py (as dependency)
└── router included in main.py
```

**Endpoints**:
- `POST /api/v1/books/` → `create()` → calls `create_book()`
- `GET /api/v1/books/` → `read_all()` → calls `get_books()`
- `GET /api/v1/books/{id}` → `read()` → calls `get_book()`
- `PUT /api/v1/books/{id}` → `update()` → calls `update_book()`
- `DELETE /api/v1/books/{id}` → `delete()` → calls `delete_book()`

---

## Complete Request Flow

### Example: Creating a Book

```
1. Client sends POST /api/v1/books/ with JSON body
   ↓
2. FastAPI (main.py) routes to api.py → create()
   ↓
3. FastAPI validates request body against BookCreate schema (schemas.py)
   ↓
4. FastAPI injects database session via get_session() dependency (database.py)
   ↓
5. create() calls create_book(session, book) from crud.py
   ↓
6. crud.py converts BookCreate → Book model (models.py)
   ↓
7. crud.py saves Book to database using session
   ↓
8. crud.py returns Book model
   ↓
9. FastAPI converts Book → BookRead schema (schemas.py)
   ↓
10. Client receives JSON response with BookRead data
```

### Example: Reading a Book

```
1. Client sends GET /api/v1/books/1
   ↓
2. FastAPI routes to api.py → read(book_id=1)
   ↓
3. FastAPI injects session via get_session() dependency
   ↓
4. read() calls get_book(session, 1) from crud.py
   ↓
5. crud.py queries database using Book model
   ↓
6. Returns Book model or None
   ↓
7. api.py checks if book exists, raises 404 if not
   ↓
8. FastAPI converts Book → BookRead schema
   ↓
9. Client receives JSON response
```

---

## Data Flow Diagram

```
┌─────────────┐
│   Client    │
│  (Browser/  │
│   Postman)  │
└──────┬──────┘
       │ HTTP Request
       ↓
┌─────────────────────────────────────┐
│      main.py (FastAPI App)         │
│  - Initializes FastAPI             │
│  - Includes router at /api/v1      │
│  - Startup: create_db_and_tables()  │
└──────┬──────────────────────────────┘
       │
       ↓
┌─────────────────────────────────────┐
│         api.py (Router)             │
│  - Defines HTTP endpoints           │
│  - Validates with schemas           │
│  - Uses get_session() dependency    │
└──────┬──────────────────────────────┘
       │
       ↓
┌─────────────────────────────────────┐
│         crud.py (Business Logic)   │
│  - create_book()                    │
│  - get_book()                       │
│  - get_books()                      │
│  - update_book()                    │
│  - delete_book()                    │
└──────┬──────────────────────────────┘
       │
       ↓
┌─────────────────────────────────────┐
│      models.py (Database Models)   │
│  - Book (SQLModel table)            │
│  - BookBase (base fields)           │
└──────┬──────────────────────────────┘
       │
       ↓
┌─────────────────────────────────────┐
│      database.py (Database Layer)  │
│  - engine (SQLAlchemy engine)       │
│  - get_session() (dependency)       │
│  - create_db_and_tables()           │
└──────┬──────────────────────────────┘
       │
       ↓
┌─────────────────────────────────────┐
│         Database (SQLite/MySQL)     │
└─────────────────────────────────────┘

┌─────────────────────────────────────┐
│      schemas.py (Validation)        │
│  - BookCreate (request validation)  │
│  - BookRead (response shape)        │
│  - BookUpdate (partial updates)     │
└─────────────────────────────────────┘
       ↑                              │
       │ Used by api.py for           │
       │ request/response validation  │
       └──────────────────────────────┘
```

---

## Architecture Layers

### 1. **Presentation Layer** (`api.py`)
- Handles HTTP requests/responses
- Route definitions
- Input validation
- Error handling

### 2. **Business Logic Layer** (`crud.py`)
- Core business operations
- Data transformation
- Transaction management

### 3. **Data Access Layer** (`models.py` + `database.py`)
- Database models
- Session management
- Database connection

### 4. **Validation Layer** (`schemas.py`)
- Request validation
- Response serialization
- Type safety

### 5. **Application Layer** (`main.py`)
- Application initialization
- Component wiring
- Configuration

---

## Key Design Patterns

1. **Dependency Injection**: FastAPI's `Depends()` injects database sessions
2. **Repository Pattern**: CRUD functions abstract database operations
3. **Schema Pattern**: Separate models for database and API (models vs schemas)
4. **Layered Architecture**: Clear separation of concerns across layers

---

## Technology Stack

- **FastAPI**: Web framework
- **SQLModel**: ORM (combines SQLAlchemy + Pydantic)
- **Pydantic**: Data validation
- **SQLAlchemy**: Database toolkit
- **python-dotenv**: Environment variable management
- **Uvicorn**: ASGI server (for running the app)

---

## Environment Variables

The application uses these environment variables (via `.env` file):
- `DATABASE_URL`: Database connection string (default: `sqlite:///./test.db`)
- `API_TITLE`: API title (default: "BookStore API")
- `API_VERSION`: API version (default: "1.0.0")
- `ROOT_PATH`: Root path for proxy setups (default: "/")


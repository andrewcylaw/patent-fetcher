# Patent Fetcher




### Implementation 

- Python 3.13 using `poetry (>=2.0)`
- Python CLI tool implemented using `click`, `pydantic`
- Unit testing using `pytest`
- Environment variables managed using `pydantic-settings`
- Containerized using `docker`, but also runnable on local machine


The fetcher performs a batch-based query on the given patent api, and dumps either to disk or to a database (SQLite included for reference).
Performs a health check, and if successful, pulls patents from the given date range. The program logic flow is 

```
 cli -> patent client <-> api
              |
              v
         output client
         /     |     \  
       local sqlite3 (...)
 ```

### Design Choices

I think there is ample room for feature enhancements, such as:

- Synchronous requests
  - For a take-home test, I deliberately used `requests` as-is for clarity and simplicity
  - For production or something more network bound, I would use something async like `httpx` and introduce session management
- Exception handling
  - I am intentionally raising generic `HTTPErrors` and `ValueErrors`, but a real system would have custom exception types, tracebacks, and other error handling like retries
- Testing
  - Full unit testing would
- Production
  - Other productionizing tools, such as `flake8`, `mypy`, `black`, `precommit` were omitted for brevity, but normally they would be included 

---

### Future Improvements / Polish
- Caching 
  - In a production system, I would consider adding caching to reduce API hits, network latency, especially on identical requests
  - This could be anything like an in-memory cache or a persistent downstream cache like a database
- Environment variables / configuration
  - The dotenv file (`.env.sample`) is consciously hardcoded into my implementation of Pydantic settings, but better practice would be templating the values and/or environment-specific values
  - Keys/secrets can be grabbed during runtime from a store (eg SecretsManager) or injected during CICD instead of committed
- Load balancing
  - Depending on the workload, a large date range can be chunked across different workers, etc
- Database ORM
  - A SQLite output was provided to demonstrate various outputs 
    - In production an ORM like `SQLAlchemy` or Django's would be used for session/transaction management, etc

---

### Usage

#### Installation
```commandline
poetry install --with test
```

#### Tests
```commandline
pytest
```

### Building & Running

```
docker build . -t patent_fetcher
docker run patent_fetcher 2001-04-25 2001-05-25

-- The Dockerfile contains a different entrypoint which allows for the cli with more options
docker run patent_fetcher check-health
docker run patent_fetcher fetch-patents 2024-01-02 2024-01-03 --page_size 20 --start_page 2 --num_pages 3 --output local
```

#### Command Line

There are two ways of executing a patent fetch:

- `patent_fetcher_cli fetch-patents`
```
Usage: patent_fetcher_cli fetch-patents [OPTIONS]
                                        [%Y-%m-%d|%Y-%m-%dT%H:%M:%S|%Y-%m-%d%H:%M:%S]
                                        [%Y-%m-%d|%Y-%m-%dT%H:%M:%S|%Y-%m-%d%H:%M:%S]
                                       
  Fetches patents from the patent API between START_DATE and END_DATE and outputs them to OUTPUT.
  Optionally, NUM_PAGES can be fetched of PAGE_SIZE each, starting from a specific START_PAGE.                            
                                       
Options:
  --start_page INTEGER     Optional - specifies the page to start fetching from if provided. If omitted, starts from page 1
  --num_pages INTEGER      Optional - specifies the number of pages to fetch. If omitted, fetches all pages
  --page_size INTEGER      Optional - number of items to fetch per page, defaults to 1000
  --output [local|sqlite]  Optional - specifies output location, defaults to none
  --help                   Show this message and exit.
  
Examples:
   patent_fetcher_cli fetch-patents 2024-01-02 2024-01-03
   patent_fetcher_cli fetch-patents 2024-01-02 2024-01-03 --page_size 20 --start_page 2 --num_pages 3 --output local
```

- `patent_fetcher_cli check-health`
```
Usage: patent_fetcher_cli check-health [OPTIONS]

  Performs a health check against the patent API. 
```

- `patent_fetcher DATE DATE`
```
patent_fetcher [OPTIONS]
               [%Y-%m-%d|%Y-%m-%dT%H:%M:%S|%Y-%m-%d%H:%M:%S]
               [%Y-%m-%d|%Y-%m-%dT%H:%M:%S|%Y-%m-%d%H:%M:%S]
               
  Synonymous with `patent_fetcher_cli fetch-patents`. Implemented so that the example from the 
  readme can be executed as-is. Defaults to fetching all patents with a page size of 1000, with no output. 
```

### Environment Variables
```
API_URL - Required, STRING (default none)
  API endpoint for patent fetching
  
API_TOKEN - Required, STRING (defaults to the demo token)
  API authentication token
  
BUFFER_SIZE - Optional, INTEGER (default 10000)
  Number of records to keep on disk before flushing
  
SQLITE_DB - Optional, STRING :memory:
  Specifies where the SQLite database to write out to is
  
MAX_PAGE_SIZE - Required, INTEGER (default 1000)
  Specifies the max number of items per page
```

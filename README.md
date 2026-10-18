# Financial Ledger Microservice

A production-grade, ACID-compliant financial ledger microservice built using Python, Flask, and PostgreSQL.

## Features
- **ACID Compliance**: Ensures strict transactional integrity during transfers.
- **Pessimistic Locking**: Prevents race conditions and double-spending using `SELECT FOR UPDATE`.
- **Double-Entry Bookkeeping**: Accurate database schema tracking debits and credits.
- **Automated Testing**: Unit and integration test suite using `pytest`.

## Tech Stack
- **Backend**: Python, Flask
- **Database**: PostgreSQL (`psycopg2`)
- **Testing**: `pytest`

## Quickstart
1. Clone the repository:
   ```bash
   git clone [https://github.com/banerjeesneha7723/ledger-microservice.git](https://github.com/banerjeesneha7723/ledger-microservice.git)

-- PostgreSQL Double-Entry Bookkeeping Schema

CREATE TABLE IF NOT EXISTS accounts (
    account_id VARCHAR(50) PRIMARY KEY,
    owner_name VARCHAR(100) NOT NULL,
    currency VARCHAR(10) DEFAULT 'USD',
    balance NUMERIC(15, 2) NOT NULL DEFAULT 0.00,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS transactions (
    transaction_id SERIAL PRIMARY KEY,
    transfer_id VARCHAR(64) NOT NULL, -- Groups debit and credit legs together
    account_id VARCHAR(50) REFERENCES accounts(account_id),
    amount NUMERIC(15, 2) NOT NULL, -- Positive for credit, negative for debit
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Index for high-speed ledger lookups
CREATE INDEX IF NOT EXISTS idx_transactions_transfer_id ON transactions(transfer_id);
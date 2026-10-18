import os
import logging
import psycopg2
from psycopg2.extras import RealDictCursor
from flask import Flask, request, jsonify

# Configure professional logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("ledger-microservice")

app = Flask(__name__)

# Environment-driven configuration
DB_HOST = os.getenv("DB_HOST", "127.0.0.1")
DB_NAME = os.getenv("DB_NAME", "ledger_db")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
DB_PORT = os.getenv("DB_PORT", "5432")

def get_db_connection():
    return psycopg2.connect(
        host=DB_HOST,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        port=DB_PORT
    )

@app.route("/health", methods=["GET"])
def health_check():
    return jsonify({"status": "healthy", "service": "ledger-microservice"}), 200

@app.route("/accounts", methods=["POST"])
def create_account():
    data = request.get_json()
    account_id = data.get("account_id")
    owner_name = data.get("owner_name")
    currency = data.get("currency", "USD")
    initial_balance = float(data.get("initial_balance", 0.00))

    if not account_id or not owner_name:
        return jsonify({"error": "account_id and owner_name are required"}), 400

    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO accounts (account_id, owner_name, currency, balance) VALUES (%s, %s, %s, %s);",
                (account_id, owner_name, currency, initial_balance)
            )
        conn.commit()
        logger.info(f"Account created successfully: {account_id} for {owner_name}")
        return jsonify({"message": "Account created successfully", "account_id": account_id}), 201
    except Exception as e:
        conn.rollback()
        logger.error(f"Failed to create account {account_id}: {str(e)}")
        return jsonify({"error": str(e)}), 400
    finally:
        conn.close()

@app.route("/accounts/<account_id>", methods=["GET"])
def get_account(account_id):
    conn = get_db_connection()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("SELECT * FROM accounts WHERE account_id = %s;", (account_id,))
            account = cur.fetchone()
            if not account:
                return jsonify({"error": "Account not found"}), 404
            return jsonify(account), 200
    except Exception as e:
        logger.error(f"Error fetching account {account_id}: {str(e)}")
        return jsonify({"error": str(e)}), 500
    finally:
        conn.close()

@app.route("/transactions", methods=["POST"])
def create_transaction():
    data = request.get_json()
    source_id = data.get("source_account_id")
    dest_id = data.get("destination_account_id")
    amount = float(data.get("amount", 0.00))
    
    if amount <= 0:
        return jsonify({"error": "Amount must be greater than zero"}), 400

    conn = get_db_connection()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            if source_id:
                # Pessimistic locking to prevent race conditions
                cur.execute("SELECT balance FROM accounts WHERE account_id = %s FOR UPDATE;", (source_id,))
                source = cur.fetchone()
                if not source or float(source['balance']) < amount:
                    return jsonify({"error": "Insufficient funds or source account not found"}), 400
                cur.execute("UPDATE accounts SET balance = balance - %s WHERE account_id = %s;", (amount, source_id))
            
            if dest_id:
                cur.execute("SELECT balance FROM accounts WHERE account_id = %s FOR UPDATE;", (dest_id,))
                dest = cur.fetchone()
                if not dest:
                    return jsonify({"error": "Destination account not found"}), 400
                cur.execute("UPDATE accounts SET balance = balance + %s WHERE account_id = %s;", (amount, dest_id))
            
        conn.commit()
        logger.info(f"Transaction successful: Transferred {amount} from {source_id} to {dest_id}")
        return jsonify({"message": "Transaction completed successfully"}), 201
        
    except Exception as e:
        conn.rollback()
        logger.error(f"Transaction failed, rolled back changes: {str(e)}")
        return jsonify({"error": str(e)}), 500
    finally:
        conn.close()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
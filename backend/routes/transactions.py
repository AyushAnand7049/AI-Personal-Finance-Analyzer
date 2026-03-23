from fastapi import APIRouter, HTTPException, UploadFile, File
from models.schemas import TransactionCreate, TransactionResponse, CSVUploadResponse
from services.categorizer import categorize_transaction, batch_categorize
from database import get_db
import csv
import io
from typing import List

router = APIRouter()

@router.post("/", response_model=dict)
def add_transaction(tx: TransactionCreate):
    """Add a single transaction"""
    category = tx.category
    confidence = 1.0
    predicted_category = None
    
    if not category:
        predicted_category, confidence = categorize_transaction(tx.description)
        category = predicted_category
    
    with get_db() as conn:
        cursor = conn.execute(
            """INSERT INTO transactions (date, description, amount, category, predicted_category, confidence)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (tx.date, tx.description, tx.amount, category, predicted_category, confidence)
        )
        tx_id = cursor.lastrowid
    
    return {
        "id": tx_id,
        "message": "Transaction added successfully",
        "category": category,
        "confidence": confidence
    }

@router.get("/", response_model=List[dict])
def get_transactions(limit: int = 50, offset: int = 0):
    """Get all transactions with pagination"""
    with get_db() as conn:
        rows = conn.execute(
            "SELECT * FROM transactions ORDER BY date DESC LIMIT ? OFFSET ?",
            (limit, offset)
        ).fetchall()
    return [dict(r) for r in rows]

@router.delete("/{tx_id}")
def delete_transaction(tx_id: int):
    """Delete a transaction"""
    with get_db() as conn:
        result = conn.execute("DELETE FROM transactions WHERE id = ?", (tx_id,))
        if result.rowcount == 0:
            raise HTTPException(status_code=404, detail="Transaction not found")
    return {"message": "Transaction deleted"}

@router.post("/upload-csv", response_model=CSVUploadResponse)
async def upload_csv(file: UploadFile = File(...)):
    """Upload transactions from CSV file"""
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only CSV files allowed")
    
    content = await file.read()
    text = content.decode("utf-8-sig")  # handle BOM
    
    reader = csv.DictReader(io.StringIO(text))
    
    imported = 0
    failed = 0
    transactions = []
    
    for row in reader:
        try:
            # Flexible column name matching
            date = row.get("date") or row.get("Date") or row.get("DATE")
            description = row.get("description") or row.get("Description") or row.get("DESC") or row.get("narration") or row.get("Narration")
            amount_raw = row.get("amount") or row.get("Amount") or row.get("AMOUNT") or row.get("debit") or row.get("Debit")
            
            if not date or not description or not amount_raw:
                failed += 1
                continue
            
            amount = abs(float(str(amount_raw).replace(",", "").replace("₹", "").strip()))
            category, confidence = categorize_transaction(description)
            
            with get_db() as conn:
                cursor = conn.execute(
                    """INSERT INTO transactions (date, description, amount, category, predicted_category, confidence)
                       VALUES (?, ?, ?, ?, ?, ?)""",
                    (date, description, amount, category, category, confidence)
                )
                tx_id = cursor.lastrowid
            
            transactions.append({
                "id": tx_id,
                "date": date,
                "description": description,
                "amount": amount,
                "category": category,
                "confidence": confidence
            })
            imported += 1
            
        except Exception as e:
            failed += 1
            continue
    
    return {
        "imported": imported,
        "failed": failed,
        "transactions": transactions[:10]  # return first 10 as preview
    }

@router.get("/categories")
def get_categories():
    """Get all available categories"""
    with get_db() as conn:
        rows = conn.execute("SELECT * FROM categories").fetchall()
    return [dict(r) for r in rows]

@router.put("/{tx_id}/category")
def update_category(tx_id: int, category: str):
    """Manually update a transaction's category"""
    with get_db() as conn:
        result = conn.execute(
            "UPDATE transactions SET category = ? WHERE id = ?",
            (category, tx_id)
        )
        if result.rowcount == 0:
            raise HTTPException(status_code=404, detail="Transaction not found")
    return {"message": "Category updated", "category": category}

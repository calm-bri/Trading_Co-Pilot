from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from typing import List
import pandas as pd
from io import StringIO
from app.core.database import get_db
from app.core.security import get_current_user
from app.models import User, Trade
from app.schemas.trade import Trade as TradeSchema, TradeCreate
import structlog

router = APIRouter()

@router.post("/", response_model=TradeSchema)
async def create_trade(
    trade: TradeCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new trade for the current user."""
    logger = structlog.get_logger()
    logger.info("Creating new trade", user_id=current_user.id, symbol=trade.symbol, trade_type=trade.trade_type)

    db_trade = Trade(
        user_id=current_user.id,
        symbol=trade.symbol.upper(),
        trade_type=trade.trade_type.lower(),
        quantity=trade.quantity,
        price=trade.price,
        notes=trade.notes
    )
    db.add(db_trade)
    db.commit()
    db.refresh(db_trade)
    return db_trade

@router.get("/", response_model=List[TradeSchema])
async def get_trades(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all trades for the current user."""
    trades = db.query(Trade).filter(Trade.user_id == current_user.id).offset(skip).limit(limit).all()
    return trades

@router.get("/{trade_id}", response_model=TradeSchema)
async def get_trade(
    trade_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific trade by ID."""
    trade = db.query(Trade).filter(Trade.id == trade_id, Trade.user_id == current_user.id).first()
    if not trade:
        raise HTTPException(status_code=404, detail="Trade not found")
    return trade

@router.put("/{trade_id}", response_model=TradeSchema)
async def update_trade(
    trade_id: int,
    trade_update: TradeCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update a trade."""
    trade = db.query(Trade).filter(Trade.id == trade_id, Trade.user_id == current_user.id).first()
    if not trade:
        raise HTTPException(status_code=404, detail="Trade not found")

    for field, value in trade_update.dict().items():
        setattr(trade, field, value)

    db.commit()
    db.refresh(trade)
    return trade

@router.delete("/{trade_id}")
async def delete_trade(
    trade_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a trade."""
    trade = db.query(Trade).filter(Trade.id == trade_id, Trade.user_id == current_user.id).first()
    if not trade:
        raise HTTPException(status_code=404, detail="Trade not found")

    db.delete(trade)
    db.commit()
    return {"message": "Trade deleted successfully"}

@router.post("/upload-csv")
async def upload_csv(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Upload a CSV file and bulk insert trades for the current user."""
    logger = structlog.get_logger()
    logger.info("CSV upload initiated", user_id=current_user.id, filename=file.filename)

    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="File must be a CSV")

    try:
        contents = await file.read()
        csv_data = StringIO(contents.decode('utf-8'))
        df = pd.read_csv(csv_data)

        # Validate required columns
        required_columns = ['symbol', 'trade_type', 'quantity', 'price']
        if not all(col in df.columns for col in required_columns):
            raise HTTPException(status_code=400, detail=f"CSV must contain columns: {', '.join(required_columns)}")

        # Validate and prepare trades
        trades_to_insert = []
        for index, row in df.iterrows():
            try:
                trade = Trade(
                    user_id=current_user.id,
                    symbol=str(row['symbol']).upper(),
                    trade_type=str(row['trade_type']).lower(),
                    quantity=float(row['quantity']),
                    price=float(row['price']),
                    notes=str(row.get('notes', '')) if pd.notna(row.get('notes')) else None
                )
                # Basic validation
                if trade.trade_type not in ['buy', 'sell']:
                    raise ValueError(f"Invalid trade_type at row {index+1}: {trade.trade_type}")
                if trade.quantity <= 0 or trade.price <= 0:
                    raise ValueError(f"Invalid quantity or price at row {index+1}")
                trades_to_insert.append(trade)
            except (ValueError, TypeError) as e:
                raise HTTPException(status_code=400, detail=f"Error at row {index+1}: {str(e)}")

        # Bulk insert using transaction
        db.add_all(trades_to_insert)
        db.commit()

        logger.info("CSV upload successful", user_id=current_user.id, trades_inserted=len(trades_to_insert))
        return {"message": f"Successfully uploaded {len(trades_to_insert)} trades"}

    except pd.errors.EmptyDataError:
        raise HTTPException(status_code=400, detail="CSV file is empty")
    except UnicodeDecodeError:
        raise HTTPException(status_code=400, detail="Invalid file encoding. Use UTF-8.")
    except Exception as e:
        db.rollback()
        logger.error("CSV upload failed", user_id=current_user.id, error=str(e))
        raise HTTPException(status_code=500, detail=f"Error processing CSV: {str(e)}")

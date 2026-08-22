from typing import Optional
from decimal import Decimal
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
import anthropic

from app.config import get_settings
from app.models.ai_usage import AIUsageLog

EXTRACTION_MODEL = "claude-haiku-4-5"

# $ per 1M tokens
PRICING = {
    "claude-haiku-4-5": {"input": Decimal("1.00"), "output": Decimal("5.00")},
}


class ExtractedSalesData(BaseModel):
    customer_name: Optional[str] = Field(None, description="Customer/company name")
    product_name: Optional[str] = Field(None, description="Product or license sold")
    vendor_name: Optional[str] = Field(None, description="Vendor/manufacturer of the product")
    amount: Optional[float] = Field(None, description="Sale amount, numeric only")
    sale_date: Optional[str] = Field(None, description="Sale date in YYYY-MM-DD format")
    contract_expiry_date: Optional[str] = Field(None, description="Contract/renewal expiry date in YYYY-MM-DD format")
    notes: Optional[str] = Field(None, description="Any other relevant details that don't fit other fields")


class AIExtractionError(Exception):
    pass


def _calc_cost(model: str, input_tokens: int, output_tokens: int) -> Decimal:
    pricing = PRICING.get(model)
    if not pricing:
        return Decimal("0")
    return (
        (Decimal(input_tokens) / Decimal(1_000_000)) * pricing["input"]
        + (Decimal(output_tokens) / Decimal(1_000_000)) * pricing["output"]
    )


def extract_sales_data(text: str, db: Session, task_id: Optional[int] = None) -> dict:
    """
    Use Claude to extract structured sales data from unstructured free text
    (emails, notes, pasted document content, etc). Every call is logged to
    ai_usage_logs with token counts and computed cost for real-time tracking.
    """
    settings = get_settings()
    if not settings.anthropic_api_key:
        raise AIExtractionError("ANTHROPIC_API_KEY is not configured")

    client = anthropic.Anthropic(api_key=settings.anthropic_api_key)

    usage_log = AIUsageLog(
        task_id=task_id,
        feature="data_extraction",
        model=EXTRACTION_MODEL,
    )

    try:
        response = client.messages.parse(
            model=EXTRACTION_MODEL,
            max_tokens=1024,
            system=(
                "You extract structured sales data from unstructured text "
                "(emails, notes, invoices, free text). Only extract what is "
                "explicitly present; leave fields null if not mentioned. "
                "Normalize dates to YYYY-MM-DD."
            ),
            messages=[{"role": "user", "content": text}],
            output_format=ExtractedSalesData,
        )

        usage_log.input_tokens = response.usage.input_tokens
        usage_log.output_tokens = response.usage.output_tokens
        usage_log.cost_usd = _calc_cost(
            EXTRACTION_MODEL, response.usage.input_tokens, response.usage.output_tokens
        )
        usage_log.success = True
        db.add(usage_log)
        db.commit()

        return {
            "extracted": response.parsed_output.model_dump(),
            "usage": {
                "input_tokens": usage_log.input_tokens,
                "output_tokens": usage_log.output_tokens,
                "cost_usd": float(usage_log.cost_usd),
            },
        }

    except anthropic.APIStatusError as e:
        usage_log.success = False
        usage_log.error_message = str(e)[:500]
        db.add(usage_log)
        db.commit()
        raise AIExtractionError(f"Claude API error: {e}")
    except Exception as e:
        usage_log.success = False
        usage_log.error_message = str(e)[:500]
        db.add(usage_log)
        db.commit()
        raise AIExtractionError(str(e))


def get_usage_stats(db: Session) -> dict:
    """Real-time AI usage cost stats: today, this month, all-time."""
    from sqlalchemy import func
    from datetime import datetime, timezone

    now = datetime.utcnow()
    today_start = datetime(now.year, now.month, now.day)
    month_start = datetime(now.year, now.month, 1)

    def _sum_since(since: Optional[datetime]) -> dict:
        query = db.query(
            func.coalesce(func.sum(AIUsageLog.cost_usd), 0),
            func.count(AIUsageLog.id),
            func.coalesce(func.sum(AIUsageLog.input_tokens), 0),
            func.coalesce(func.sum(AIUsageLog.output_tokens), 0),
        ).filter(AIUsageLog.success == True)  # noqa: E712
        if since:
            query = query.filter(AIUsageLog.created_at >= since)
        cost, count, input_tokens, output_tokens = query.first()
        return {
            "cost_usd": float(cost),
            "requests": count,
            "input_tokens": int(input_tokens),
            "output_tokens": int(output_tokens),
        }

    return {
        "today": _sum_since(today_start),
        "this_month": _sum_since(month_start),
        "all_time": _sum_since(None),
    }

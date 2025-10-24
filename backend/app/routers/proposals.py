"""
Options Proposals Router - Create and execute options trade proposals
"""

import logging
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from app.core.jwt import get_current_user
from app.services.order_execution import OptionsProposal, get_order_execution_service


logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/proposals", tags=["proposals"])


class CreateProposalRequest(BaseModel):
    """Request to create an options trade proposal"""

    symbol: str
    option_symbol: str
    quantity: int
    order_type: str = "limit"


class ExecuteProposalRequest(BaseModel):
    """Request to execute an approved proposal"""

    proposal: OptionsProposal
    limit_price: Optional[float] = None


@router.post("/create", dependencies=[Depends(get_current_user)])
async def create_proposal(request: CreateProposalRequest):
    """
    Create a detailed options trade proposal with risk analysis

    **Workflow:**
    1. Fetches option data from Tradier (live market data)
    2. Calculates Greeks (delta, gamma, theta, vega)
    3. Computes risk metrics (max loss, max profit, breakeven)
    4. Returns proposal for user review

    **Example:**
    ```json
    {
      "symbol": "SPY",
      "option_symbol": "SPY250117C00590000",
      "quantity": 1,
      "order_type": "limit"
    }
    ```

    **Response:**
    ```json
    {
      "symbol": "SPY",
      "option_symbol": "SPY250117C00590000",
      "contract_type": "call",
      "strike": 590.0,
      "expiration": "2025-01-17",
      "premium": 12.50,
      "quantity": 1,
      "underlying_price": 580.25,
      "greeks": {
        "delta": 0.65,
        "gamma": 0.02,
        "theta": -0.15,
        "vega": 0.25
      },
      "max_risk": 1250.00,
      "max_profit": 999999,
      "breakeven": 602.50,
      "probability_of_profit": 65.0,
      "risk_reward_ratio": 799.99,
      "margin_requirement": 1250.00
    }
    ```
    """
    try:
        service = get_order_execution_service()
        proposal = await service.create_proposal(
            symbol=request.symbol,
            option_symbol=request.option_symbol,
            quantity=request.quantity,
            order_type=request.order_type,
        )

        return {
            "success": True,
            "proposal": proposal.dict(),
            "message": f"Proposal created for {request.quantity} contract(s) of {request.option_symbol}",
        }

    except ValueError as e:
        logger.warning(f"Invalid proposal request: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to create proposal: {e}")
        raise HTTPException(status_code=500, detail="Failed to create proposal")


@router.post("/execute", dependencies=[Depends(get_current_user)])
async def execute_proposal(request: ExecuteProposalRequest):
    """
    Execute an approved options trade proposal

    **Workflow:**
    1. Validates the proposal
    2. Submits order to Alpaca (paper trading)
    3. Returns order confirmation

    **⚠️ Paper Trading Mode:**
    - All executions use Alpaca Paper Trading API
    - NO real money is at risk
    - Orders are simulated with live market conditions

    **Example:**
    ```json
    {
      "proposal": { ... full proposal object from /create ... },
      "limit_price": 12.75
    }
    ```

    **Response:**
    ```json
    {
      "success": true,
      "order_id": "abc123-def456",
      "status": "accepted",
      "filled_qty": 0,
      "filled_avg_price": null,
      "submitted_at": "2025-01-15T14:30:00Z",
      "proposal": { ... }
    }
    ```
    """
    try:
        service = get_order_execution_service()
        result = await service.execute_proposal(
            proposal=request.proposal,
            limit_price=request.limit_price,
        )

        if not result.get("success"):
            raise HTTPException(
                status_code=400,
                detail=result.get("error", "Order execution failed"),
            )

        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to execute proposal: {e}")
        raise HTTPException(status_code=500, detail="Failed to execute order")


@router.get("/history", dependencies=[Depends(get_current_user)])
async def get_proposal_history():
    """
    Get history of created proposals

    **Future Enhancement:**
    - Store proposals in database
    - Track acceptance/rejection rates
    - Analyze which proposals were most profitable

    **Current Status:** Not yet implemented
    """
    return {
        "success": True,
        "proposals": [],
        "message": "Proposal history coming soon - currently in-memory only",
    }

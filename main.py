from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from typing import Optional
import uuid
import os
from scenarios.receipt_simple import ReceiptSimpleScenario
from scenarios.receipt_advanced import ReceiptAdvancedScenario
from scenarios.loan import LoanScenario
from scenarios.claim_marketplace_buyer import ClaimMarketplaceBuyerScenario
from scenarios.claim_universal import ClaimUniversalScenario
from scenarios.complaint_rospotrebnadzor import ComplaintRospotrebnadzorScenario
from scenarios.complaint_prosecutor import ComplaintProsecutorScenario
from scenarios.claim_bank_block import ClaimBankBlockScenario

app = FastAPI()

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def serve_index():
    return FileResponse("index.html")


sessions = {}

SCENARIO_CLASSES = {
    "receipt_simple": ReceiptSimpleScenario,
    "receipt_advanced": ReceiptAdvancedScenario,
    "loan": LoanScenario,
    "claim_marketplace_buyer": ClaimMarketplaceBuyerScenario,
    "claim_universal": ClaimUniversalScenario,
    "complaint_rospotrebnadzor": ComplaintRospotrebnadzorScenario,
    "complaint_prosecutor": ComplaintProsecutorScenario,
    "claim_bank_block": ClaimBankBlockScenario,
}

TEMPLATE_MAP = {
    "receipt_simple": "templates/receipt_simple.txt",
    "receipt_advanced": "templates/receipt_advanced.txt",
    "loan": "templates/loan.txt",
    "claim_marketplace_buyer": "templates/claim_marketplace_buyer.txt",
    "claim_universal": "templates/claim_universal.txt",
    "complaint_rospotrebnadzor": "templates/complaint_rospotrebnadzor.txt",
    "complaint_prosecutor": "templates/complaint_prosecutor.txt",
    "claim_bank_block": "templates/claim_bank_block.txt",
}


def _make_key(session_id: str, scenario_type: str) -> str:
    return f"{session_id}:{scenario_type}"


def get_or_create_scenario(session_id: str = None, scenario_type: str = "receipt_simple"):
    if session_id is None or session_id == "":
        session_id = str(uuid.uuid4())
    
    key = _make_key(session_id, scenario_type)
    
    if key not in sessions:
        scenario_class = SCENARIO_CLASSES.get(scenario_type, ReceiptSimpleScenario)
        sessions[key] = scenario_class()
    
    return sessions[key], session_id


def is_error_response(text: str) -> bool:
    if not text:
        return False
    error_prefixes = ("не может быть", "Пожалуйста, введите", "Ошибка")
    return text.startswith(error_prefixes)


@app.post("/api/scenario/{scenario_type}")
async def handle_scenario(scenario_type: str, request: Request):
    data = await request.json()
    session_id = data.get("session_id")
    answer = data.get("answer", "")
    
    template_path = TEMPLATE_MAP.get(scenario_type, "templates/receipt_simple.txt")
    
    scenario, session_id = get_or_create_scenario(session_id, scenario_type)
    
    # Логика: если answer пустой — начать сценарий, иначе — продолжить
    if not answer:
        if scenario.get_current_step() == "start":
            scenario.process_answer("")
        question = scenario.get_next_question()
        return JSONResponse({
            "is_complete": False,
            "question": question,
            "session_id": session_id,
            "current_step": scenario.get_current_step()
        })
    else:
        result = scenario.process_answer(answer)
        
        if result and is_error_response(result):
            return JSONResponse({
                "question": result,
                "session_id": session_id,
                "current_step": scenario.get_current_step()
            })
        
        if result:
            return JSONResponse({
                "question": result,
                "session_id": session_id,
                "current_step": scenario.get_current_step()
            })
        
        if scenario.is_complete():
            document = scenario.generate_document(template_path)
            return JSONResponse({
                "is_complete": True,
                "document": document,
                "session_id": session_id,
                "current_step": "done"
            })
        
        next_question = scenario.get_next_question()
        return JSONResponse({
            "question": next_question,
            "session_id": session_id,
            "current_step": scenario.get_current_step()
        })


@app.post("/api/session/{session_id}/reset")
def reset_session(session_id: str):
    keys_to_delete = [key for key in sessions if key.startswith(f"{session_id}:")]
    for key in keys_to_delete:
        del sessions[key]
    return {"status": "ok", "session_id": session_id, "deleted": len(keys_to_delete)}


@app.get("/api/session/{session_id}/status")
def session_status(session_id: str):
    result = {"session_id": session_id, "scenarios": {}}
    for key, scenario in sessions.items():
        if key.startswith(f"{session_id}:"):
            scenario_type = key.split(":")[1]
            result["scenarios"][scenario_type] = {
                "current_step": scenario.get_current_step(),
                "is_complete": scenario.is_complete(),
                "data": scenario.data
            }
    if not result["scenarios"]:
        return {"status": "not_found", "session_id": session_id}
    return result


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import uvicorn
import json
import sys
import os

# Dynamically add the root directory to path so we can import from mcp_connector
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from mcp_connector.connector import (
    book_advance_car,
    get_advance_bookings,
    update_booking_status,
    get_dealership_full,
    get_cars,
    get_car,
    compare_cars,
    list_variants,
    book_test_drive,
    book_service,
    book_rental
)

app = FastAPI()

TOOLS = [
    {
        "name": "list_cars",
        "description": "List the dealership's cars (GET /api/cars). Each record has the car's name, family, body_type, price range, and highlights. Pass 'body_type' (e.g., SUV, Sedan), 'family', or a free-text 'q' query to narrow the list down. Use the 'slug' from this list with get_car or compare_cars.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "q": {"type": "string"},
                "body_type": {"type": "string"},
                "family": {"type": "string"},
                "limit": {"type": "integer"}
            }
        }
    },
    {
        "name": "get_car",
        "description": "Fetch one car's full profile by its slug (GET /api/cars/{model_id}). Adds specifications, features, colours, gallery, variants and FAQs on top of the fields returned by list_cars. Call this tool first to read the real variants and colors rather than guessing before booking.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "model_id": {"type": "string"}
            },
            "required": ["model_id"]
        }
    },
    {
        "name": "compare_cars",
        "description": "Compare between two and four cars attribute by attribute (GET /api/compare). Pass a comma-separated list of car slugs (e.g., 'taigun-sport,virtus-chrome'). Returns a matrix of comparisons ready to drop into a table.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "ids": {"type": "string"}
            },
            "required": ["ids"]
        }
    },
    {
        "name": "list_variants",
        "description": "Every variant across the whole range, with its own price (GET /api/variants). Filter by 'model_id', 'trim' (e.g., GT Line), or 'transmission' (e.g., DSG, MT). Use this to find a specific variant to book.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "model_id": {"type": "string"},
                "trim": {"type": "string"},
                "transmission": {"type": "string"},
                "limit": {"type": "integer"}
            }
        }
    },
    {
        "name": "get_dealership",
        "description": "Returns the full dealership profile and all outlets in a single response (GET /api/dealership-full). Use this to find the correct 'dealership_id' before making an advance booking, or to answer questions about operating hours and locations.",
        "inputSchema": {
            "type": "object",
            "properties": {}
        }
    },
    {
        "name": "book_test_drive",
        "description": "Book a test drive for a customer (POST /api/leads/test-drive) and return the new lead reference. The API validates the request. 'model' must be a valid car name. Always ask the user for their contact details, preferred date, and preferred time before calling.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "first_name": {"type": "string"},
                "last_name": {"type": "string"},
                "email": {"type": "string"},
                "mobile": {"type": "string"},
                "model": {"type": "string"},
                "preferred_date": {"type": "string"},
                "preferred_time": {"type": "string"}
            },
            "required": ["first_name", "last_name", "email", "mobile", "model", "preferred_date", "preferred_time"]
        }
    },
    {
        "name": "book_advance_car",
        "description": "Request an advance booking for a new car (POST /api/leads/advance-booking). Call get_car and get_dealership first to read the real variants, colors, and dealership IDs rather than guessing. This writes data - confirm the details with the patient/customer before calling it.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "first_name": {"type": "string"},
                "last_name": {"type": "string"},
                "email": {"type": "string"},
                "mobile": {"type": "string"},
                "model": {"type": "string"},
                "dealership_id": {"type": "string"},
                "variant": {"type": "string"},
                "color": {"type": "string"}
            },
            "required": ["first_name", "last_name", "email", "mobile", "model", "dealership_id"]
        }
    },
    {
        "name": "book_service",
        "description": "Book a workshop service slot for any Volkswagen (POST /api/leads/service). You must collect the customer's registration number, preferred date, and service type before calling this endpoint.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "first_name": {"type": "string"},
                "last_name": {"type": "string"},
                "email": {"type": "string"},
                "mobile": {"type": "string"},
                "model": {"type": "string"},
                "registration_number": {"type": "string"},
                "service_type": {"type": "string"},
                "preferred_date": {"type": "string"}
            },
            "required": ["first_name", "last_name", "email", "mobile", "model", "registration_number", "service_type", "preferred_date"]
        }
    },
    {
        "name": "book_rental",
        "description": "Request a car rental for specific dates (POST /api/leads/rent). Validates if the car is already booked. You must collect start_date and end_date from the user.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "first_name": {"type": "string"},
                "last_name": {"type": "string"},
                "email": {"type": "string"},
                "mobile": {"type": "string"},
                "model": {"type": "string"},
                "start_date": {"type": "string"},
                "end_date": {"type": "string"}
            },
            "required": ["first_name", "last_name", "email", "mobile", "model", "start_date", "end_date"]
        }
    }
]

@app.post("/mcp")
async def mcp_handler(request: Request):
    try:
        req = await request.json()
    except:
        return JSONResponse({"jsonrpc": "2.0", "error": {"code": -32700, "message": "Parse error"}})
        
    method = req.get("method")
    req_id = req.get("id")
    
    if method == "initialize":
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {
                "protocolVersion": req.get("params", {}).get("protocolVersion", "2024-11-05"),
                "capabilities": {},
                "serverInfo": {"name": "volkswagen-elite-proxy", "version": "1.0.0"}
            }
        }
        
    if method == "tools/list":
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {
                "tools": TOOLS
            }
        }
        
    if method == "tools/call":
        params = req.get("params", {})
        tool_name = params.get("name")
        args = params.get("arguments", {})
        
        try:
            if tool_name == "list_cars":
                res = await get_cars(**args)
            elif tool_name == "get_car":
                res = await get_car(**args)
            elif tool_name == "compare_cars":
                res = await compare_cars(**args)
            elif tool_name == "list_variants":
                res = await list_variants(**args)
            elif tool_name == "get_dealership":
                res = await get_dealership_full()
            elif tool_name == "book_test_drive":
                res = await book_test_drive(**args)
            elif tool_name == "book_advance_car":
                res = await book_advance_car(**args)
            elif tool_name == "book_service":
                res = await book_service(**args)
            elif tool_name == "book_rental":
                res = await book_rental(**args)
            else:
                return {"jsonrpc": "2.0", "id": req_id, "error": {"code": -32601, "message": "Method not found"}}
                
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {
                    "content": [{"type": "text", "text": json.dumps(res)}]
                }
            }
        except Exception as e:
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {
                    "isError": True,
                    "content": [{"type": "text", "text": str(e)}]
                }
            }

    return {"jsonrpc": "2.0", "id": req_id, "error": {"code": -32601, "message": "Method not found"}}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)

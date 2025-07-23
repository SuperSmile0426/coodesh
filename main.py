import asyncio
import json
from typing import Dict, Any, Optional
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from enum import Enum

app = FastAPI(
    title="API Integration Proxy",
    description="A FastAPI endpoint that acts as a mocked proxy to external APIs",
    version="1.0.0"
)

class Provider(str, Enum):
    SALESFORCE = "salesforce"
    UPS = "ups"

class AuthType(str, Enum):
    PASSWORD = "password"
    API_KEY = "api_key"
    OAUTH = "oauth"

class IntegrationRequest(BaseModel):
    action: str
    parameters: Dict[str, Any]
    auth_type: Optional[AuthType] = AuthType.API_KEY
    auth_credentials: Optional[Dict[str, str]] = None

class IntegrationResponse(BaseModel):
    status: str
    data: Dict[str, Any]
    provider: str
    action: str

# Mocked API handlers
class SalesforceHandler:
    """Mocked Salesforce REST API handler"""
    
    @staticmethod
    async def handle_request(action: str, parameters: Dict[str, Any], auth_credentials: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        # Simulate API call delay
        await asyncio.sleep(0.5)
        
        # Mock different Salesforce actions
        if action == "create_lead":
            return {
                "id": "00Q1234567890ABC",
                "email": parameters.get("email", "test@example.com"),
                "company": parameters.get("company", "Test Company"),
                "status": "New",
                "created_date": "2024-01-15T10:30:00Z"
            }
        elif action == "update_contact":
            return {
                "id": parameters.get("contact_id", "0031234567890ABC"),
                "email": parameters.get("email", "updated@example.com"),
                "phone": parameters.get("phone", "+1234567890"),
                "last_modified": "2024-01-15T10:30:00Z"
            }
        elif action == "get_account":
            return {
                "id": parameters.get("account_id", "0011234567890ABC"),
                "name": "Acme Corporation",
                "industry": "Technology",
                "annual_revenue": 1000000,
                "employees": 500
            }
        else:
            return {
                "error": f"Unknown Salesforce action: {action}",
                "available_actions": ["create_lead", "update_contact", "get_account"]
            }

class UPSHandler:
    """Mocked UPS SOAP/XML API handler"""
    
    @staticmethod
    async def handle_request(action: str, parameters: Dict[str, Any], auth_credentials: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        # Simulate API call delay
        await asyncio.sleep(0.8)
        
        # Mock different UPS actions
        if action == "track_package":
            return {
                "tracking_number": parameters.get("tracking_number", "1Z999AA1234567890"),
                "status": "In Transit",
                "location": "Memphis, TN",
                "estimated_delivery": "2024-01-18T14:00:00Z",
                "shipment_details": {
                    "weight": "2.5 lbs",
                    "service": "Ground",
                    "origin": "New York, NY",
                    "destination": "Los Angeles, CA"
                }
            }
        elif action == "calculate_shipping":
            return {
                "origin_zip": parameters.get("origin_zip", "10001"),
                "destination_zip": parameters.get("destination_zip", "90210"),
                "weight": parameters.get("weight", "5.0"),
                "service": parameters.get("service", "Ground"),
                "rate": 15.99,
                "delivery_days": 5
            }
        elif action == "create_shipment":
            return {
                "shipment_id": "UPS123456789",
                "tracking_number": "1Z999AA1234567890",
                "label_url": "https://api.ups.com/labels/123456789.pdf",
                "rate": 25.50,
                "estimated_delivery": "2024-01-18T14:00:00Z"
            }
        else:
            return {
                "error": f"Unknown UPS action: {action}",
                "available_actions": ["track_package", "calculate_shipping", "create_shipment"]
            }

# Provider registry
PROVIDER_HANDLERS = {
    Provider.SALESFORCE: SalesforceHandler,
    Provider.UPS: UPSHandler
}

@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "API Integration Proxy",
        "version": "1.0.0",
        "available_providers": [provider.value for provider in Provider],
        "endpoint": "/integrate/{provider}",
        "method": "POST"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "api-integration-proxy"}

@app.post("/integrate/{provider}", response_model=IntegrationResponse)
async def integrate_provider(provider: Provider, request: IntegrationRequest):
    """
    Main integration endpoint that routes requests to different mocked API providers.
    
    Args:
        provider: The API provider (salesforce or ups)
        request: The integration request containing action, parameters, and auth info
    
    Returns:
        IntegrationResponse: Normalized response with status and data
    """
    try:
        # Validate provider
        if provider not in PROVIDER_HANDLERS:
            raise HTTPException(
                status_code=400, 
                detail=f"Unsupported provider: {provider}. Supported providers: {list(PROVIDER_HANDLERS.keys())}"
            )
        
        # Get handler for the provider
        handler_class = PROVIDER_HANDLERS[provider]
        
        # Validate auth credentials if provided
        if request.auth_credentials:
            if not _validate_auth_credentials(request.auth_type, request.auth_credentials):
                raise HTTPException(
                    status_code=401,
                    detail="Invalid authentication credentials"
                )
        
        # Handle the request
        handler = handler_class()
        result = await handler.handle_request(
            action=request.action,
            parameters=request.parameters,
            auth_credentials=request.auth_credentials
        )
        
        # Check if the result contains an error
        if "error" in result:
            return IntegrationResponse(
                status="error",
                data=result,
                provider=provider.value,
                action=request.action
            )
        
        return IntegrationResponse(
            status="success",
            data=result,
            provider=provider.value,
            action=request.action
        )
        
    except Exception as e:
        # Handle unexpected errors gracefully
        return IntegrationResponse(
            status="error",
            data={
                "error": "Internal server error",
                "message": str(e),
                "provider": provider.value,
                "action": request.action
            },
            provider=provider.value,
            action=request.action
        )

def _validate_auth_credentials(auth_type: AuthType, credentials: Dict[str, str]) -> bool:
    """
    Mock authentication validation.
    In a real implementation, this would validate against the actual provider's auth system.
    """
    if auth_type == AuthType.PASSWORD:
        return credentials.get("username") and credentials.get("password")
    elif auth_type == AuthType.API_KEY:
        return credentials.get("api_key") is not None
    elif auth_type == AuthType.OAUTH:
        return credentials.get("access_token") is not None
    return False

@app.get("/providers/{provider}/actions")
async def get_provider_actions(provider: Provider):
    """Get available actions for a specific provider"""
    if provider == Provider.SALESFORCE:
        return {
            "provider": provider.value,
            "actions": [
                {
                    "name": "create_lead",
                    "description": "Create a new lead in Salesforce",
                    "required_parameters": ["email", "company"]
                },
                {
                    "name": "update_contact",
                    "description": "Update an existing contact",
                    "required_parameters": ["contact_id", "email"]
                },
                {
                    "name": "get_account",
                    "description": "Retrieve account information",
                    "required_parameters": ["account_id"]
                }
            ]
        }
    elif provider == Provider.UPS:
        return {
            "provider": provider.value,
            "actions": [
                {
                    "name": "track_package",
                    "description": "Track a package by tracking number",
                    "required_parameters": ["tracking_number"]
                },
                {
                    "name": "calculate_shipping",
                    "description": "Calculate shipping rates",
                    "required_parameters": ["origin_zip", "destination_zip", "weight"]
                },
                {
                    "name": "create_shipment",
                    "description": "Create a new shipment",
                    "required_parameters": ["origin_address", "destination_address", "weight"]
                }
            ]
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001) 
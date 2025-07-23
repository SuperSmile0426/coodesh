# API Integration Proxy

A FastAPI endpoint that acts as a mocked proxy to external APIs, supporting multiple providers with different authentication schemes.

This is a challenge by Coodesh

## Description

This project implements a FastAPI-based integration proxy that simulates interactions with external APIs (Salesforce and UPS) without making actual API calls. It provides a unified interface for workflow automation platforms to interact with third-party systems through mocked responses.

## Technologies Used

- **Python 3.8+**
- **FastAPI** - Modern web framework for building APIs
- **Pydantic** - Data validation using Python type annotations
- **Uvicorn** - ASGI server for running FastAPI applications
- **Pytest** - Testing framework with async support
- **HTTPX** - HTTP client for testing

## Features

- **Multi-Provider Support**: Currently supports Salesforce (REST) and UPS (SOAP/XML-style)
- **Extensible Architecture**: Easy to add new providers and actions
- **Multiple Authentication Schemes**: Password, API Key, and OAuth support
- **Normalized Responses**: Consistent JSON response format across all providers
- **Error Handling**: Graceful handling of unexpected formats and errors
- **Unit Testing**: Comprehensive test coverage for handlers and endpoints
- **API Documentation**: Auto-generated OpenAPI documentation

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd coodesh
```

2. Create a virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Running the Application

Start the FastAPI server:
```bash
python main.py
```

Or using uvicorn directly:
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`

### API Documentation

Once the server is running, you can access:
- **Interactive API docs**: http://localhost:8000/docs
- **Alternative API docs**: http://localhost:8000/redoc

### Example Requests

#### Salesforce Integration

Create a new lead:
```bash
curl -X POST "http://localhost:8000/integrate/salesforce" \
  -H "Content-Type: application/json" \
  -d '{
    "action": "create_lead",
    "parameters": {
      "email": "john.doe@example.com",
      "company": "Acme Corp"
    },
    "auth_type": "api_key",
    "auth_credentials": {
      "api_key": "your_salesforce_api_key"
    }
  }'
```

Update a contact:
```bash
curl -X POST "http://localhost:8000/integrate/salesforce" \
  -H "Content-Type: application/json" \
  -d '{
    "action": "update_contact",
    "parameters": {
      "contact_id": "0031234567890ABC",
      "email": "updated@example.com",
      "phone": "+1234567890"
    },
    "auth_type": "password",
    "auth_credentials": {
      "username": "your_username",
      "password": "your_password"
    }
  }'
```

#### UPS Integration

Track a package:
```bash
curl -X POST "http://localhost:8000/integrate/ups" \
  -H "Content-Type: application/json" \
  -d '{
    "action": "track_package",
    "parameters": {
      "tracking_number": "1Z999AA1234567890"
    },
    "auth_type": "api_key",
    "auth_credentials": {
      "api_key": "your_ups_api_key"
    }
  }'
```

Calculate shipping rates:
```bash
curl -X POST "http://localhost:8000/integrate/ups" \
  -H "Content-Type: application/json" \
  -d '{
    "action": "calculate_shipping",
    "parameters": {
      "origin_zip": "10001",
      "destination_zip": "90210",
      "weight": "5.0",
      "service": "Ground"
    },
    "auth_type": "oauth",
    "auth_credentials": {
      "access_token": "your_oauth_token"
    }
  }'
```

### Available Endpoints

- `GET /` - API information and available providers
- `GET /health` - Health check endpoint
- `POST /integrate/{provider}` - Main integration endpoint
- `GET /providers/{provider}/actions` - Get available actions for a provider

### Supported Providers and Actions

#### Salesforce
- `create_lead` - Create a new lead
- `update_contact` - Update an existing contact
- `get_account` - Retrieve account information

#### UPS
- `track_package` - Track a package by tracking number
- `calculate_shipping` - Calculate shipping rates
- `create_shipment` - Create a new shipment

### Authentication Types

- **Password**: Username and password combination
- **API Key**: Simple API key authentication
- **OAuth**: Access token-based authentication

## Testing

Run the test suite:
```bash
pytest test_main.py -v
```

Run tests with coverage:
```bash
pytest test_main.py --cov=main --cov-report=html
```

## Project Structure

```
coodesh/
├── main.py              # Main FastAPI application
├── test_main.py         # Unit tests
├── requirements.txt     # Python dependencies
├── README.md           # Project documentation
└── .gitignore          # Git ignore file
```

## Response Format

All responses follow a normalized JSON format:

```json
{
  "status": "success|error",
  "data": {
    // Provider-specific response data
  },
  "provider": "salesforce|ups",
  "action": "action_name"
}
```

## Error Handling

The API handles various error scenarios:
- Invalid provider names
- Unknown actions
- Invalid authentication credentials
- Malformed request payloads
- Internal server errors

## Extensibility

To add a new provider:

1. Create a new handler class (e.g., `NewProviderHandler`)
2. Implement the `handle_request` static method
3. Add the provider to the `Provider` enum
4. Register the handler in `PROVIDER_HANDLERS`
5. Add provider actions to the `/providers/{provider}/actions` endpoint

## Development

### Adding New Providers

Example of adding a new provider:

```python
class NewProviderHandler:
    @staticmethod
    async def handle_request(action: str, parameters: Dict[str, Any], auth_credentials: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        await asyncio.sleep(0.3)  # Simulate API delay
        
        if action == "custom_action":
            return {
                "result": "success",
                "data": parameters
            }
        else:
            return {
                "error": f"Unknown action: {action}",
                "available_actions": ["custom_action"]
            }

# Add to enum and registry
PROVIDER_HANDLERS[Provider.NEW_PROVIDER] = NewProviderHandler
```

## License

This project is part of a Coodesh challenge.

## Support

For questions about the implementation or this challenge, please refer to the platform documentation or contact the support team.

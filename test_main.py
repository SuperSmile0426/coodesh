import pytest
import asyncio
from fastapi.testclient import TestClient
from main import app, SalesforceHandler, UPSHandler, Provider, AuthType

client = TestClient(app)

class TestSalesforceHandler:
    """Test cases for Salesforce handler"""
    
    @pytest.mark.asyncio
    async def test_create_lead(self):
        """Test creating a lead in Salesforce"""
        result = await SalesforceHandler.handle_request(
            action="create_lead",
            parameters={"email": "test@example.com", "company": "Test Corp"}
        )
        
        assert result["email"] == "test@example.com"
        assert result["company"] == "Test Corp"
        assert result["status"] == "New"
        assert "id" in result
        assert "created_date" in result
    
    @pytest.mark.asyncio
    async def test_update_contact(self):
        """Test updating a contact in Salesforce"""
        result = await SalesforceHandler.handle_request(
            action="update_contact",
            parameters={
                "contact_id": "0031234567890ABC",
                "email": "updated@example.com",
                "phone": "+1234567890"
            }
        )
        
        assert result["id"] == "0031234567890ABC"
        assert result["email"] == "updated@example.com"
        assert result["phone"] == "+1234567890"
        assert "last_modified" in result
    
    @pytest.mark.asyncio
    async def test_unknown_action(self):
        """Test handling of unknown action"""
        result = await SalesforceHandler.handle_request(
            action="unknown_action",
            parameters={}
        )
        
        assert "error" in result
        assert "available_actions" in result

class TestUPSHandler:
    """Test cases for UPS handler"""
    
    @pytest.mark.asyncio
    async def test_track_package(self):
        """Test tracking a package with UPS"""
        result = await UPSHandler.handle_request(
            action="track_package",
            parameters={"tracking_number": "1Z999AA1234567890"}
        )
        
        assert result["tracking_number"] == "1Z999AA1234567890"
        assert result["status"] == "In Transit"
        assert "location" in result
        assert "estimated_delivery" in result
        assert "shipment_details" in result
    
    @pytest.mark.asyncio
    async def test_calculate_shipping(self):
        """Test calculating shipping rates with UPS"""
        result = await UPSHandler.handle_request(
            action="calculate_shipping",
            parameters={
                "origin_zip": "10001",
                "destination_zip": "90210",
                "weight": "5.0",
                "service": "Ground"
            }
        )
        
        assert result["origin_zip"] == "10001"
        assert result["destination_zip"] == "90210"
        assert result["weight"] == "5.0"
        assert result["service"] == "Ground"
        assert "rate" in result
        assert "delivery_days" in result

class TestAPIEndpoints:
    """Test cases for API endpoints"""
    
    def test_root_endpoint(self):
        """Test the root endpoint"""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "API Integration Proxy"
        assert "salesforce" in data["available_providers"]
        assert "ups" in data["available_providers"]
    
    def test_health_check(self):
        """Test the health check endpoint"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
    
    def test_salesforce_integration_success(self):
        """Test successful Salesforce integration"""
        payload = {
            "action": "create_lead",
            "parameters": {
                "email": "test@example.com",
                "company": "Test Company"
            },
            "auth_type": "api_key",
            "auth_credentials": {
                "api_key": "test_api_key"
            }
        }
        
        response = client.post("/integrate/salesforce", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert data["provider"] == "salesforce"
        assert data["action"] == "create_lead"
        assert "data" in data
    
    def test_ups_integration_success(self):
        """Test successful UPS integration"""
        payload = {
            "action": "track_package",
            "parameters": {
                "tracking_number": "1Z999AA1234567890"
            },
            "auth_type": "api_key",
            "auth_credentials": {
                "api_key": "test_api_key"
            }
        }
        
        response = client.post("/integrate/ups", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert data["provider"] == "ups"
        assert data["action"] == "track_package"
        assert "data" in data
    
    def test_invalid_provider(self):
        """Test integration with invalid provider"""
        payload = {
            "action": "test_action",
            "parameters": {}
        }
        
        response = client.post("/integrate/invalid_provider", json=payload)
        assert response.status_code == 422  # Validation error
    
    def test_invalid_auth_credentials(self):
        """Test integration with invalid auth credentials"""
        payload = {
            "action": "create_lead",
            "parameters": {"email": "test@example.com"},
            "auth_type": "password",
            "auth_credentials": {
                "username": "test_user"
                # Missing password
            }
        }
        
        response = client.post("/integrate/salesforce", json=payload)
        assert response.status_code == 401
    
    def test_provider_actions_salesforce(self):
        """Test getting Salesforce provider actions"""
        response = client.get("/providers/salesforce/actions")
        assert response.status_code == 200
        data = response.json()
        assert data["provider"] == "salesforce"
        assert len(data["actions"]) == 3
        assert any(action["name"] == "create_lead" for action in data["actions"])
    
    def test_provider_actions_ups(self):
        """Test getting UPS provider actions"""
        response = client.get("/providers/ups/actions")
        assert response.status_code == 200
        data = response.json()
        assert data["provider"] == "ups"
        assert len(data["actions"]) == 3
        assert any(action["name"] == "track_package" for action in data["actions"])

if __name__ == "__main__":
    pytest.main([__file__]) 
import pytest

def test_health_check(client):
    """Test the health check endpoint returns 200."""
    response = client.get('/health')
    assert response.status_code == 200
    assert response.json['status'] == 'healthy'

def test_login_page_loads(client):
    """Test login page is accessible."""
    response = client.get('/login')
    assert response.status_code == 200
    assert b'Login' in response.data

def test_register_page_loads(client):
    """Test registration page is accessible."""
    response = client.get('/register')
    assert response.status_code == 200
    assert b'Sign Up' in response.data

def test_unauthenticated_redirect(client):
    """Test that unauthorized users are redirected to login."""
    response = client.get('/dashboard')
    assert response.status_code == 302
    assert '/login' in response.headers['Location']

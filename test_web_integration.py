"""
Round 47: Web Integration & API System
Agents can access web resources, make API calls, and integrate with external services.
Features: web scraping, API clients, endpoint management, request validation, response handling.
"""

import pytest
from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Callable


class RequestMethod(Enum):
    """HTTP request methods"""
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"
    PATCH = "PATCH"


class ResponseStatus(Enum):
    """Status of API response"""
    SUCCESS = "success"  # 2xx
    REDIRECT = "redirect"  # 3xx
    CLIENT_ERROR = "client_error"  # 4xx
    SERVER_ERROR = "server_error"  # 5xx
    TIMEOUT = "timeout"
    NETWORK_ERROR = "network_error"


@dataclass
class APIEndpoint:
    """Definition of an API endpoint"""
    endpoint_id: str
    name: str
    url: str
    method: RequestMethod
    description: str
    required_params: List[str] = field(default_factory=list)
    optional_params: List[str] = field(default_factory=list)
    authentication_type: str = "none"  # "none", "api_key", "oauth", "jwt"
    rate_limit: int = 60  # requests per minute
    timeout: float = 5.0
    enabled: bool = True

    def to_dict(self) -> Dict:
        return {
            "id": self.endpoint_id,
            "name": self.name,
            "url": self.url,
            "method": self.method.value,
            "auth": self.authentication_type,
            "rate_limit": self.rate_limit
        }


@dataclass
class APIRequest:
    """Request to API endpoint"""
    request_id: str
    endpoint_id: str
    agent_id: str
    parameters: Dict[str, Any] = field(default_factory=dict)
    headers: Dict[str, str] = field(default_factory=dict)
    body: Optional[str] = None
    timestamp: float = 0.0
    timeout: float = 5.0

    def to_dict(self) -> Dict:
        return {
            "id": self.request_id,
            "endpoint": self.endpoint_id,
            "agent": self.agent_id,
            "params": len(self.parameters),
            "timeout": self.timeout
        }


@dataclass
class APIResponse:
    """Response from API call"""
    response_id: str
    request_id: str
    status: ResponseStatus
    status_code: int = 0
    data: Dict[str, Any] = field(default_factory=dict)
    error_message: str = ""
    latency_ms: float = 0.0
    timestamp: float = 0.0
    cached: bool = False

    def to_dict(self) -> Dict:
        return {
            "id": self.response_id,
            "request": self.request_id,
            "status": self.status.value,
            "code": self.status_code,
            "latency": self.latency_ms,
            "cached": self.cached
        }


@dataclass
class WebResource:
    """Resource scraped from web"""
    resource_id: str
    url: str
    title: str
    content: str
    content_type: str  # "text", "html", "json", "markdown"
    scraped_at: float = 0.0
    expiry_at: float = 0.0
    source_quality: float = 0.5  # 0.0-1.0

    def is_expired(self, current_time: float = 0.0) -> bool:
        """Check if resource has expired"""
        if self.expiry_at == 0.0:
            return False
        return current_time >= self.expiry_at

    def to_dict(self) -> Dict:
        return {
            "id": self.resource_id,
            "url": self.url,
            "title": self.title,
            "type": self.content_type,
            "quality": self.source_quality
        }


class APIEndpointManager:
    """Manages available API endpoints"""

    def __init__(self):
        self.endpoints: Dict[str, APIEndpoint] = {}
        self.endpoint_usage: Dict[str, int] = {}  # endpoint_id -> usage count

    def register_endpoint(self, endpoint: APIEndpoint) -> bool:
        """Register new API endpoint"""
        if endpoint.endpoint_id in self.endpoints:
            return False

        self.endpoints[endpoint.endpoint_id] = endpoint
        self.endpoint_usage[endpoint.endpoint_id] = 0
        return True

    def get_endpoint(self, endpoint_id: str) -> Optional[APIEndpoint]:
        """Get endpoint by ID"""
        return self.endpoints.get(endpoint_id)

    def list_endpoints(self) -> List[APIEndpoint]:
        """Get all endpoints"""
        return list(self.endpoints.values())

    def list_enabled_endpoints(self) -> List[APIEndpoint]:
        """Get only enabled endpoints"""
        return [e for e in self.endpoints.values() if e.enabled]

    def enable_endpoint(self, endpoint_id: str) -> bool:
        """Enable endpoint"""
        if endpoint_id not in self.endpoints:
            return False
        self.endpoints[endpoint_id].enabled = True
        return True

    def disable_endpoint(self, endpoint_id: str) -> bool:
        """Disable endpoint"""
        if endpoint_id not in self.endpoints:
            return False
        self.endpoints[endpoint_id].enabled = False
        return True

    def record_usage(self, endpoint_id: str) -> bool:
        """Record endpoint usage"""
        if endpoint_id not in self.endpoints:
            return False
        self.endpoint_usage[endpoint_id] += 1
        return True

    def get_most_used_endpoints(self, limit: int = 10) -> List[APIEndpoint]:
        """Get most frequently used endpoints"""
        sorted_endpoints = sorted(
            self.endpoints.items(),
            key=lambda x: self.endpoint_usage.get(x[0], 0),
            reverse=True
        )
        return [e for _, e in sorted_endpoints[:limit]]

    def to_dict(self) -> Dict:
        return {
            "total_endpoints": len(self.endpoints),
            "enabled": len(self.list_enabled_endpoints()),
            "total_usage": sum(self.endpoint_usage.values())
        }


class APIRequestValidator:
    """Validates API requests before sending"""

    def validate_request(self, request: APIRequest, endpoint: APIEndpoint) -> bool:
        """Validate request against endpoint spec"""
        # Check required parameters
        for param in endpoint.required_params:
            if param not in request.parameters:
                return False

        # Check no extra parameters
        for param in request.parameters.keys():
            if param not in endpoint.required_params and param not in endpoint.optional_params:
                return False

        # Check timeout is reasonable (0.5-60 seconds)
        if not (0.5 <= request.timeout <= 60.0):
            return False

        return True

    def validate_response(self, response: APIResponse) -> bool:
        """Validate response is well-formed"""
        if response.status_code < 0:
            return False

        if response.latency_ms < 0:
            return False

        return True


class WebCrawler:
    """Crawls and caches web resources"""

    def __init__(self):
        self.resources: Dict[str, WebResource] = {}
        self.url_cache: Dict[str, str] = {}  # url -> resource_id

    def scrape_resource(self, url: str, content: str, content_type: str = "html") -> WebResource:
        """Scrape web resource (simulated)"""
        resource_id = f"res_{len(self.resources)}"

        # Extract title from content (simplified)
        title = "Web Resource" if len(content) < 50 else content[:50]

        resource = WebResource(
            resource_id=resource_id,
            url=url,
            title=title,
            content=content,
            content_type=content_type,
            source_quality=0.8 if len(content) > 100 else 0.5
        )

        self.resources[resource_id] = resource
        self.url_cache[url] = resource_id

        return resource

    def get_resource(self, url: str) -> Optional[WebResource]:
        """Get cached resource by URL"""
        if url not in self.url_cache:
            return None

        resource_id = self.url_cache[url]
        return self.resources.get(resource_id)

    def clear_expired_resources(self, current_time: float = 0.0) -> int:
        """Remove expired resources"""
        expired_ids = [
            rid for rid, r in self.resources.items()
            if r.is_expired(current_time)
        ]

        for rid in expired_ids:
            resource = self.resources.pop(rid)
            self.url_cache.pop(resource.url, None)

        return len(expired_ids)

    def get_cache_stats(self) -> Dict:
        """Get cache statistics"""
        return {
            "cached_resources": len(self.resources),
            "total_urls_visited": len(self.url_cache)
        }

    def to_dict(self) -> Dict:
        return {
            "resources": len(self.resources),
            "urls_cached": len(self.url_cache)
        }


class RateLimiter:
    """Enforces rate limits on API endpoints"""

    def __init__(self):
        self.request_history: Dict[str, List[float]] = {}  # endpoint_id -> timestamps

    def is_rate_limited(self, endpoint_id: str, endpoint: APIEndpoint, current_time: float = 0.0) -> bool:
        """Check if endpoint is rate limited"""
        if endpoint_id not in self.request_history:
            return False

        # Get requests in last minute
        minute_ago = current_time - 60.0
        recent_requests = [
            t for t in self.request_history[endpoint_id]
            if t >= minute_ago
        ]

        return len(recent_requests) >= endpoint.rate_limit

    def record_request(self, endpoint_id: str, timestamp: float = 0.0) -> bool:
        """Record API request"""
        if endpoint_id not in self.request_history:
            self.request_history[endpoint_id] = []

        self.request_history[endpoint_id].append(timestamp)

        # Clean old requests (older than 2 minutes)
        two_minutes_ago = timestamp - 120.0
        self.request_history[endpoint_id] = [
            t for t in self.request_history[endpoint_id]
            if t >= two_minutes_ago
        ]

        return True

    def get_remaining_requests(self, endpoint_id: str, endpoint: APIEndpoint, current_time: float = 0.0) -> int:
        """Get remaining requests before rate limit"""
        if endpoint_id not in self.request_history:
            return endpoint.rate_limit

        minute_ago = current_time - 60.0
        recent = len([
            t for t in self.request_history[endpoint_id]
            if t >= minute_ago
        ])

        return max(0, endpoint.rate_limit - recent)

    def to_dict(self) -> Dict:
        return {
            "tracked_endpoints": len(self.request_history),
            "total_requests_recorded": sum(len(v) for v in self.request_history.values())
        }


class WebIntegrationManager:
    """Central manager for web integration"""

    def __init__(self):
        self.endpoint_manager = APIEndpointManager()
        self.request_validator = APIRequestValidator()
        self.web_crawler = WebCrawler()
        self.rate_limiter = RateLimiter()
        self.request_log: Dict[str, APIRequest] = {}
        self.response_log: Dict[str, APIResponse] = {}

    def register_endpoint(self, endpoint: APIEndpoint) -> bool:
        """Register API endpoint"""
        return self.endpoint_manager.register_endpoint(endpoint)

    def make_request(self, request: APIRequest) -> APIResponse:
        """Make API request with validation"""
        endpoint = self.endpoint_manager.get_endpoint(request.endpoint_id)
        if not endpoint:
            return APIResponse(
                response_id=f"res_{len(self.response_log)}",
                request_id=request.request_id,
                status=ResponseStatus.CLIENT_ERROR,
                status_code=404,
                error_message="Endpoint not found"
            )

        # Check if enabled
        if not endpoint.enabled:
            return APIResponse(
                response_id=f"res_{len(self.response_log)}",
                request_id=request.request_id,
                status=ResponseStatus.CLIENT_ERROR,
                status_code=403,
                error_message="Endpoint disabled"
            )

        # Validate request
        if not self.request_validator.validate_request(request, endpoint):
            return APIResponse(
                response_id=f"res_{len(self.response_log)}",
                request_id=request.request_id,
                status=ResponseStatus.CLIENT_ERROR,
                status_code=400,
                error_message="Invalid request parameters"
            )

        # Check rate limit
        if self.rate_limiter.is_rate_limited(request.endpoint_id, endpoint, request.timestamp):
            return APIResponse(
                response_id=f"res_{len(self.response_log)}",
                request_id=request.request_id,
                status=ResponseStatus.CLIENT_ERROR,
                status_code=429,
                error_message="Rate limit exceeded"
            )

        # Record request
        self.request_log[request.request_id] = request
        self.endpoint_manager.record_usage(request.endpoint_id)
        self.rate_limiter.record_request(request.endpoint_id, request.timestamp)

        # Create success response (simulated)
        response = APIResponse(
            response_id=f"res_{len(self.response_log)}",
            request_id=request.request_id,
            status=ResponseStatus.SUCCESS,
            status_code=200,
            data={"result": "success", "endpoint": endpoint.name},
            latency_ms=50.0
        )

        self.response_log[response.response_id] = response
        return response

    def scrape_web(self, url: str, content: str, content_type: str = "html") -> WebResource:
        """Scrape web resource"""
        return self.web_crawler.scrape_resource(url, content, content_type)

    def get_cached_resource(self, url: str) -> Optional[WebResource]:
        """Get cached web resource"""
        return self.web_crawler.get_resource(url)

    def get_system_stats(self) -> Dict:
        """Get system statistics"""
        return {
            "endpoints": self.endpoint_manager.to_dict(),
            "web_cache": self.web_crawler.to_dict(),
            "rate_limiter": self.rate_limiter.to_dict(),
            "total_requests": len(self.request_log),
            "total_responses": len(self.response_log)
        }

    def to_dict(self) -> Dict:
        return {
            "endpoints": len(self.endpoint_manager.endpoints),
            "cached_resources": len(self.web_crawler.resources),
            "requests_made": len(self.request_log)
        }


# ===== Tests =====

def test_api_endpoint_creation():
    """Test creating API endpoint"""
    endpoint = APIEndpoint(
        "ep1", "Weather API", "https://api.weather.com/current",
        RequestMethod.GET, "Get current weather"
    )
    assert endpoint.endpoint_id == "ep1"
    assert endpoint.method == RequestMethod.GET


def test_api_endpoint_manager_register():
    """Test registering endpoint"""
    manager = APIEndpointManager()
    endpoint = APIEndpoint(
        "ep1", "API", "https://example.com",
        RequestMethod.GET, "Test API"
    )
    assert manager.register_endpoint(endpoint) is True
    assert manager.get_endpoint("ep1") is not None


def test_api_endpoint_duplicate_rejection():
    """Test manager rejects duplicate endpoints"""
    manager = APIEndpointManager()
    endpoint = APIEndpoint(
        "ep1", "API", "https://example.com",
        RequestMethod.GET, "Test"
    )
    assert manager.register_endpoint(endpoint) is True
    assert manager.register_endpoint(endpoint) is False


def test_api_endpoint_enable_disable():
    """Test enabling/disabling endpoints"""
    manager = APIEndpointManager()
    endpoint = APIEndpoint(
        "ep1", "API", "https://example.com",
        RequestMethod.GET, "Test", enabled=True
    )
    manager.register_endpoint(endpoint)

    assert manager.disable_endpoint("ep1") is True
    assert not manager.get_endpoint("ep1").enabled


def test_api_request_creation():
    """Test creating API request"""
    request = APIRequest(
        "req1", "ep1", "agent1",
        parameters={"city": "Boston"},
        timeout=5.0
    )
    assert request.request_id == "req1"
    assert request.parameters["city"] == "Boston"


def test_request_validator_valid():
    """Test validating valid request"""
    validator = APIRequestValidator()
    endpoint = APIEndpoint(
        "ep1", "API", "https://api.com",
        RequestMethod.GET, "Test",
        required_params=["city"],
        optional_params=["country"]
    )

    request = APIRequest(
        "req1", "ep1", "agent1",
        parameters={"city": "Boston"}
    )

    assert validator.validate_request(request, endpoint) is True


def test_request_validator_missing_required():
    """Test validator rejects missing required params"""
    validator = APIRequestValidator()
    endpoint = APIEndpoint(
        "ep1", "API", "https://api.com",
        RequestMethod.GET, "Test",
        required_params=["city"]
    )

    request = APIRequest(
        "req1", "ep1", "agent1",
        parameters={}  # Missing required param
    )

    assert validator.validate_request(request, endpoint) is False


def test_api_response_creation():
    """Test creating API response"""
    response = APIResponse(
        "res1", "req1", ResponseStatus.SUCCESS,
        status_code=200, data={"result": "ok"}
    )
    assert response.response_id == "res1"
    assert response.status == ResponseStatus.SUCCESS


def test_web_crawler_scrape():
    """Test web crawler"""
    crawler = WebCrawler()
    resource = crawler.scrape_resource(
        "https://example.com",
        "This is example content",
        "html"
    )
    assert resource.url == "https://example.com"
    assert len(resource.content) > 0


def test_web_crawler_cache():
    """Test resource caching"""
    crawler = WebCrawler()
    resource = crawler.scrape_resource(
        "https://example.com",
        "Content here",
        "html"
    )

    cached = crawler.get_resource("https://example.com")
    assert cached is not None
    assert cached.resource_id == resource.resource_id


def test_rate_limiter_allows_requests():
    """Test rate limiter allows requests under limit"""
    limiter = RateLimiter()
    endpoint = APIEndpoint(
        "ep1", "API", "https://api.com",
        RequestMethod.GET, "Test", rate_limit=60
    )

    # Record 30 requests
    for i in range(30):
        limiter.record_request("ep1", float(i))

    # Should not be rate limited
    assert not limiter.is_rate_limited("ep1", endpoint, 30.0)


def test_rate_limiter_blocks_excess():
    """Test rate limiter blocks excess requests"""
    limiter = RateLimiter()
    endpoint = APIEndpoint(
        "ep1", "API", "https://api.com",
        RequestMethod.GET, "Test", rate_limit=10
    )

    # Record 10 requests in current minute
    for i in range(10):
        limiter.record_request("ep1", float(i))

    # Should be rate limited
    assert limiter.is_rate_limited("ep1", endpoint, 30.0)


def test_rate_limiter_remaining():
    """Test getting remaining requests"""
    limiter = RateLimiter()
    endpoint = APIEndpoint(
        "ep1", "API", "https://api.com",
        RequestMethod.GET, "Test", rate_limit=60
    )

    for i in range(20):
        limiter.record_request("ep1", float(i))

    remaining = limiter.get_remaining_requests("ep1", endpoint, 30.0)
    assert remaining == 40  # 60 - 20


def test_web_integration_manager_endpoint():
    """Test web integration manager"""
    manager = WebIntegrationManager()
    endpoint = APIEndpoint(
        "ep1", "API", "https://api.com",
        RequestMethod.GET, "Test"
    )
    assert manager.register_endpoint(endpoint) is True


def test_web_integration_make_request():
    """Test making API request"""
    manager = WebIntegrationManager()
    endpoint = APIEndpoint(
        "ep1", "API", "https://api.com",
        RequestMethod.GET, "Test",
        required_params=["query"],
        optional_params=["limit"]
    )
    manager.register_endpoint(endpoint)

    request = APIRequest(
        "req1", "ep1", "agent1",
        parameters={"query": "test"}
    )

    response = manager.make_request(request)
    assert response.status == ResponseStatus.SUCCESS
    assert response.status_code == 200


def test_web_integration_disabled_endpoint():
    """Test request to disabled endpoint"""
    manager = WebIntegrationManager()
    endpoint = APIEndpoint(
        "ep1", "API", "https://api.com",
        RequestMethod.GET, "Test", enabled=False
    )
    manager.register_endpoint(endpoint)

    request = APIRequest(
        "req1", "ep1", "agent1",
        parameters={}
    )

    response = manager.make_request(request)
    assert response.status == ResponseStatus.CLIENT_ERROR
    assert response.status_code == 403


def test_web_integration_scraping():
    """Test web scraping"""
    manager = WebIntegrationManager()
    resource = manager.scrape_web(
        "https://example.com",
        "Example content",
        "html"
    )
    assert resource is not None


def test_complete_web_workflow():
    """Test complete web integration workflow"""
    manager = WebIntegrationManager()

    # Register endpoint
    endpoint = APIEndpoint(
        "search", "Search API", "https://api.example.com/search",
        RequestMethod.GET, "Search for content",
        required_params=["q"],
        optional_params=["limit", "offset"]
    )
    assert manager.register_endpoint(endpoint) is True

    # Make request
    request = APIRequest(
        "req1", "search", "agent1",
        parameters={"q": "python", "limit": "10"}
    )

    response = manager.make_request(request)
    assert response.status == ResponseStatus.SUCCESS
    assert response.status_code == 200

    # Scrape web
    resource = manager.scrape_web(
        "https://example.com/article",
        "This is an article about Python programming",
        "markdown"
    )
    assert resource is not None

    # Get cache stats
    cached = manager.get_cached_resource("https://example.com/article")
    assert cached is not None

    # Check system stats
    stats = manager.get_system_stats()
    assert stats["total_requests"] >= 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

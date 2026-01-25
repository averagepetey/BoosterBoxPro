"""
Admin IP Allowlist Middleware

Restricts /admin/* endpoints to specific IP addresses for extra security.
Even if someone steals admin credentials, they can't access admin endpoints
from unauthorized locations.

Configuration:
  ADMIN_ALLOWED_IPS=192.168.1.1,10.0.0.1  # Comma-separated IPs
  ADMIN_IP_ALLOWLIST_ENABLED=true         # Enable/disable (default: true in prod)

Features:
  - Supports multiple IPs (comma-separated)
  - Supports CIDR notation (e.g., 192.168.1.0/24)
  - Automatically allows localhost in development
  - Logs blocked attempts for security monitoring
"""

import os
import logging
from ipaddress import ip_address, ip_network
from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from typing import List, Set

logger = logging.getLogger(__name__)


class AdminIPAllowlistMiddleware(BaseHTTPMiddleware):
    """
    Middleware to restrict admin endpoints to allowed IP addresses.
    """
    
    def __init__(self, app):
        super().__init__(app)
        self.enabled = self._is_enabled()
        self.allowed_ips = self._load_allowed_ips()
        self.allowed_networks = self._load_allowed_networks()
        
        if self.enabled:
            logger.info(f"Admin IP allowlist enabled. Allowed IPs: {self.allowed_ips}")
            logger.info(f"Allowed networks: {[str(n) for n in self.allowed_networks]}")
        else:
            logger.warning("Admin IP allowlist is DISABLED. All IPs can access admin endpoints.")
    
    def _is_enabled(self) -> bool:
        """Check if IP allowlist is enabled."""
        # Disabled by default in development for convenience
        env = os.getenv("ENVIRONMENT", "development")
        enabled_env = os.getenv("ADMIN_IP_ALLOWLIST_ENABLED", "").lower()
        
        if enabled_env == "true":
            return True
        elif enabled_env == "false":
            return False
        else:
            # Default: enabled in production, disabled in development
            return env == "production"
    
    def _load_allowed_ips(self) -> Set[str]:
        """Load allowed IPs from environment variable."""
        allowed_ips_str = os.getenv("ADMIN_ALLOWED_IPS", "")
        
        # Always allow localhost variants for development
        localhost_ips = {"127.0.0.1", "::1", "localhost"}
        
        if not allowed_ips_str:
            logger.warning("ADMIN_ALLOWED_IPS not set. Only localhost will be allowed for admin.")
            return localhost_ips
        
        # Parse comma-separated IPs (skip CIDR notation, handled separately)
        custom_ips = set()
        for ip_str in allowed_ips_str.split(","):
            ip_str = ip_str.strip()
            if ip_str and "/" not in ip_str:  # Skip CIDR notation
                custom_ips.add(ip_str)
        
        return localhost_ips | custom_ips
    
    def _load_allowed_networks(self) -> List:
        """Load allowed CIDR networks from environment variable."""
        allowed_ips_str = os.getenv("ADMIN_ALLOWED_IPS", "")
        networks = []
        
        for ip_str in allowed_ips_str.split(","):
            ip_str = ip_str.strip()
            if ip_str and "/" in ip_str:  # CIDR notation
                try:
                    networks.append(ip_network(ip_str, strict=False))
                except ValueError as e:
                    logger.error(f"Invalid CIDR network in ADMIN_ALLOWED_IPS: {ip_str} - {e}")
        
        return networks
    
    def _get_client_ip(self, request: Request) -> str:
        """
        Get the real client IP, considering proxies.
        
        Priority:
        1. X-Forwarded-For header (first IP if multiple)
        2. X-Real-IP header
        3. Direct client IP
        """
        # Check X-Forwarded-For (common with proxies/load balancers)
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            # Take the first IP (original client)
            return forwarded_for.split(",")[0].strip()
        
        # Check X-Real-IP (nginx)
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip.strip()
        
        # Fall back to direct connection IP
        if request.client:
            return request.client.host
        
        return "unknown"
    
    def _is_ip_allowed(self, client_ip: str) -> bool:
        """Check if the IP is in the allowlist."""
        # Direct IP match
        if client_ip in self.allowed_ips:
            return True
        
        # Check CIDR networks
        try:
            client_ip_obj = ip_address(client_ip)
            for network in self.allowed_networks:
                if client_ip_obj in network:
                    return True
        except ValueError:
            # Invalid IP address format
            logger.warning(f"Invalid client IP format: {client_ip}")
            return False
        
        return False
    
    async def dispatch(self, request: Request, call_next):
        """Process request and check IP for admin endpoints."""
        # Only check /admin/* routes
        if not request.url.path.startswith("/admin"):
            return await call_next(request)
        
        # Skip check if disabled
        if not self.enabled:
            return await call_next(request)
        
        # Get client IP
        client_ip = self._get_client_ip(request)
        
        # Check if allowed
        if self._is_ip_allowed(client_ip):
            logger.debug(f"Admin access granted for IP: {client_ip} to {request.url.path}")
            return await call_next(request)
        
        # Block and log
        logger.warning(
            f"BLOCKED admin access attempt from unauthorized IP: {client_ip} "
            f"to {request.url.path} - User-Agent: {request.headers.get('User-Agent', 'unknown')}"
        )
        
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied. Your IP is not authorized for admin access."
        )

Admin IP Allowlist Middleware

Restricts /admin/* endpoints to specific IP addresses for extra security.
Even if someone steals admin credentials, they can't access admin endpoints
from unauthorized locations.

Configuration:
  ADMIN_ALLOWED_IPS=192.168.1.1,10.0.0.1  # Comma-separated IPs
  ADMIN_IP_ALLOWLIST_ENABLED=true         # Enable/disable (default: true in prod)

Features:
  - Supports multiple IPs (comma-separated)
  - Supports CIDR notation (e.g., 192.168.1.0/24)
  - Automatically allows localhost in development
  - Logs blocked attempts for security monitoring
"""

import os
import logging
from ipaddress import ip_address, ip_network
from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from typing import List, Set

logger = logging.getLogger(__name__)


class AdminIPAllowlistMiddleware(BaseHTTPMiddleware):
    """
    Middleware to restrict admin endpoints to allowed IP addresses.
    """
    
    def __init__(self, app):
        super().__init__(app)
        self.enabled = self._is_enabled()
        self.allowed_ips = self._load_allowed_ips()
        self.allowed_networks = self._load_allowed_networks()
        
        if self.enabled:
            logger.info(f"Admin IP allowlist enabled. Allowed IPs: {self.allowed_ips}")
            logger.info(f"Allowed networks: {[str(n) for n in self.allowed_networks]}")
        else:
            logger.warning("Admin IP allowlist is DISABLED. All IPs can access admin endpoints.")
    
    def _is_enabled(self) -> bool:
        """Check if IP allowlist is enabled."""
        # Disabled by default in development for convenience
        env = os.getenv("ENVIRONMENT", "development")
        enabled_env = os.getenv("ADMIN_IP_ALLOWLIST_ENABLED", "").lower()
        
        if enabled_env == "true":
            return True
        elif enabled_env == "false":
            return False
        else:
            # Default: enabled in production, disabled in development
            return env == "production"
    
    def _load_allowed_ips(self) -> Set[str]:
        """Load allowed IPs from environment variable."""
        allowed_ips_str = os.getenv("ADMIN_ALLOWED_IPS", "")
        
        # Always allow localhost variants for development
        localhost_ips = {"127.0.0.1", "::1", "localhost"}
        
        if not allowed_ips_str:
            logger.warning("ADMIN_ALLOWED_IPS not set. Only localhost will be allowed for admin.")
            return localhost_ips
        
        # Parse comma-separated IPs (skip CIDR notation, handled separately)
        custom_ips = set()
        for ip_str in allowed_ips_str.split(","):
            ip_str = ip_str.strip()
            if ip_str and "/" not in ip_str:  # Skip CIDR notation
                custom_ips.add(ip_str)
        
        return localhost_ips | custom_ips
    
    def _load_allowed_networks(self) -> List:
        """Load allowed CIDR networks from environment variable."""
        allowed_ips_str = os.getenv("ADMIN_ALLOWED_IPS", "")
        networks = []
        
        for ip_str in allowed_ips_str.split(","):
            ip_str = ip_str.strip()
            if ip_str and "/" in ip_str:  # CIDR notation
                try:
                    networks.append(ip_network(ip_str, strict=False))
                except ValueError as e:
                    logger.error(f"Invalid CIDR network in ADMIN_ALLOWED_IPS: {ip_str} - {e}")
        
        return networks
    
    def _get_client_ip(self, request: Request) -> str:
        """
        Get the real client IP, considering proxies.
        
        Priority:
        1. X-Forwarded-For header (first IP if multiple)
        2. X-Real-IP header
        3. Direct client IP
        """
        # Check X-Forwarded-For (common with proxies/load balancers)
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            # Take the first IP (original client)
            return forwarded_for.split(",")[0].strip()
        
        # Check X-Real-IP (nginx)
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip.strip()
        
        # Fall back to direct connection IP
        if request.client:
            return request.client.host
        
        return "unknown"
    
    def _is_ip_allowed(self, client_ip: str) -> bool:
        """Check if the IP is in the allowlist."""
        # Direct IP match
        if client_ip in self.allowed_ips:
            return True
        
        # Check CIDR networks
        try:
            client_ip_obj = ip_address(client_ip)
            for network in self.allowed_networks:
                if client_ip_obj in network:
                    return True
        except ValueError:
            # Invalid IP address format
            logger.warning(f"Invalid client IP format: {client_ip}")
            return False
        
        return False
    
    async def dispatch(self, request: Request, call_next):
        """Process request and check IP for admin endpoints."""
        # Only check /admin/* routes
        if not request.url.path.startswith("/admin"):
            return await call_next(request)
        
        # Skip check if disabled
        if not self.enabled:
            return await call_next(request)
        
        # Get client IP
        client_ip = self._get_client_ip(request)
        
        # Check if allowed
        if self._is_ip_allowed(client_ip):
            logger.debug(f"Admin access granted for IP: {client_ip} to {request.url.path}")
            return await call_next(request)
        
        # Block and log
        logger.warning(
            f"BLOCKED admin access attempt from unauthorized IP: {client_ip} "
            f"to {request.url.path} - User-Agent: {request.headers.get('User-Agent', 'unknown')}"
        )
        
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied. Your IP is not authorized for admin access."
        )

Admin IP Allowlist Middleware

Restricts /admin/* endpoints to specific IP addresses for extra security.
Even if someone steals admin credentials, they can't access admin endpoints
from unauthorized locations.

Configuration:
  ADMIN_ALLOWED_IPS=192.168.1.1,10.0.0.1  # Comma-separated IPs
  ADMIN_IP_ALLOWLIST_ENABLED=true         # Enable/disable (default: true in prod)

Features:
  - Supports multiple IPs (comma-separated)
  - Supports CIDR notation (e.g., 192.168.1.0/24)
  - Automatically allows localhost in development
  - Logs blocked attempts for security monitoring
"""

import os
import logging
from ipaddress import ip_address, ip_network
from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from typing import List, Set

logger = logging.getLogger(__name__)


class AdminIPAllowlistMiddleware(BaseHTTPMiddleware):
    """
    Middleware to restrict admin endpoints to allowed IP addresses.
    """
    
    def __init__(self, app):
        super().__init__(app)
        self.enabled = self._is_enabled()
        self.allowed_ips = self._load_allowed_ips()
        self.allowed_networks = self._load_allowed_networks()
        
        if self.enabled:
            logger.info(f"Admin IP allowlist enabled. Allowed IPs: {self.allowed_ips}")
            logger.info(f"Allowed networks: {[str(n) for n in self.allowed_networks]}")
        else:
            logger.warning("Admin IP allowlist is DISABLED. All IPs can access admin endpoints.")
    
    def _is_enabled(self) -> bool:
        """Check if IP allowlist is enabled."""
        # Disabled by default in development for convenience
        env = os.getenv("ENVIRONMENT", "development")
        enabled_env = os.getenv("ADMIN_IP_ALLOWLIST_ENABLED", "").lower()
        
        if enabled_env == "true":
            return True
        elif enabled_env == "false":
            return False
        else:
            # Default: enabled in production, disabled in development
            return env == "production"
    
    def _load_allowed_ips(self) -> Set[str]:
        """Load allowed IPs from environment variable."""
        allowed_ips_str = os.getenv("ADMIN_ALLOWED_IPS", "")
        
        # Always allow localhost variants for development
        localhost_ips = {"127.0.0.1", "::1", "localhost"}
        
        if not allowed_ips_str:
            logger.warning("ADMIN_ALLOWED_IPS not set. Only localhost will be allowed for admin.")
            return localhost_ips
        
        # Parse comma-separated IPs (skip CIDR notation, handled separately)
        custom_ips = set()
        for ip_str in allowed_ips_str.split(","):
            ip_str = ip_str.strip()
            if ip_str and "/" not in ip_str:  # Skip CIDR notation
                custom_ips.add(ip_str)
        
        return localhost_ips | custom_ips
    
    def _load_allowed_networks(self) -> List:
        """Load allowed CIDR networks from environment variable."""
        allowed_ips_str = os.getenv("ADMIN_ALLOWED_IPS", "")
        networks = []
        
        for ip_str in allowed_ips_str.split(","):
            ip_str = ip_str.strip()
            if ip_str and "/" in ip_str:  # CIDR notation
                try:
                    networks.append(ip_network(ip_str, strict=False))
                except ValueError as e:
                    logger.error(f"Invalid CIDR network in ADMIN_ALLOWED_IPS: {ip_str} - {e}")
        
        return networks
    
    def _get_client_ip(self, request: Request) -> str:
        """
        Get the real client IP, considering proxies.
        
        Priority:
        1. X-Forwarded-For header (first IP if multiple)
        2. X-Real-IP header
        3. Direct client IP
        """
        # Check X-Forwarded-For (common with proxies/load balancers)
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            # Take the first IP (original client)
            return forwarded_for.split(",")[0].strip()
        
        # Check X-Real-IP (nginx)
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip.strip()
        
        # Fall back to direct connection IP
        if request.client:
            return request.client.host
        
        return "unknown"
    
    def _is_ip_allowed(self, client_ip: str) -> bool:
        """Check if the IP is in the allowlist."""
        # Direct IP match
        if client_ip in self.allowed_ips:
            return True
        
        # Check CIDR networks
        try:
            client_ip_obj = ip_address(client_ip)
            for network in self.allowed_networks:
                if client_ip_obj in network:
                    return True
        except ValueError:
            # Invalid IP address format
            logger.warning(f"Invalid client IP format: {client_ip}")
            return False
        
        return False
    
    async def dispatch(self, request: Request, call_next):
        """Process request and check IP for admin endpoints."""
        # Only check /admin/* routes
        if not request.url.path.startswith("/admin"):
            return await call_next(request)
        
        # Skip check if disabled
        if not self.enabled:
            return await call_next(request)
        
        # Get client IP
        client_ip = self._get_client_ip(request)
        
        # Check if allowed
        if self._is_ip_allowed(client_ip):
            logger.debug(f"Admin access granted for IP: {client_ip} to {request.url.path}")
            return await call_next(request)
        
        # Block and log
        logger.warning(
            f"BLOCKED admin access attempt from unauthorized IP: {client_ip} "
            f"to {request.url.path} - User-Agent: {request.headers.get('User-Agent', 'unknown')}"
        )
        
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied. Your IP is not authorized for admin access."
        )


Admin IP Allowlist Middleware

Restricts /admin/* endpoints to specific IP addresses for extra security.
Even if someone steals admin credentials, they can't access admin endpoints
from unauthorized locations.

Configuration:
  ADMIN_ALLOWED_IPS=192.168.1.1,10.0.0.1  # Comma-separated IPs
  ADMIN_IP_ALLOWLIST_ENABLED=true         # Enable/disable (default: true in prod)

Features:
  - Supports multiple IPs (comma-separated)
  - Supports CIDR notation (e.g., 192.168.1.0/24)
  - Automatically allows localhost in development
  - Logs blocked attempts for security monitoring
"""

import os
import logging
from ipaddress import ip_address, ip_network
from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from typing import List, Set

logger = logging.getLogger(__name__)


class AdminIPAllowlistMiddleware(BaseHTTPMiddleware):
    """
    Middleware to restrict admin endpoints to allowed IP addresses.
    """
    
    def __init__(self, app):
        super().__init__(app)
        self.enabled = self._is_enabled()
        self.allowed_ips = self._load_allowed_ips()
        self.allowed_networks = self._load_allowed_networks()
        
        if self.enabled:
            logger.info(f"Admin IP allowlist enabled. Allowed IPs: {self.allowed_ips}")
            logger.info(f"Allowed networks: {[str(n) for n in self.allowed_networks]}")
        else:
            logger.warning("Admin IP allowlist is DISABLED. All IPs can access admin endpoints.")
    
    def _is_enabled(self) -> bool:
        """Check if IP allowlist is enabled."""
        # Disabled by default in development for convenience
        env = os.getenv("ENVIRONMENT", "development")
        enabled_env = os.getenv("ADMIN_IP_ALLOWLIST_ENABLED", "").lower()
        
        if enabled_env == "true":
            return True
        elif enabled_env == "false":
            return False
        else:
            # Default: enabled in production, disabled in development
            return env == "production"
    
    def _load_allowed_ips(self) -> Set[str]:
        """Load allowed IPs from environment variable."""
        allowed_ips_str = os.getenv("ADMIN_ALLOWED_IPS", "")
        
        # Always allow localhost variants for development
        localhost_ips = {"127.0.0.1", "::1", "localhost"}
        
        if not allowed_ips_str:
            logger.warning("ADMIN_ALLOWED_IPS not set. Only localhost will be allowed for admin.")
            return localhost_ips
        
        # Parse comma-separated IPs (skip CIDR notation, handled separately)
        custom_ips = set()
        for ip_str in allowed_ips_str.split(","):
            ip_str = ip_str.strip()
            if ip_str and "/" not in ip_str:  # Skip CIDR notation
                custom_ips.add(ip_str)
        
        return localhost_ips | custom_ips
    
    def _load_allowed_networks(self) -> List:
        """Load allowed CIDR networks from environment variable."""
        allowed_ips_str = os.getenv("ADMIN_ALLOWED_IPS", "")
        networks = []
        
        for ip_str in allowed_ips_str.split(","):
            ip_str = ip_str.strip()
            if ip_str and "/" in ip_str:  # CIDR notation
                try:
                    networks.append(ip_network(ip_str, strict=False))
                except ValueError as e:
                    logger.error(f"Invalid CIDR network in ADMIN_ALLOWED_IPS: {ip_str} - {e}")
        
        return networks
    
    def _get_client_ip(self, request: Request) -> str:
        """
        Get the real client IP, considering proxies.
        
        Priority:
        1. X-Forwarded-For header (first IP if multiple)
        2. X-Real-IP header
        3. Direct client IP
        """
        # Check X-Forwarded-For (common with proxies/load balancers)
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            # Take the first IP (original client)
            return forwarded_for.split(",")[0].strip()
        
        # Check X-Real-IP (nginx)
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip.strip()
        
        # Fall back to direct connection IP
        if request.client:
            return request.client.host
        
        return "unknown"
    
    def _is_ip_allowed(self, client_ip: str) -> bool:
        """Check if the IP is in the allowlist."""
        # Direct IP match
        if client_ip in self.allowed_ips:
            return True
        
        # Check CIDR networks
        try:
            client_ip_obj = ip_address(client_ip)
            for network in self.allowed_networks:
                if client_ip_obj in network:
                    return True
        except ValueError:
            # Invalid IP address format
            logger.warning(f"Invalid client IP format: {client_ip}")
            return False
        
        return False
    
    async def dispatch(self, request: Request, call_next):
        """Process request and check IP for admin endpoints."""
        # Only check /admin/* routes
        if not request.url.path.startswith("/admin"):
            return await call_next(request)
        
        # Skip check if disabled
        if not self.enabled:
            return await call_next(request)
        
        # Get client IP
        client_ip = self._get_client_ip(request)
        
        # Check if allowed
        if self._is_ip_allowed(client_ip):
            logger.debug(f"Admin access granted for IP: {client_ip} to {request.url.path}")
            return await call_next(request)
        
        # Block and log
        logger.warning(
            f"BLOCKED admin access attempt from unauthorized IP: {client_ip} "
            f"to {request.url.path} - User-Agent: {request.headers.get('User-Agent', 'unknown')}"
        )
        
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied. Your IP is not authorized for admin access."
        )

Admin IP Allowlist Middleware

Restricts /admin/* endpoints to specific IP addresses for extra security.
Even if someone steals admin credentials, they can't access admin endpoints
from unauthorized locations.

Configuration:
  ADMIN_ALLOWED_IPS=192.168.1.1,10.0.0.1  # Comma-separated IPs
  ADMIN_IP_ALLOWLIST_ENABLED=true         # Enable/disable (default: true in prod)

Features:
  - Supports multiple IPs (comma-separated)
  - Supports CIDR notation (e.g., 192.168.1.0/24)
  - Automatically allows localhost in development
  - Logs blocked attempts for security monitoring
"""

import os
import logging
from ipaddress import ip_address, ip_network
from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from typing import List, Set

logger = logging.getLogger(__name__)


class AdminIPAllowlistMiddleware(BaseHTTPMiddleware):
    """
    Middleware to restrict admin endpoints to allowed IP addresses.
    """
    
    def __init__(self, app):
        super().__init__(app)
        self.enabled = self._is_enabled()
        self.allowed_ips = self._load_allowed_ips()
        self.allowed_networks = self._load_allowed_networks()
        
        if self.enabled:
            logger.info(f"Admin IP allowlist enabled. Allowed IPs: {self.allowed_ips}")
            logger.info(f"Allowed networks: {[str(n) for n in self.allowed_networks]}")
        else:
            logger.warning("Admin IP allowlist is DISABLED. All IPs can access admin endpoints.")
    
    def _is_enabled(self) -> bool:
        """Check if IP allowlist is enabled."""
        # Disabled by default in development for convenience
        env = os.getenv("ENVIRONMENT", "development")
        enabled_env = os.getenv("ADMIN_IP_ALLOWLIST_ENABLED", "").lower()
        
        if enabled_env == "true":
            return True
        elif enabled_env == "false":
            return False
        else:
            # Default: enabled in production, disabled in development
            return env == "production"
    
    def _load_allowed_ips(self) -> Set[str]:
        """Load allowed IPs from environment variable."""
        allowed_ips_str = os.getenv("ADMIN_ALLOWED_IPS", "")
        
        # Always allow localhost variants for development
        localhost_ips = {"127.0.0.1", "::1", "localhost"}
        
        if not allowed_ips_str:
            logger.warning("ADMIN_ALLOWED_IPS not set. Only localhost will be allowed for admin.")
            return localhost_ips
        
        # Parse comma-separated IPs (skip CIDR notation, handled separately)
        custom_ips = set()
        for ip_str in allowed_ips_str.split(","):
            ip_str = ip_str.strip()
            if ip_str and "/" not in ip_str:  # Skip CIDR notation
                custom_ips.add(ip_str)
        
        return localhost_ips | custom_ips
    
    def _load_allowed_networks(self) -> List:
        """Load allowed CIDR networks from environment variable."""
        allowed_ips_str = os.getenv("ADMIN_ALLOWED_IPS", "")
        networks = []
        
        for ip_str in allowed_ips_str.split(","):
            ip_str = ip_str.strip()
            if ip_str and "/" in ip_str:  # CIDR notation
                try:
                    networks.append(ip_network(ip_str, strict=False))
                except ValueError as e:
                    logger.error(f"Invalid CIDR network in ADMIN_ALLOWED_IPS: {ip_str} - {e}")
        
        return networks
    
    def _get_client_ip(self, request: Request) -> str:
        """
        Get the real client IP, considering proxies.
        
        Priority:
        1. X-Forwarded-For header (first IP if multiple)
        2. X-Real-IP header
        3. Direct client IP
        """
        # Check X-Forwarded-For (common with proxies/load balancers)
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            # Take the first IP (original client)
            return forwarded_for.split(",")[0].strip()
        
        # Check X-Real-IP (nginx)
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip.strip()
        
        # Fall back to direct connection IP
        if request.client:
            return request.client.host
        
        return "unknown"
    
    def _is_ip_allowed(self, client_ip: str) -> bool:
        """Check if the IP is in the allowlist."""
        # Direct IP match
        if client_ip in self.allowed_ips:
            return True
        
        # Check CIDR networks
        try:
            client_ip_obj = ip_address(client_ip)
            for network in self.allowed_networks:
                if client_ip_obj in network:
                    return True
        except ValueError:
            # Invalid IP address format
            logger.warning(f"Invalid client IP format: {client_ip}")
            return False
        
        return False
    
    async def dispatch(self, request: Request, call_next):
        """Process request and check IP for admin endpoints."""
        # Only check /admin/* routes
        if not request.url.path.startswith("/admin"):
            return await call_next(request)
        
        # Skip check if disabled
        if not self.enabled:
            return await call_next(request)
        
        # Get client IP
        client_ip = self._get_client_ip(request)
        
        # Check if allowed
        if self._is_ip_allowed(client_ip):
            logger.debug(f"Admin access granted for IP: {client_ip} to {request.url.path}")
            return await call_next(request)
        
        # Block and log
        logger.warning(
            f"BLOCKED admin access attempt from unauthorized IP: {client_ip} "
            f"to {request.url.path} - User-Agent: {request.headers.get('User-Agent', 'unknown')}"
        )
        
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied. Your IP is not authorized for admin access."
        )

Admin IP Allowlist Middleware

Restricts /admin/* endpoints to specific IP addresses for extra security.
Even if someone steals admin credentials, they can't access admin endpoints
from unauthorized locations.

Configuration:
  ADMIN_ALLOWED_IPS=192.168.1.1,10.0.0.1  # Comma-separated IPs
  ADMIN_IP_ALLOWLIST_ENABLED=true         # Enable/disable (default: true in prod)

Features:
  - Supports multiple IPs (comma-separated)
  - Supports CIDR notation (e.g., 192.168.1.0/24)
  - Automatically allows localhost in development
  - Logs blocked attempts for security monitoring
"""

import os
import logging
from ipaddress import ip_address, ip_network
from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from typing import List, Set

logger = logging.getLogger(__name__)


class AdminIPAllowlistMiddleware(BaseHTTPMiddleware):
    """
    Middleware to restrict admin endpoints to allowed IP addresses.
    """
    
    def __init__(self, app):
        super().__init__(app)
        self.enabled = self._is_enabled()
        self.allowed_ips = self._load_allowed_ips()
        self.allowed_networks = self._load_allowed_networks()
        
        if self.enabled:
            logger.info(f"Admin IP allowlist enabled. Allowed IPs: {self.allowed_ips}")
            logger.info(f"Allowed networks: {[str(n) for n in self.allowed_networks]}")
        else:
            logger.warning("Admin IP allowlist is DISABLED. All IPs can access admin endpoints.")
    
    def _is_enabled(self) -> bool:
        """Check if IP allowlist is enabled."""
        # Disabled by default in development for convenience
        env = os.getenv("ENVIRONMENT", "development")
        enabled_env = os.getenv("ADMIN_IP_ALLOWLIST_ENABLED", "").lower()
        
        if enabled_env == "true":
            return True
        elif enabled_env == "false":
            return False
        else:
            # Default: enabled in production, disabled in development
            return env == "production"
    
    def _load_allowed_ips(self) -> Set[str]:
        """Load allowed IPs from environment variable."""
        allowed_ips_str = os.getenv("ADMIN_ALLOWED_IPS", "")
        
        # Always allow localhost variants for development
        localhost_ips = {"127.0.0.1", "::1", "localhost"}
        
        if not allowed_ips_str:
            logger.warning("ADMIN_ALLOWED_IPS not set. Only localhost will be allowed for admin.")
            return localhost_ips
        
        # Parse comma-separated IPs (skip CIDR notation, handled separately)
        custom_ips = set()
        for ip_str in allowed_ips_str.split(","):
            ip_str = ip_str.strip()
            if ip_str and "/" not in ip_str:  # Skip CIDR notation
                custom_ips.add(ip_str)
        
        return localhost_ips | custom_ips
    
    def _load_allowed_networks(self) -> List:
        """Load allowed CIDR networks from environment variable."""
        allowed_ips_str = os.getenv("ADMIN_ALLOWED_IPS", "")
        networks = []
        
        for ip_str in allowed_ips_str.split(","):
            ip_str = ip_str.strip()
            if ip_str and "/" in ip_str:  # CIDR notation
                try:
                    networks.append(ip_network(ip_str, strict=False))
                except ValueError as e:
                    logger.error(f"Invalid CIDR network in ADMIN_ALLOWED_IPS: {ip_str} - {e}")
        
        return networks
    
    def _get_client_ip(self, request: Request) -> str:
        """
        Get the real client IP, considering proxies.
        
        Priority:
        1. X-Forwarded-For header (first IP if multiple)
        2. X-Real-IP header
        3. Direct client IP
        """
        # Check X-Forwarded-For (common with proxies/load balancers)
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            # Take the first IP (original client)
            return forwarded_for.split(",")[0].strip()
        
        # Check X-Real-IP (nginx)
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip.strip()
        
        # Fall back to direct connection IP
        if request.client:
            return request.client.host
        
        return "unknown"
    
    def _is_ip_allowed(self, client_ip: str) -> bool:
        """Check if the IP is in the allowlist."""
        # Direct IP match
        if client_ip in self.allowed_ips:
            return True
        
        # Check CIDR networks
        try:
            client_ip_obj = ip_address(client_ip)
            for network in self.allowed_networks:
                if client_ip_obj in network:
                    return True
        except ValueError:
            # Invalid IP address format
            logger.warning(f"Invalid client IP format: {client_ip}")
            return False
        
        return False
    
    async def dispatch(self, request: Request, call_next):
        """Process request and check IP for admin endpoints."""
        # Only check /admin/* routes
        if not request.url.path.startswith("/admin"):
            return await call_next(request)
        
        # Skip check if disabled
        if not self.enabled:
            return await call_next(request)
        
        # Get client IP
        client_ip = self._get_client_ip(request)
        
        # Check if allowed
        if self._is_ip_allowed(client_ip):
            logger.debug(f"Admin access granted for IP: {client_ip} to {request.url.path}")
            return await call_next(request)
        
        # Block and log
        logger.warning(
            f"BLOCKED admin access attempt from unauthorized IP: {client_ip} "
            f"to {request.url.path} - User-Agent: {request.headers.get('User-Agent', 'unknown')}"
        )
        
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied. Your IP is not authorized for admin access."
        )


Admin IP Allowlist Middleware

Restricts /admin/* endpoints to specific IP addresses for extra security.
Even if someone steals admin credentials, they can't access admin endpoints
from unauthorized locations.

Configuration:
  ADMIN_ALLOWED_IPS=192.168.1.1,10.0.0.1  # Comma-separated IPs
  ADMIN_IP_ALLOWLIST_ENABLED=true         # Enable/disable (default: true in prod)

Features:
  - Supports multiple IPs (comma-separated)
  - Supports CIDR notation (e.g., 192.168.1.0/24)
  - Automatically allows localhost in development
  - Logs blocked attempts for security monitoring
"""

import os
import logging
from ipaddress import ip_address, ip_network
from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from typing import List, Set

logger = logging.getLogger(__name__)


class AdminIPAllowlistMiddleware(BaseHTTPMiddleware):
    """
    Middleware to restrict admin endpoints to allowed IP addresses.
    """
    
    def __init__(self, app):
        super().__init__(app)
        self.enabled = self._is_enabled()
        self.allowed_ips = self._load_allowed_ips()
        self.allowed_networks = self._load_allowed_networks()
        
        if self.enabled:
            logger.info(f"Admin IP allowlist enabled. Allowed IPs: {self.allowed_ips}")
            logger.info(f"Allowed networks: {[str(n) for n in self.allowed_networks]}")
        else:
            logger.warning("Admin IP allowlist is DISABLED. All IPs can access admin endpoints.")
    
    def _is_enabled(self) -> bool:
        """Check if IP allowlist is enabled."""
        # Disabled by default in development for convenience
        env = os.getenv("ENVIRONMENT", "development")
        enabled_env = os.getenv("ADMIN_IP_ALLOWLIST_ENABLED", "").lower()
        
        if enabled_env == "true":
            return True
        elif enabled_env == "false":
            return False
        else:
            # Default: enabled in production, disabled in development
            return env == "production"
    
    def _load_allowed_ips(self) -> Set[str]:
        """Load allowed IPs from environment variable."""
        allowed_ips_str = os.getenv("ADMIN_ALLOWED_IPS", "")
        
        # Always allow localhost variants for development
        localhost_ips = {"127.0.0.1", "::1", "localhost"}
        
        if not allowed_ips_str:
            logger.warning("ADMIN_ALLOWED_IPS not set. Only localhost will be allowed for admin.")
            return localhost_ips
        
        # Parse comma-separated IPs (skip CIDR notation, handled separately)
        custom_ips = set()
        for ip_str in allowed_ips_str.split(","):
            ip_str = ip_str.strip()
            if ip_str and "/" not in ip_str:  # Skip CIDR notation
                custom_ips.add(ip_str)
        
        return localhost_ips | custom_ips
    
    def _load_allowed_networks(self) -> List:
        """Load allowed CIDR networks from environment variable."""
        allowed_ips_str = os.getenv("ADMIN_ALLOWED_IPS", "")
        networks = []
        
        for ip_str in allowed_ips_str.split(","):
            ip_str = ip_str.strip()
            if ip_str and "/" in ip_str:  # CIDR notation
                try:
                    networks.append(ip_network(ip_str, strict=False))
                except ValueError as e:
                    logger.error(f"Invalid CIDR network in ADMIN_ALLOWED_IPS: {ip_str} - {e}")
        
        return networks
    
    def _get_client_ip(self, request: Request) -> str:
        """
        Get the real client IP, considering proxies.
        
        Priority:
        1. X-Forwarded-For header (first IP if multiple)
        2. X-Real-IP header
        3. Direct client IP
        """
        # Check X-Forwarded-For (common with proxies/load balancers)
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            # Take the first IP (original client)
            return forwarded_for.split(",")[0].strip()
        
        # Check X-Real-IP (nginx)
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip.strip()
        
        # Fall back to direct connection IP
        if request.client:
            return request.client.host
        
        return "unknown"
    
    def _is_ip_allowed(self, client_ip: str) -> bool:
        """Check if the IP is in the allowlist."""
        # Direct IP match
        if client_ip in self.allowed_ips:
            return True
        
        # Check CIDR networks
        try:
            client_ip_obj = ip_address(client_ip)
            for network in self.allowed_networks:
                if client_ip_obj in network:
                    return True
        except ValueError:
            # Invalid IP address format
            logger.warning(f"Invalid client IP format: {client_ip}")
            return False
        
        return False
    
    async def dispatch(self, request: Request, call_next):
        """Process request and check IP for admin endpoints."""
        # Only check /admin/* routes
        if not request.url.path.startswith("/admin"):
            return await call_next(request)
        
        # Skip check if disabled
        if not self.enabled:
            return await call_next(request)
        
        # Get client IP
        client_ip = self._get_client_ip(request)
        
        # Check if allowed
        if self._is_ip_allowed(client_ip):
            logger.debug(f"Admin access granted for IP: {client_ip} to {request.url.path}")
            return await call_next(request)
        
        # Block and log
        logger.warning(
            f"BLOCKED admin access attempt from unauthorized IP: {client_ip} "
            f"to {request.url.path} - User-Agent: {request.headers.get('User-Agent', 'unknown')}"
        )
        
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied. Your IP is not authorized for admin access."
        )

Admin IP Allowlist Middleware

Restricts /admin/* endpoints to specific IP addresses for extra security.
Even if someone steals admin credentials, they can't access admin endpoints
from unauthorized locations.

Configuration:
  ADMIN_ALLOWED_IPS=192.168.1.1,10.0.0.1  # Comma-separated IPs
  ADMIN_IP_ALLOWLIST_ENABLED=true         # Enable/disable (default: true in prod)

Features:
  - Supports multiple IPs (comma-separated)
  - Supports CIDR notation (e.g., 192.168.1.0/24)
  - Automatically allows localhost in development
  - Logs blocked attempts for security monitoring
"""

import os
import logging
from ipaddress import ip_address, ip_network
from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from typing import List, Set

logger = logging.getLogger(__name__)


class AdminIPAllowlistMiddleware(BaseHTTPMiddleware):
    """
    Middleware to restrict admin endpoints to allowed IP addresses.
    """
    
    def __init__(self, app):
        super().__init__(app)
        self.enabled = self._is_enabled()
        self.allowed_ips = self._load_allowed_ips()
        self.allowed_networks = self._load_allowed_networks()
        
        if self.enabled:
            logger.info(f"Admin IP allowlist enabled. Allowed IPs: {self.allowed_ips}")
            logger.info(f"Allowed networks: {[str(n) for n in self.allowed_networks]}")
        else:
            logger.warning("Admin IP allowlist is DISABLED. All IPs can access admin endpoints.")
    
    def _is_enabled(self) -> bool:
        """Check if IP allowlist is enabled."""
        # Disabled by default in development for convenience
        env = os.getenv("ENVIRONMENT", "development")
        enabled_env = os.getenv("ADMIN_IP_ALLOWLIST_ENABLED", "").lower()
        
        if enabled_env == "true":
            return True
        elif enabled_env == "false":
            return False
        else:
            # Default: enabled in production, disabled in development
            return env == "production"
    
    def _load_allowed_ips(self) -> Set[str]:
        """Load allowed IPs from environment variable."""
        allowed_ips_str = os.getenv("ADMIN_ALLOWED_IPS", "")
        
        # Always allow localhost variants for development
        localhost_ips = {"127.0.0.1", "::1", "localhost"}
        
        if not allowed_ips_str:
            logger.warning("ADMIN_ALLOWED_IPS not set. Only localhost will be allowed for admin.")
            return localhost_ips
        
        # Parse comma-separated IPs (skip CIDR notation, handled separately)
        custom_ips = set()
        for ip_str in allowed_ips_str.split(","):
            ip_str = ip_str.strip()
            if ip_str and "/" not in ip_str:  # Skip CIDR notation
                custom_ips.add(ip_str)
        
        return localhost_ips | custom_ips
    
    def _load_allowed_networks(self) -> List:
        """Load allowed CIDR networks from environment variable."""
        allowed_ips_str = os.getenv("ADMIN_ALLOWED_IPS", "")
        networks = []
        
        for ip_str in allowed_ips_str.split(","):
            ip_str = ip_str.strip()
            if ip_str and "/" in ip_str:  # CIDR notation
                try:
                    networks.append(ip_network(ip_str, strict=False))
                except ValueError as e:
                    logger.error(f"Invalid CIDR network in ADMIN_ALLOWED_IPS: {ip_str} - {e}")
        
        return networks
    
    def _get_client_ip(self, request: Request) -> str:
        """
        Get the real client IP, considering proxies.
        
        Priority:
        1. X-Forwarded-For header (first IP if multiple)
        2. X-Real-IP header
        3. Direct client IP
        """
        # Check X-Forwarded-For (common with proxies/load balancers)
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            # Take the first IP (original client)
            return forwarded_for.split(",")[0].strip()
        
        # Check X-Real-IP (nginx)
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip.strip()
        
        # Fall back to direct connection IP
        if request.client:
            return request.client.host
        
        return "unknown"
    
    def _is_ip_allowed(self, client_ip: str) -> bool:
        """Check if the IP is in the allowlist."""
        # Direct IP match
        if client_ip in self.allowed_ips:
            return True
        
        # Check CIDR networks
        try:
            client_ip_obj = ip_address(client_ip)
            for network in self.allowed_networks:
                if client_ip_obj in network:
                    return True
        except ValueError:
            # Invalid IP address format
            logger.warning(f"Invalid client IP format: {client_ip}")
            return False
        
        return False
    
    async def dispatch(self, request: Request, call_next):
        """Process request and check IP for admin endpoints."""
        # Only check /admin/* routes
        if not request.url.path.startswith("/admin"):
            return await call_next(request)
        
        # Skip check if disabled
        if not self.enabled:
            return await call_next(request)
        
        # Get client IP
        client_ip = self._get_client_ip(request)
        
        # Check if allowed
        if self._is_ip_allowed(client_ip):
            logger.debug(f"Admin access granted for IP: {client_ip} to {request.url.path}")
            return await call_next(request)
        
        # Block and log
        logger.warning(
            f"BLOCKED admin access attempt from unauthorized IP: {client_ip} "
            f"to {request.url.path} - User-Agent: {request.headers.get('User-Agent', 'unknown')}"
        )
        
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied. Your IP is not authorized for admin access."
        )

Admin IP Allowlist Middleware

Restricts /admin/* endpoints to specific IP addresses for extra security.
Even if someone steals admin credentials, they can't access admin endpoints
from unauthorized locations.

Configuration:
  ADMIN_ALLOWED_IPS=192.168.1.1,10.0.0.1  # Comma-separated IPs
  ADMIN_IP_ALLOWLIST_ENABLED=true         # Enable/disable (default: true in prod)

Features:
  - Supports multiple IPs (comma-separated)
  - Supports CIDR notation (e.g., 192.168.1.0/24)
  - Automatically allows localhost in development
  - Logs blocked attempts for security monitoring
"""

import os
import logging
from ipaddress import ip_address, ip_network
from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from typing import List, Set

logger = logging.getLogger(__name__)


class AdminIPAllowlistMiddleware(BaseHTTPMiddleware):
    """
    Middleware to restrict admin endpoints to allowed IP addresses.
    """
    
    def __init__(self, app):
        super().__init__(app)
        self.enabled = self._is_enabled()
        self.allowed_ips = self._load_allowed_ips()
        self.allowed_networks = self._load_allowed_networks()
        
        if self.enabled:
            logger.info(f"Admin IP allowlist enabled. Allowed IPs: {self.allowed_ips}")
            logger.info(f"Allowed networks: {[str(n) for n in self.allowed_networks]}")
        else:
            logger.warning("Admin IP allowlist is DISABLED. All IPs can access admin endpoints.")
    
    def _is_enabled(self) -> bool:
        """Check if IP allowlist is enabled."""
        # Disabled by default in development for convenience
        env = os.getenv("ENVIRONMENT", "development")
        enabled_env = os.getenv("ADMIN_IP_ALLOWLIST_ENABLED", "").lower()
        
        if enabled_env == "true":
            return True
        elif enabled_env == "false":
            return False
        else:
            # Default: enabled in production, disabled in development
            return env == "production"
    
    def _load_allowed_ips(self) -> Set[str]:
        """Load allowed IPs from environment variable."""
        allowed_ips_str = os.getenv("ADMIN_ALLOWED_IPS", "")
        
        # Always allow localhost variants for development
        localhost_ips = {"127.0.0.1", "::1", "localhost"}
        
        if not allowed_ips_str:
            logger.warning("ADMIN_ALLOWED_IPS not set. Only localhost will be allowed for admin.")
            return localhost_ips
        
        # Parse comma-separated IPs (skip CIDR notation, handled separately)
        custom_ips = set()
        for ip_str in allowed_ips_str.split(","):
            ip_str = ip_str.strip()
            if ip_str and "/" not in ip_str:  # Skip CIDR notation
                custom_ips.add(ip_str)
        
        return localhost_ips | custom_ips
    
    def _load_allowed_networks(self) -> List:
        """Load allowed CIDR networks from environment variable."""
        allowed_ips_str = os.getenv("ADMIN_ALLOWED_IPS", "")
        networks = []
        
        for ip_str in allowed_ips_str.split(","):
            ip_str = ip_str.strip()
            if ip_str and "/" in ip_str:  # CIDR notation
                try:
                    networks.append(ip_network(ip_str, strict=False))
                except ValueError as e:
                    logger.error(f"Invalid CIDR network in ADMIN_ALLOWED_IPS: {ip_str} - {e}")
        
        return networks
    
    def _get_client_ip(self, request: Request) -> str:
        """
        Get the real client IP, considering proxies.
        
        Priority:
        1. X-Forwarded-For header (first IP if multiple)
        2. X-Real-IP header
        3. Direct client IP
        """
        # Check X-Forwarded-For (common with proxies/load balancers)
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            # Take the first IP (original client)
            return forwarded_for.split(",")[0].strip()
        
        # Check X-Real-IP (nginx)
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip.strip()
        
        # Fall back to direct connection IP
        if request.client:
            return request.client.host
        
        return "unknown"
    
    def _is_ip_allowed(self, client_ip: str) -> bool:
        """Check if the IP is in the allowlist."""
        # Direct IP match
        if client_ip in self.allowed_ips:
            return True
        
        # Check CIDR networks
        try:
            client_ip_obj = ip_address(client_ip)
            for network in self.allowed_networks:
                if client_ip_obj in network:
                    return True
        except ValueError:
            # Invalid IP address format
            logger.warning(f"Invalid client IP format: {client_ip}")
            return False
        
        return False
    
    async def dispatch(self, request: Request, call_next):
        """Process request and check IP for admin endpoints."""
        # Only check /admin/* routes
        if not request.url.path.startswith("/admin"):
            return await call_next(request)
        
        # Skip check if disabled
        if not self.enabled:
            return await call_next(request)
        
        # Get client IP
        client_ip = self._get_client_ip(request)
        
        # Check if allowed
        if self._is_ip_allowed(client_ip):
            logger.debug(f"Admin access granted for IP: {client_ip} to {request.url.path}")
            return await call_next(request)
        
        # Block and log
        logger.warning(
            f"BLOCKED admin access attempt from unauthorized IP: {client_ip} "
            f"to {request.url.path} - User-Agent: {request.headers.get('User-Agent', 'unknown')}"
        )
        
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied. Your IP is not authorized for admin access."
        )




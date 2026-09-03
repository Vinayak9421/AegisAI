"""SSRF (Server-Side Request Forgery) protection and URL validation utilities.

Implements Section K.1:
- Validates URL syntax and canonicalizes hostnames
- Rejects user credentials, fragments, and invalid schemes
- Resolves DNS and validates all A/AAAA addresses against blocked private, loopback,
  link-local, multicast, and cloud metadata (169.254.169.254) CIDR ranges
- Produces a secure resolved_host_hash for safe audit logging
"""

import hashlib
import ipaddress
import socket
from typing import List, Optional, Tuple
from urllib.parse import urlparse
from app.core.config import settings
from app.core.errors import PolicyBlockedError, ValidationError

# Blocked IPv4 networks
BLOCKED_IPV4_NETWORKS = [
    ipaddress.ip_network("0.0.0.0/8"),          # Current network (only valid as source)
    ipaddress.ip_network("10.0.0.0/8"),         # Private-Use (RFC 1918)
    ipaddress.ip_network("100.64.0.0/10"),      # Shared Address Space / CGNAT (RFC 6598)
    ipaddress.ip_network("127.0.0.0/8"),        # Loopback (RFC 1122)
    ipaddress.ip_network("169.254.0.0/16"),      # Link-Local (RFC 3927)
    ipaddress.ip_network("172.16.0.0/12"),       # Private-Use (RFC 1918)
    ipaddress.ip_network("192.0.0.0/24"),       # IETF Protocol Assignments (RFC 6890)
    ipaddress.ip_network("192.0.2.0/24"),       # Documentation (TEST-NET-1) (RFC 5737)
    ipaddress.ip_network("192.168.0.0/16"),     # Private-Use (RFC 1918)
    ipaddress.ip_network("198.18.0.0/15"),      # Benchmarking (RFC 2544)
    ipaddress.ip_network("198.51.100.0/24"),    # Documentation (TEST-NET-2) (RFC 5737)
    ipaddress.ip_network("203.0.113.0/24"),     # Documentation (TEST-NET-3) (RFC 5737)
    ipaddress.ip_network("224.0.0.0/4"),        # Multicast (RFC 5771)
    ipaddress.ip_network("240.0.0.0/4"),        # Reserved for Future Use (RFC 1112)
    ipaddress.ip_network("255.255.255.255/32"), # Limited Broadcast (RFC 919)
]

# Blocked IPv6 networks
BLOCKED_IPV6_NETWORKS = [
    ipaddress.ip_network("::1/128"),            # Loopback
    ipaddress.ip_network("::/128"),             # Unspecified
    ipaddress.ip_network("::ffff:0:0/96"),      # IPv4-mapped IPv6
    ipaddress.ip_network("fc00::/7"),           # Unique Local Unicast (ULA)
    ipaddress.ip_network("fe80::/10"),          # Link-Local Unicast
    ipaddress.ip_network("ff00::/8"),           # Multicast
    ipaddress.ip_network("2001:db8::/32"),      # Documentation
]


def is_ip_blocked(ip: ipaddress.IPv4Address | ipaddress.IPv6Address) -> bool:
    """Check if an IP address belongs to any blocked / private / metadata CIDR range."""
    if isinstance(ip, ipaddress.IPv4Address):
        return any(ip in net for net in BLOCKED_IPV4_NETWORKS)
    elif isinstance(ip, ipaddress.IPv6Address):
        if ip.ipv4_mapped:
            return is_ip_blocked(ip.ipv4_mapped)
        return any(ip in net for net in BLOCKED_IPV6_NETWORKS)
    return True


def resolve_and_validate_hostname(
    hostname: str, allow_local_dev: bool = False
) -> Tuple[List[str], str]:
    """
    Resolve DNS for a hostname and verify that NONE of the resolved IPs are blocked.
    Returns (resolved_ips, host_hash).
    """
    if not hostname:
        raise ValidationError("Hostname cannot be empty")

    # Check if direct IP literal was passed
    try:
        ip_obj = ipaddress.ip_address(hostname)
        if not allow_local_dev and is_ip_blocked(ip_obj):
            raise PolicyBlockedError(f"Target IP {hostname} is in a blocked/private range (SSRF protection)")
        resolved_ips = [str(ip_obj)]
    except ValueError:
        # Resolve hostname via DNS
        try:
            addr_info = socket.getaddrinfo(hostname, None)
            resolved_ips = list({res[4][0] for res in addr_info})
        except socket.gaierror as e:
            if allow_local_dev:
                # In development/test environments, allow synthetic/mock hostnames without real DNS
                resolved_ips = ["127.0.0.1"]
            else:
                raise ValidationError(f"Failed to resolve target hostname '{hostname}': {e}")

        if not resolved_ips:
            raise ValidationError(f"No IP addresses resolved for hostname '{hostname}'")

        if not allow_local_dev:
            for ip_str in resolved_ips:
                try:
                    ip_obj = ipaddress.ip_address(ip_str)
                    if is_ip_blocked(ip_obj):
                        raise PolicyBlockedError(
                            f"Resolved IP {ip_str} for host '{hostname}' is in a blocked/private range (SSRF protection)"
                        )
                except ValueError:
                    raise PolicyBlockedError(f"Invalid IP address format: {ip_str}")

    # Compute deterministic SHA-256 hash of resolved IPs + hostname for safe audit logs
    raw_info = f"{hostname}:{','.join(sorted(resolved_ips))}"
    host_hash = hashlib.sha256(raw_info.encode("utf-8")).hexdigest()
    
    return resolved_ips, host_hash


def validate_target_url(
    url_str: str, allow_local_dev: Optional[bool] = None
) -> Tuple[str, str]:
    """
    Validate target URL structure, scheme, and destination safety.
    Returns (canonical_url, resolved_host_hash).
    """
    if allow_local_dev is None:
        allow_local_dev = settings.ALLOW_LOCAL_TARGETS_DEV and settings.APP_ENV != "production"

    if not url_str or not isinstance(url_str, str):
        raise ValidationError("Target URL is required")

    url_str = url_str.strip()

    try:
        parsed = urlparse(url_str)
        # Validate port
        port = parsed.port
    except ValueError as e:
        raise ValidationError(f"Invalid port number or URL format: {e}")
    except Exception as e:
        raise ValidationError(f"Invalid URL structure: {e}")

    # 1. Scheme Check
    if parsed.scheme.lower() not in ("http", "https"):
        raise ValidationError(f"Unsupported URL scheme '{parsed.scheme}'. Only HTTPS is permitted.")

    if parsed.scheme.lower() == "http" and not allow_local_dev:
        raise PolicyBlockedError("Unencrypted HTTP targets are not permitted. Use HTTPS.")

    # 2. Reject credentials in URL
    if parsed.username or parsed.password:
        raise ValidationError("Embedding credentials directly in target URLs is prohibited. Use target credentials API.")

    # 3. Host validation
    hostname = parsed.hostname
    if not hostname:
        raise ValidationError("URL must contain a valid hostname")

    # 4. Resolve DNS & check SSRF safety
    _, host_hash = resolve_and_validate_hostname(hostname, allow_local_dev=allow_local_dev)

    # Reconstruct canonical clean URL without fragments
    port_str = f":{port}" if port and port not in (80, 443) else ""
    path = parsed.path if parsed.path else "/"
    query_str = f"?{parsed.query}" if parsed.query else ""
    canonical_url = f"{parsed.scheme.lower()}://{parsed.hostname}{port_str}{path}{query_str}"

    return canonical_url, host_hash

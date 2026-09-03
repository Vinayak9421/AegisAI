"""SSRF validation tests covering IP ranges, schemes, credentials in URLs, and host hashing."""

import pytest
from app.core.errors import PolicyBlockedError, ValidationError
from app.core.ssrf import is_ip_blocked, validate_target_url
import ipaddress


def test_blocked_ip_ranges():
    # IPv4 loopback & private
    assert is_ip_blocked(ipaddress.ip_address("127.0.0.1")) is True
    assert is_ip_blocked(ipaddress.ip_address("10.0.0.50")) is True
    assert is_ip_blocked(ipaddress.ip_address("172.16.0.1")) is True
    assert is_ip_blocked(ipaddress.ip_address("192.168.1.1")) is True
    assert is_ip_blocked(ipaddress.ip_address("169.254.169.254")) is True  # Cloud metadata
    assert is_ip_blocked(ipaddress.ip_address("100.64.0.1")) is True      # CGNAT
    assert is_ip_blocked(ipaddress.ip_address("0.0.0.0")) is True

    # IPv6 loopback & private
    assert is_ip_blocked(ipaddress.ip_address("::1")) is True
    assert is_ip_blocked(ipaddress.ip_address("fc00::1")) is True
    assert is_ip_blocked(ipaddress.ip_address("fe80::1")) is True

    # Public safe IPs
    assert is_ip_blocked(ipaddress.ip_address("8.8.8.8")) is False
    assert is_ip_blocked(ipaddress.ip_address("1.1.1.1")) is False


def test_validate_target_url_rejects_credentials_in_url():
    with pytest.raises(ValidationError, match="Embedding credentials directly in target URLs is prohibited"):
        validate_target_url("https://admin:secretpassword@api.example.com/v1/chat")


def test_validate_target_url_rejects_unsupported_schemes():
    with pytest.raises(ValidationError, match="Unsupported URL scheme"):
        validate_target_url("ftp://api.example.com/v1/chat")
    with pytest.raises(ValidationError, match="Unsupported URL scheme"):
        validate_target_url("file:///etc/passwd")


def test_validate_target_url_rejects_invalid_port():
    with pytest.raises(ValidationError, match="Invalid port number"):
        validate_target_url("https://api.example.com:70000/v1/chat")


def test_validate_target_url_rejects_private_ips_in_strict_mode():
    with pytest.raises(PolicyBlockedError, match="SSRF protection"):
        validate_target_url("https://127.0.0.1:8000/v1/chat", allow_local_dev=False)

    with pytest.raises(PolicyBlockedError, match="SSRF protection"):
        validate_target_url("https://169.254.169.254/latest/meta-data", allow_local_dev=False)

    with pytest.raises(PolicyBlockedError, match="SSRF protection"):
        validate_target_url("https://192.168.1.1/api", allow_local_dev=False)


def test_validate_target_url_allows_safe_public_https():
    canonical_url, host_hash = validate_target_url("https://api.openai.com/v1/chat/completions", allow_local_dev=False)
    assert canonical_url.startswith("https://api.openai.com")
    assert len(host_hash) == 64  # SHA-256


def test_validate_target_url_allows_http_only_in_dev_mode():
    # When allow_local_dev is True
    canonical_url, host_hash = validate_target_url("http://127.0.0.1:8000/v1/chat", allow_local_dev=True)
    assert canonical_url == "http://127.0.0.1:8000/v1/chat"
    assert host_hash is not None

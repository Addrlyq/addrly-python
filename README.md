# addrly

Official Python SDK for the [Addrly](https://addrly.app) email validation API.

## Install

```bash
pip install addrly
```

## Quick Start

```python
from addrly import Addrly

client = Addrly("sk_your_api_key")

# Validate an email
result = client.validate_email("user@example.com")
print(result["mx"], result["disposable"], result["domain_age_in_days"])

# Validate a domain
domain = client.validate_domain("example.com")

# Auto-detect (email or domain)
auto = client.validate("test@gmail.com")
```

## Bulk Validation

```python
# Bulk email validation (Pro: 500, Ultra: 1000)
bulk = client.bulk_validate_emails([
    "user1@gmail.com",
    "user2@yahoo.com",
    "spam@tempmail.com",
])
print(bulk["summary"])  # {"total": 3, "valid": 2, ...}

# Bulk domain validation
domains = client.bulk_validate_domains(["gmail.com", "tempmail.com"])
```

## Gates

```python
# Evaluate an email against a gate
decision = client.gate("gate_abc123def456", email="user@tempmail.com")
print(decision["decision"]["action"])  # "block"
```

## Error Handling

```python
from addrly import Addrly, AddrlyError

try:
    result = client.validate_email("test@example.com")
except AddrlyError as e:
    print(e.status)    # 429
    print(e.error)     # "Rate limit exceeded"
    print(e.response)  # full API error response
```

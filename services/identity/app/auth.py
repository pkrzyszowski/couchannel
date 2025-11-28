from __future__ import annotations

from datetime import UTC, datetime, timedelta
from typing import Any

from jose import jwt

from .config import settings

KEY_ID = "couchannel-dev"
ALGORITHM = "RS256"
PRIVATE_KEY = """-----BEGIN PRIVATE KEY-----
MIIEvwIBADANBgkqhkiG9w0BAQEFAASCBKkwggSlAgEAAoIBAQCqnFz4uv+TD6R2
fq3VMrdiDAdMPbYaWy6xcBSxGgN3PqUcxcqodGUn1zZfaCgvH9J9HzKsp9xkbu3j
Ne8BQsL5k5gcABhy/9C3C23ytt7MRtNnxnrosx0dxXe66gmtGamiTfQ1lHGYJxwz
guoVKL4D2aDm9lJnyt/TJefRY0I1W9HGG9uH9YeVLT+eBVQNYgoTC86kZYVpeIgH
s2EU2pED20Y8G7qeKYmB5AiuXqo5WScWb97in7H6spqlmas2RQiuqJIC+UN8Kklc
Zvk+ByY80nxwyIuhxYPV5hPu0HYRxCWAGNf88CCzEUlxnaniqE2blIr/+3G3wpNQ
/r2cSM8PAgMBAAECggEBAIrT0ZNUFsND5z/EtQ7WxgIyZ33SeWvY5pXb7fpugIN3
pkNTbyTEEcvpg4T+7DPsYQsPZ9y2es/+s/Q+3szX1m/fedbO/RYWs28/DaiCxajT
uRKonzrbBMZE+LhP2K/SQgagCCfRMt3sdTY1QOUW0gev/w3xQfzTSG44Wfo4Gpfv
Ws78QbJ0E3vYmJSYYJsdL70Kc3XUePAvq8I9Kg1/9LumYGMANvde7sp/QeXHGhxp
+4CN8Wnc5WamIxvLiAK7CfwuxdJpGu+CSsa1wY1uTI3WVP+jzxip3xHjxmkp1Fiv
6zwgaR+4kB4AhJkoeOIturVf6MCYMrdWMCOrBAfHcYECgYEA2Yy04T07atFO39Dj
evE+qUzJ6+ahuiMGxVUd4jDV8Bp6N1AoNX5sgTilbszSCcvBUt354Y/IHRIUMcgZ
azKivawy3neQMzrUx/aVzPW9COR4CWWvTVIRdMSbUm8xHZ6/jxJB49Yv9FJJfw/k
xPBVRbMVHZabRbHWIGu50BGkhSsCgYEAyMPaQ0PwsbIRbhnbxkZ4RnUF0decZco0
fMsenXxbQcScmm+sbND7corsqiPeMmww3mKo51Gyt69+y3oeTU9tsg0EZoAznjsz
5CESV9EpWLxrfLFEpVPO096CK9CnRMZByNV5YHMW49cPq4kP1LBkQDF9q3hFlKMu
2gBAg02Z860CgYAkhj4cDsa6AVgntY9rpbMqg2znQTpn4NeTK94viplwjVF1leya
RpZ6/4Ku3o5o/J+BhSkd2KD1WIKxdPHnkIHILHAB77rzDu6If/rYhW1uX8VTdpH+
/kdV/mhBZ8+sNGne4GbVlLFKaMJUJdv3wI3gfNePtyhshBX6LXvt1fh0LwKBgQC9
IJN6joQuQZtd5wo8rKIdbZw/5Ce3VFdBwG9k2IN3X2pPqif6kpxteSYd2ZA2W+ll
dfe7giEkHTULJk1pcwvZkZ21mcwGoarum6EWDTowF8ACRVRvkpXizVg/Ql5w0Xuj
YEbpb0H+/NgMNiAtssWeG4FRiQmzTk6Sm24qw23mOQKBgQCmE42RMjbpiVta6iFp
Q76ZzNnfQfFXVqqhiJ0JnuLYjHDkto3kLugtTn47QAIYv0L2nptbX31gEnOf1Qlt
nY9nHODCUUE79n0HOlLFfpuydMURsrMeLDmEzsN6uzRKh4fySyEWNqnHaftw1H/5
Td8eDiIT8rr1XgbF53/E393W9A==
-----END PRIVATE KEY-----"""

JWKS = {
    "keys": [
        {
            "kty": "RSA",
            "use": "sig",
            "kid": KEY_ID,
            "alg": ALGORITHM,
            "n": "qpxc-Lr_kw-kdn6t1TK3YgwHTD22GlsusXAUsRoDdz6lHMXKqHRlJ9c2X2goLx_SfR8yrKfcZG7t4zXvAULC-ZOYHAAYcv_Qtwtt8rbezEbTZ8Z66LMdHcV3uuoJrRmpok30NZRxmCccM4LqFSi-A9mg5vZSZ8rf0yXn0WNCNVvRxhvbh_WHlS0_ngVUDWIKEwvOpGWFaXiIB7NhFNqRA9tGPBu6nimJgeQIrl6qOVknFm_e4p-x-rKapZmrNkUIrqiSAvlDfCpJXGb5PgcmPNJ8cMiLocWD1eYT7tB2EcQlgBjX_PAgsxFJcZ2p4qhNm5SK__txt8KTUP69nEjPDw",
            "e": "AQAB",
        }
    ]
}


def mint_token(user_id: str, scope: list[str] | None = None) -> dict[str, Any]:
    expires = datetime.now(UTC) + timedelta(seconds=settings.token_ttl_seconds)
    payload = {
        "sub": user_id,
        "scope": scope or ["read:events"],
        "iss": settings.oidc_issuer,
        "aud": settings.oidc_audience,
        "exp": expires,
        "iat": datetime.now(UTC),
    }
    token = jwt.encode(payload, PRIVATE_KEY, algorithm=ALGORITHM, headers={"kid": KEY_ID})
    return {"access_token": token, "token_type": "bearer", "expires_in": settings.token_ttl_seconds}


def get_jwks() -> dict[str, Any]:
    return JWKS

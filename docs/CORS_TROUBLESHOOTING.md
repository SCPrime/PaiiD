# CORS Troubleshooting

## Symptoms
- 403 on proxy with `{ error: "Forbidden (origin)" }`
- OPTIONS preflight blocked

## Checks
- Ensure `ALLOWED_ORIGINS` includes exact scheme+host+port
- Verify backend and proxy use same `ALLOWED_ORIGINS`
- Test preflight:
  - Allowed: `curl -i -X OPTIONS <proxy-url> -H "Origin: <allowed>" -H "Access-Control-Request-Method: GET"`
  - Disallowed: expect 403

## Headers
- Methods: `GET,POST,DELETE,OPTIONS`
- Headers: `content-type,x-request-id,authorization`
- Credentials: `true`

## Diagnostics
- Proxy logs origin/referrer/host decision
- Use `/api/proxy/_routes` to verify allowed prefixes

# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 0.2.x   | :white_check_mark: |
| 0.1.x   | :white_check_mark: |
| < 0.1   | :x:                |

## Reporting a Vulnerability

We take security seriously at RAGlint. If you discover a security vulnerability, please follow these steps:

### 1. **Do Not** Open a Public Issue

Please **do not** report security vulnerabilities through public GitHub issues, discussions, or pull requests.

### 2. Report Privately

Send an email to **security@raglint.ai** (or create a private security advisory on GitHub) with:
- Description of the vulnerability
- Steps to reproduce
- Potential impact
- Suggested fix (if applicable)

### 3. Response Timeline

- **Initial Response**: Within 48 hours
- **Status Update**: Within 7 days
- **Fix Timeline**: Depends on severity
  - **Critical**: 7-14 days
  - **High**: 14-30 days
  - **Medium/Low**: 30-90 days

### 4. Disclosure Policy

- We will work with you to understand and resolve the issue
- We will credit you in the security advisory (unless you prefer to remain anonymous)
- We will coordinate public disclosure after a fix is released

## Security Best Practices

When using RAGLint in production:

### Dashboard Security

1. **Change Default Credentials**: Always create unique user accounts
2. **Use HTTPS**: Deploy behind a reverse proxy (nginx, Caddy) with TLS
3. **Enable Rate Limiting**: Configure rate limits to prevent brute force attacks
4. **Restrict Access**: Use firewall rules or network policies to limit dashboard access

### API Security

1. **Environment Variables**: Never commit secrets to version control
   ```bash
   export OPENAI_API_KEY="your-key-here"
   export SECRET_KEY="generate-a-strong-secret"
   ```

2. **API Keys**: Rotate API keys regularly
3. **Input Validation**: RAGLint validates inputs, but review uploaded data
4. **File Uploads**: Limit file sizes and types (configured in `raglint.yml`)

### Database Security

1. **Backup Regularly**: Use `sqlite3` backup for local deployments
2. **Permissions**: Ensure database file has restrictive permissions (600)
3. **Encryption at Rest**: For sensitive data, use encrypted filesystems

### Dependencies

1. **Keep Updated**: Run `pip install --upgrade raglint` regularly
2. **Audit Dependencies**: We use `pip-audit` in CI/CD
3. **Review Changes**: Check `CHANGELOG.md` for security fixes

### Network Security

1. **Private Networks**: Deploy dashboard on private networks when possible
2. **VPN Access**: Require VPN for remote access
3. **CORS**: Configure CORS settings for your environment
   ```python
   # In dashboard deployment
   app.add_middleware(
       CORSMiddleware,
       allow_origins=["https://yourdomain.com"],
       allow_credentials=True,
   )
   ```

## Security Features

RAGLint includes:
- ✅ **Password Hashing**: Bcrypt with salt
- ✅ **JWT Authentication**: Secure token-based auth
- ✅ **Input Validation**: Pydantic models for all inputs
- ✅ **SQL Injection Prevention**: SQLAlchemy ORM
- ✅ **XSS Prevention**: Template auto-escaping (Jinja2)
- ✅ **CSRF Protection**: Token-based protection (FastAPI default)

## Known Limitations

- **Local Authentication**: Dashboard uses local auth, not SSO (roadmap item)
- **Rate Limiting**: Available but requires manual configuration
- **Audit Logging**: Basic logging, detailed audit logs on roadmap

## Security Roadmap

Planned security enhancements:
- [ ] SSO integration (OAuth2, SAML)
- [ ] Fine-grained access control (RBAC)
- [ ] Detailed audit logs
- [ ] Rate limiting by default
- [ ] Security scanning in pre-commit hooks
- [ ] CVE database monitoring

## Acknowledgments

We appreciate the security research community. Contributors will be acknowledged here:
- (None yet - be the first!)

## Contact

For security concerns: **security@raglint.ai**  
For general questions: **team@raglint.ai**

---

**Last Updated**: 2025-11-22

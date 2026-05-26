from typing import Dict, List, Any, Optional
import structlog
from app.core.agent_base import BaseAgent, ReasoningMode, AgentStatus
from app.core.model_router import TaskType

logger = structlog.get_logger()


class SecurityAgent(BaseAgent):
    """Specialized agent for security analysis and vulnerability detection"""

    def __init__(self, model_router, memory_manager):
        super().__init__(
            agent_id="security",
            name="Security Agent",
            description="Expert in security analysis, vulnerability detection, and threat assessment",
            model_router=model_router,
            memory_manager=memory_manager,
            reasoning_mode=ReasoningMode.DEEP,
        )
        self.security_categories = [
            "authentication",
            "authorization",
            "injection",
            "xss",
            "csrf",
            "data_exposure",
            "cryptography",
            "configuration",
        ]

    async def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Execute security task"""
        self.status = AgentStatus.EXECUTING

        try:
            task_type = task.get("type", "audit")
            description = task.get("description", "")
            context = task.get("context", {})

            if task_type == "audit":
                result = await self.security_audit(description, context)
            elif task_type == "vulnerability":
                result = await self.detect_vulnerabilities(description, context)
            elif task_type == "harden":
                result = await self.security_hardening(description, context)
            elif task_type == "review":
                result = await self.security_review(description, context)
            else:
                result = await self.security_audit(description, context)

            if context.get("enable_reflection", True):
                reflection = await self.reflect(str(result))
                result["reflection"] = reflection

            await self.log_execution(task, result)
            self.status = AgentStatus.COMPLETED

            return result

        except Exception as e:
            logger.error("Security agent execution failed", error=str(e))
            self.status = AgentStatus.FAILED
            raise

    async def security_audit(
        self,
        description: str,
        context: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Perform comprehensive security audit"""

        code = context.get("code", "")
        architecture = context.get("architecture", "")
        scope = context.get("scope", "full")

        prompt = f"""
        Perform a security audit:

        Description: {description}
        Code: {code}
        Architecture: {architecture}
        Scope: {scope}

        Analyze:
        1. Authentication and authorization
        2. Input validation and sanitization
        3. SQL injection vulnerabilities
        4. XSS vulnerabilities
        5. CSRF protection
        6. Data exposure risks
        7. Cryptography usage
        8. Configuration security
        9. Dependency vulnerabilities
        10. API security

        Provide:
        - Severity ratings (Critical, High, Medium, Low)
        - Specific vulnerabilities found
        - Remediation recommendations
        - Priority order for fixes

        Be thorough and specific.
        """

        audit = await self.think(prompt, context)

        return {
            "status": "success",
            "audit": audit,
            "scope": scope,
        }

    async def detect_vulnerabilities(
        self,
        description: str,
        context: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Detect specific vulnerabilities"""

        code = context.get("code", "")
        vulnerability_type = context.get("vulnerability_type", "all")

        prompt = f"""
        Detect vulnerabilities in this code:

        Code:
        {code}

        Focus: {vulnerability_type}
        Description: {description}

        Check for:
        1. Injection flaws (SQL, NoSQL, Command, LDAP)
        2. Broken authentication
        3. Sensitive data exposure
        4. XML external entities (XXE)
        5. Broken access control
        6. Security misconfiguration
        7. Cross-site scripting (XSS)
        8. Insecure deserialization
        9. Using components with known vulnerabilities
        10. Insufficient logging and monitoring

        For each vulnerability found:
        - Exact location in code
        - Severity level
        - Exploitation scenario
        - Fix recommendation
        - Code example of fix
        """

        vulnerabilities = await self.think(prompt, context)

        return {
            "status": "success",
            "vulnerabilities": vulnerabilities,
            "vulnerability_type": vulnerability_type,
        }

    async def security_hardening(
        self,
        description: str,
        context: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Provide security hardening recommendations"""

        system_type = context.get("system_type", "web_application")
        current_security = context.get("current_security", "")

        prompt = f"""
        Provide security hardening recommendations:

        System Type: {system_type}
        Current Security: {current_security}
        Description: {description}

        Provide hardening for:
        1. Network security
        2. Application security
        3. Database security
        4. API security
        5. Authentication mechanisms
        6. Authorization controls
        7. Data encryption
        8. Logging and monitoring
        9. Incident response
        10. Security headers

        For each recommendation:
        - Implementation steps
        - Priority level
        - Expected impact
        - Potential trade-offs
        """

        hardening = await self.think(prompt, context)

        return {
            "status": "success",
            "hardening": hardening,
            "system_type": system_type,
        }

    async def security_review(
        self,
        description: str,
        context: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Review code for security best practices"""

        code = context.get("code", "")
        language = context.get("language", "python")

        prompt = f"""
        Review this code for security best practices:

        Code:
        {code}

        Language: {language}
        Description: {description}

        Evaluate:
        1. Input validation
        2. Output encoding
        3. Authentication implementation
        4. Authorization checks
        5. Cryptography usage
        6. Error handling
        7. Logging practices
        8. Secure configuration
        9. Dependency security
        10. Code quality from security perspective

        Provide:
        - Security score (0-100)
        - Specific issues found
        - Best practice violations
        - Recommendations
        - Secure code examples
        """

        review = await self.think(prompt, context)

        return {
            "status": "success",
            "review": review,
            "language": language,
        }

    def get_system_prompt(self) -> str:
        """Get security agent system prompt"""
        return f"""You are the Security Agent, an expert in cybersecurity and vulnerability assessment.

Security Categories: {', '.join(self.security_categories)}

Your expertise:
- OWASP Top 10
- Secure coding practices
- Penetration testing
- Threat modeling
- Security architecture
- Cryptography
- Compliance (GDPR, HIPAA, PCI-DSS)
- Incident response

Principles:
- Defense in depth
- Least privilege
- Fail securely
- Don't trust user input
- Keep security simple
- Fix security issues early
- Stay updated on threats
- Document security decisions"""

    def get_task_type(self) -> TaskType:
        """Get task type for model routing"""
        return TaskType.REASONING

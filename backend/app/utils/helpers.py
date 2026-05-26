from typing import Any, Dict, List, Optional
from datetime import datetime
import hashlib
import json


def generate_id(prefix: str, *args) -> str:
    """Generate a unique ID with prefix"""
    content = f"{prefix}_{datetime.utcnow().isoformat()}_{'_'.join(str(a) for a in args)}"
    hash_value = hashlib.md5(content.encode()).hexdigest()[:8]
    return f"{prefix}_{hash_value}"


def get_timestamp() -> str:
    """Get current UTC timestamp in ISO format"""
    return datetime.utcnow().isoformat()


def safe_json_loads(data: str, default: Any = None) -> Any:
    """Safely load JSON with fallback"""
    try:
        return json.loads(data)
    except (json.JSONDecodeError, TypeError):
        return default


def safe_json_dumps(data: Any, default: str = "{}") -> str:
    """Safely dump JSON with fallback"""
    try:
        return json.dumps(data)
    except (TypeError, ValueError):
        return default


def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """Truncate text to max length"""
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix


def extract_code_blocks(text: str) -> List[Dict[str, str]]:
    """Extract code blocks from markdown text"""
    import re

    pattern = r"```(\w+)?\n(.*?)```"
    matches = re.findall(pattern, text, re.DOTALL)

    return [
        {
            "language": lang or "text",
            "code": code.strip(),
        }
        for lang, code in matches
    ]


def merge_dicts(*dicts: Dict) -> Dict:
    """Merge multiple dictionaries"""
    result = {}
    for d in dicts:
        if d:
            result.update(d)
    return result


def chunk_list(items: List[Any], chunk_size: int) -> List[List[Any]]:
    """Split list into chunks"""
    return [items[i:i + chunk_size] for i in range(0, len(items), chunk_size)]


def sanitize_filename(filename: str) -> str:
    """Sanitize filename for safe filesystem usage"""
    import re

    # Remove invalid characters
    filename = re.sub(r'[<>:"/\\|?*]', '', filename)

    # Replace spaces with underscores
    filename = filename.replace(' ', '_')

    # Limit length
    if len(filename) > 255:
        name, ext = filename.rsplit('.', 1) if '.' in filename else (filename, '')
        filename = name[:255 - len(ext) - 1] + '.' + ext if ext else name[:255]

    return filename


def calculate_token_estimate(text: str) -> int:
    """Rough estimate of token count (1 token ≈ 4 characters)"""
    return len(text) // 4


def format_duration(seconds: float) -> str:
    """Format duration in human-readable format"""
    if seconds < 60:
        return f"{seconds:.1f}s"
    elif seconds < 3600:
        minutes = seconds / 60
        return f"{minutes:.1f}m"
    else:
        hours = seconds / 3600
        return f"{hours:.1f}h"


def validate_api_key(api_key: str, provider: str) -> bool:
    """Basic API key validation"""
    if not api_key:
        return False

    # Basic format checks
    if provider == "openai" and not api_key.startswith("sk-"):
        return False
    elif provider == "anthropic" and not api_key.startswith("sk-ant-"):
        return False

    return len(api_key) > 20


def parse_model_name(model: str) -> Dict[str, str]:
    """Parse model name into provider and model"""
    parts = model.split('/')

    if len(parts) == 2:
        return {
            "provider": parts[0],
            "model": parts[1],
        }

    # Infer provider from model name
    if model.startswith("gpt"):
        provider = "openai"
    elif model.startswith("claude"):
        provider = "anthropic"
    elif model.startswith("gemini"):
        provider = "google"
    else:
        provider = "unknown"

    return {
        "provider": provider,
        "model": model,
    }

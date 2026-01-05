"""
Heuristic prompt quality analyzer.
Scores prompts on a 1-10 scale based on Claude Code best practices.

Based on research from:
- Anthropic's Claude Code best practices
- Community prompting guidelines
"""

import re
from dataclasses import dataclass


@dataclass
class Score:
    """Prompt quality score with breakdown."""
    total: float          # 1-10 score
    category: str         # grunt, minimal, adequate, solid, excellent
    breakdown: dict       # Individual component scores
    confidence: float     # 0-1 confidence in the score


# === POSITIVE SIGNALS ===

# Context/reasoning indicators (why this task matters)
CONTEXT_MARKERS = [
    'because', 'so that', 'in order to', 'for', 'since',
    'given that', 'considering', 'based on', 'due to',
    'the goal is', 'we need', 'the purpose', 'this will'
]

# Acceptance criteria (what "done" looks like)
CRITERIA_MARKERS = [
    'should', 'must', 'needs to', 'has to', 'make sure', 'ensure',
    'verify', 'check that', 'confirm', 'validate', 'expect',
    'acceptance', 'criteria', 'requirements', 'constraint'
]

# Verification/testing mentions
VERIFICATION_MARKERS = [
    'test', 'verify', 'validate', 'check', 'confirm', 'run',
    'assert', 'expect', 'should pass', 'should fail', 'build'
]

# Specificity patterns (concrete references)
SPECIFICITY_PATTERNS = [
    r'\b\w+\.(py|js|ts|tsx|jsx|go|rs|rb|java|cpp|c|h|md|json|yaml|yml)\b',  # File extensions
    r'@\w+',                                                # @ file references
    r'/[\w/.-]+\.\w+',                                     # File paths
    r'\b(function|class|def|const|let|var|func|fn)\s+\w+', # Code declarations
    r'`[^`]+`',                                            # Inline code
    r'\b[A-Z][a-z]+[A-Z]\w*\b',                           # CamelCase identifiers
    r'\b[a-z]+_[a-z_]+\b',                                # snake_case identifiers
    r'line\s*\d+',                                         # Line numbers
    r'error:?\s*\w+',                                      # Error references
    r'\b(localhost|127\.0\.0\.1|https?://)\S+',           # URLs
]

# Imperative/action language (direct instructions)
IMPERATIVE_PATTERNS = [
    r'^(add|create|write|implement|build|make|update|change|fix|remove|delete|refactor)\b',
    r'\b(add|create|write|implement|build|update|change|fix|remove|delete|refactor)\s+(a|the|this|new)\b',
]

# Structure indicators
STRUCTURE_PATTERNS = [
    r'^\s*[-*•]\s',           # Bullet points
    r'^\s*\d+[.)]\s',         # Numbered lists
    r'^#+\s',                  # Markdown headers
    r'\n\s*\n',               # Paragraph breaks (multiple sections)
]

# === NEGATIVE SIGNALS ===

# Lazy/grunt patterns (immediate low score)
LAZY_PATTERNS = [
    r'^(yes|no|ok|okay|sure|yep|nope|yup|y|n)\.?!?$',
    r'^(continue|go|do it|proceed|next|go on)\.?!?$',
    r'^(good|great|nice|cool|fine|perfect|awesome|thanks|thx|ty)\.?!?$',
    r'^(let\'s do it|let\'s go|sounds good|looks good)\.?!?$',
    r'^\d+\.?$',              # Just a number
    r'^[a-z]\.?$',            # Single letter
    r'^(what|how|why)\?$',    # Single word question
]

# Hedge/passive language (reduces score)
HEDGE_WORDS = [
    'maybe', 'possibly', 'perhaps', 'might', 'could be',
    'i think', 'i guess', 'probably', 'not sure',
    'just', 'quick', 'simple', 'easy'  # minimizing language
]

# Question format instead of imperative (passive)
PASSIVE_QUESTION_PATTERNS = [
    r'^can you\b', r'^could you\b', r'^would you\b',
    r'^do you think\b', r'^what do you think\b',
    r'^is it possible\b', r'^would it be\b',
]

# Vague/generic terms (lacks specificity)
VAGUE_TERMS = [
    'make it better', 'improve it', 'fix it', 'clean it up',
    'make it work', 'optimize it', 'refactor it',
    'something like', 'stuff like', 'things like',
    'etc', 'and so on', 'whatever'
]


def count_words(text: str) -> int:
    """Count words in text."""
    return len(text.split())


def count_matches(text: str, patterns: list, is_regex: bool = False) -> int:
    """Count matches for a list of patterns."""
    text_lower = text.lower()
    count = 0
    for pattern in patterns:
        if is_regex:
            count += len(re.findall(pattern, text, re.IGNORECASE | re.MULTILINE))
        else:
            if pattern.lower() in text_lower:
                count += 1
    return count


def has_structure(text: str) -> bool:
    """Check if text has structural elements."""
    for pattern in STRUCTURE_PATTERNS:
        if re.search(pattern, text, re.MULTILINE):
            return True
    return False


def is_lazy(text: str) -> bool:
    """Check if text matches lazy/grunt patterns."""
    text_stripped = text.strip()
    for pattern in LAZY_PATTERNS:
        if re.match(pattern, text_stripped, re.IGNORECASE):
            return True
    return False


def has_passive_question(text: str) -> bool:
    """Check if text starts with passive question format."""
    text_lower = text.lower().strip()
    for pattern in PASSIVE_QUESTION_PATTERNS:
        if re.match(pattern, text_lower):
            return True
    return False


def has_imperative(text: str) -> bool:
    """Check if text uses imperative/action language."""
    for pattern in IMPERATIVE_PATTERNS:
        if re.search(pattern, text, re.IGNORECASE | re.MULTILINE):
            return True
    return False


def score_prompt(text: str) -> Score:
    """
    Score a prompt on quality/effort based on Claude Code best practices.

    Scoring dimensions:
    - Specificity (25%): concrete references, file paths, code
    - Context (25%): reasoning, background, purpose
    - Clarity (20%): imperative vs passive, directness
    - Constraints (15%): acceptance criteria, requirements
    - Verification (15%): testing, validation mentions

    Returns Score with 1-10 rating.
    """
    # Handle empty/very short
    if not text or len(text.strip()) < 2:
        return Score(1.0, 'grunt', {'reason': 'empty'}, 1.0)

    # Check for lazy patterns first
    if is_lazy(text):
        return Score(1.0, 'grunt', {'reason': 'lazy_pattern'}, 1.0)

    # === Calculate positive signals ===
    word_count = count_words(text)
    char_count = len(text)

    # Specificity (0-2.5): concrete references
    specificity = count_matches(text, SPECIFICITY_PATTERNS, is_regex=True)
    specificity_score = min(2.5, specificity * 0.5)

    # Context (0-2.5): reasoning indicators
    context = count_matches(text, CONTEXT_MARKERS)
    context_score = min(2.5, context * 0.6)

    # Clarity (0-2): imperative vs passive
    clarity_score = 0.0
    if has_imperative(text):
        clarity_score += 1.5
    if not has_passive_question(text):
        clarity_score += 0.5
    clarity_score = min(2.0, clarity_score)

    # Constraints/criteria (0-1.5): acceptance criteria
    criteria = count_matches(text, CRITERIA_MARKERS)
    criteria_score = min(1.5, criteria * 0.4)

    # Verification (0-1.5): testing mentions
    verification = count_matches(text, VERIFICATION_MARKERS)
    verification_score = min(1.5, verification * 0.4)

    # === Calculate negative signals (penalties) ===
    hedge_count = count_matches(text, HEDGE_WORDS)
    hedge_penalty = min(1.5, hedge_count * 0.3)

    vague_count = count_matches(text, VAGUE_TERMS)
    vague_penalty = min(1.0, vague_count * 0.5)

    # === Bonus signals ===
    # Structure bonus
    structure_bonus = 0.5 if has_structure(text) else 0.0

    # Length bonus (reasonable length indicates effort)
    # <10 words = 0, 10-30 = 0.5, 30+ = 1
    length_bonus = 0.0
    if word_count >= 30:
        length_bonus = 1.0
    elif word_count >= 10:
        length_bonus = 0.5

    # === Calculate total ===
    raw_score = (
        specificity_score +      # 0-2.5 (25%)
        context_score +          # 0-2.5 (25%)
        clarity_score +          # 0-2.0 (20%)
        criteria_score +         # 0-1.5 (15%)
        verification_score +     # 0-1.5 (15%)
        structure_bonus +        # 0-0.5 (bonus)
        length_bonus -           # 0-1.0 (bonus)
        hedge_penalty -          # 0-1.5 (penalty)
        vague_penalty            # 0-1.0 (penalty)
    )

    # Scale to 1-10
    total = max(1, min(10, raw_score + 1))

    # Build breakdown
    breakdown = {
        'words': word_count,
        'chars': char_count,
        'specificity': specificity,
        'context_markers': context,
        'criteria_markers': criteria,
        'verification_markers': verification,
        'has_structure': has_structure(text),
        'has_imperative': has_imperative(text),
        'hedge_words': hedge_count,
        'vague_terms': vague_count,
        'scores': {
            'specificity': round(specificity_score, 2),
            'context': round(context_score, 2),
            'clarity': round(clarity_score, 2),
            'criteria': round(criteria_score, 2),
            'verification': round(verification_score, 2),
            'penalties': round(hedge_penalty + vague_penalty, 2)
        }
    }

    # Determine category
    if total <= 2:
        category = 'grunt'
    elif total <= 4:
        category = 'minimal'
    elif total <= 6:
        category = 'adequate'
    elif total <= 8:
        category = 'solid'
    else:
        category = 'excellent'

    # Confidence based on signal clarity
    confidence = 1.0 if total <= 2 or total >= 8 else 0.7

    return Score(round(total, 1), category, breakdown, confidence)


def categorize_score(score: float) -> str:
    """Get category name for a score."""
    if score <= 2:
        return 'grunt'
    elif score <= 4:
        return 'minimal'
    elif score <= 6:
        return 'adequate'
    elif score <= 8:
        return 'solid'
    else:
        return 'excellent'

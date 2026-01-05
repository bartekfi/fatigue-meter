"""
Report generation with ASCII charts and visualizations.
"""

import json
from collections import Counter, defaultdict
from datetime import datetime


def bar_chart(value: float, max_value: float, width: int = 16) -> str:
    """Create ASCII bar chart segment."""
    filled = int((value / max_value) * width) if max_value > 0 else 0
    return '█' * filled + '░' * (width - filled)


def sparkline(values: list[float], width: int = 20) -> str:
    """Create ASCII sparkline from values."""
    if not values:
        return ''
    chars = '▁▂▃▄▅▆▇█'
    min_v, max_v = min(values), max(values)
    if max_v == min_v:
        return chars[4] * len(values)

    normalized = [(v - min_v) / (max_v - min_v) for v in values]
    return ''.join(chars[int(n * 7)] for n in normalized[-width:])


def format_distribution(scores: list[float]) -> dict:
    """Calculate score distribution by category."""
    categories = {
        'grunt': (1, 2),
        'minimal': (3, 4),
        'adequate': (5, 6),
        'solid': (7, 8),
        'excellent': (9, 10)
    }

    total = len(scores)
    if total == 0:
        return {}

    dist = {}
    for name, (low, high) in categories.items():
        count = sum(1 for s in scores if low <= s <= high)
        pct = count / total * 100
        dist[name] = {'count': count, 'percent': pct}

    return dist


def format_hall_of_shame(prompts_with_scores: list, limit: int = 5) -> list:
    """Get worst prompts."""
    sorted_prompts = sorted(prompts_with_scores, key=lambda x: x[1])
    return [(p, s) for p, s in sorted_prompts[:limit]]


def format_hall_of_fame(prompts_with_scores: list, limit: int = 5) -> list:
    """Get best prompts."""
    sorted_prompts = sorted(prompts_with_scores, key=lambda x: x[1], reverse=True)
    return [(p, s) for p, s in sorted_prompts[:limit]]


def format_stamina_heatmap(hourly_stats: dict, dow_stats: dict) -> str:
    """
    Create GitHub-style heatmap showing activity/quality by hour and day.

    Returns ASCII heatmap string.
    """
    days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
    hours = list(range(8, 24)) + list(range(0, 8))  # 8am to 7am order

    # Intensity chars: none, low, med, high
    chars = ['·', '▫', '▪', '█']

    # Build header
    header = '         ' + '  '.join(f'{d:>3}' for d in days)

    lines = [header]

    # For now, just show hourly averages (we'd need hour+day combined stats for full heatmap)
    for hour in hours:
        row = f'{hour:02d}:00    '
        stats = hourly_stats.get(hour, {})
        avg = stats.get('avg_score', 0)
        count = stats.get('count', 0)

        if count == 0:
            intensity = 0
        elif avg <= 3:
            intensity = 1
        elif avg <= 6:
            intensity = 2
        else:
            intensity = 3

        # Repeat for each day (simplified - real version would need hour+day data)
        row += '    '.join([chars[intensity]] * 7)
        lines.append(row)

    lines.append('')
    lines.append('Legend: ·=none ▫=low ▪=med █=high')

    return '\n'.join(lines)


def format_session_pattern(session_data: list[list[float]]) -> str:
    """
    Show how scores change by position in session.

    Args:
        session_data: List of sessions, each containing scores in order
    """
    if not session_data:
        return "No session data"

    # Calculate average at each position
    max_pos = max(len(s) for s in session_data)
    position_avgs = []

    for pos in range(min(max_pos, 15)):
        scores_at_pos = [s[pos] for s in session_data if len(s) > pos]
        if scores_at_pos:
            avg = sum(scores_at_pos) / len(scores_at_pos)
            position_avgs.append((pos + 1, avg, len(scores_at_pos)))

    lines = ['Position in Session vs Average Score:', '']

    for pos, avg, count in position_avgs:
        bar = bar_chart(avg, 10, 10)
        lines.append(f'  {pos:2d}. {bar} {avg:.1f} (n={count})')

    return '\n'.join(lines)


def generate_report(
    scores: list[float],
    prompts_with_scores: list,
    hourly_stats: dict = None,
    dow_stats: dict = None,
    weekly_trend: list = None,
    session_data: list = None,
    paste_count: int = 0,
    total_prompts: int = 0,
    days: int = 30,
    show_shame: bool = True,
    show_pride: bool = True,
    show_stamina: bool = False,
    show_session: bool = False,
    show_trend: bool = False
) -> dict:
    """
    Generate comprehensive report data.

    Returns dict for JSON output that Claude will interpret.
    """
    if not scores:
        return {'error': 'No prompts found', 'prompts_analyzed': 0}

    avg_score = sum(scores) / len(scores)
    distribution = format_distribution(scores)

    report = {
        'summary': {
            'prompts_analyzed': len(scores),
            'time_period_days': days,
            'average_score': round(avg_score, 1),
            'median_score': round(sorted(scores)[len(scores)//2], 1),
        },
        'distribution': distribution,
    }

    # Paste reliance
    if total_prompts > 0:
        report['paste_reliance'] = {
            'prompts_with_paste': paste_count,
            'percent': round(paste_count / total_prompts * 100, 1)
        }

    # Hall of shame
    if show_shame:
        shame = format_hall_of_shame(prompts_with_scores, 5)
        report['hall_of_shame'] = [
            {'text': p[:80] + ('...' if len(p) > 80 else ''), 'score': s}
            for p, s in shame
        ]

    # Hall of fame
    if show_pride:
        fame = format_hall_of_fame(prompts_with_scores, 5)
        report['hall_of_fame'] = [
            {'text': p[:80] + ('...' if len(p) > 80 else ''), 'score': s}
            for p, s in fame
        ]

    # Stamina heatmap
    if show_stamina and hourly_stats:
        report['stamina'] = {
            'by_hour': {str(h): {'avg': round(s['avg_score'], 1), 'count': s['count']}
                       for h, s in hourly_stats.items()},
        }
        if dow_stats:
            day_names = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
            report['stamina']['by_day'] = {
                day_names[d]: {'avg': round(s['avg_score'], 1), 'count': s['count']}
                for d, s in dow_stats.items()
            }

    # Session pattern
    if show_session and session_data:
        position_avgs = []
        max_pos = max(len(s) for s in session_data) if session_data else 0
        for pos in range(min(max_pos, 15)):
            scores_at_pos = [s[pos] for s in session_data if len(s) > pos]
            if scores_at_pos:
                avg = sum(scores_at_pos) / len(scores_at_pos)
                position_avgs.append({'position': pos + 1, 'avg_score': round(avg, 1),
                                     'sample_size': len(scores_at_pos)})
        report['session_pattern'] = position_avgs

    # Weekly trend
    if show_trend and weekly_trend:
        report['weekly_trend'] = weekly_trend
        if len(weekly_trend) >= 2:
            recent = weekly_trend[-1]['avg_score']
            previous = weekly_trend[-2]['avg_score']
            change = recent - previous
            report['trend_direction'] = 'improving' if change > 0.2 else \
                                        'declining' if change < -0.2 else 'stable'

    return report


def format_ascii_report(report: dict) -> str:
    """Format report as ASCII text for terminal display."""
    lines = []

    # Header
    lines.append('┌─────────────────────────────────────────────┐')
    lines.append('│  LAZY METER - Prompt Quality Report         │')
    if 'summary' in report:
        s = report['summary']
        lines.append(f'│  Analyzed: {s["prompts_analyzed"]} prompts (last {s["time_period_days"]} days)       │')
    lines.append('└─────────────────────────────────────────────┘')
    lines.append('')

    # Average score
    if 'summary' in report:
        avg = report['summary']['average_score']
        bar = bar_chart(avg, 10)
        lines.append(f'Your Average Score: {avg}/10  [{bar}]')
        lines.append('')

    # Distribution
    if 'distribution' in report:
        lines.append('Distribution:')
        for cat, data in report['distribution'].items():
            pct = data['percent']
            bar = bar_chart(pct, 100, 16)
            lines.append(f'  {cat:12s} {bar} {pct:4.0f}%')
        lines.append('')

    # Hall of Shame
    if 'hall_of_shame' in report:
        lines.append('Hall of Shame:')
        for i, item in enumerate(report['hall_of_shame'], 1):
            lines.append(f'  {i}. "{item["text"]}" (score: {item["score"]})')
        lines.append('')

    # Hall of Fame
    if 'hall_of_fame' in report:
        lines.append('Hall of Fame:')
        for i, item in enumerate(report['hall_of_fame'], 1):
            lines.append(f'  {i}. "{item["text"]}" (score: {item["score"]})')
        lines.append('')

    return '\n'.join(lines)


def output_json(report: dict) -> str:
    """Output report as JSON for Claude to interpret."""
    return json.dumps(report, indent=2)

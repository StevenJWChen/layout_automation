"""
Constraint Keyword Dictionary

Simple keyword replacement system for common constraint patterns.
Allows writing: 'xcenter, swidth=10' instead of 'sx1+sx2=ox1+ox2, sx2-sx1=10'
"""

import re

# Keyword replacement dictionary
# Maps keyword → actual constraint string
CONSTRAINT_KEYWORDS = {
    # Center keywords
    'xcenter': 'sx1+sx2=ox1+ox2',
    'ycenter': 'sy1+sy2=oy1+oy2',
    'center': 'sx1+sx2=ox1+ox2, sy1+sy2=oy1+oy2',

    # Alignment keywords (edges)
    'left': 'sx1=ox1',
    'right': 'sx2=ox2',
    'top': 'sy2=oy2',
    'bottom': 'sy1=oy1',

    # Single edge distance keywords (object to subject)
    'l_edge': 'ox1-sx1',      # Distance from object left to subject left
    'r_edge': 'ox2-sx2',      # Distance from object right to subject right
    't_edge': 'oy2-sy2',      # Distance from object top to subject top
    'b_edge': 'oy1-sy1',      # Distance from object bottom to subject bottom

    # Edge distance keywords (horizontal)
    # Format: {subject_edge}{object_edge}_edge
    # l=left(x1), r=right(x2), b=bottom(y1), t=top(y2)
    'll_edge': 'sx1-ox1',     # Distance from subject left to object left
    'lr_edge': 'sx1-ox2',     # Distance from subject left to object right
    'rl_edge': 'sx2-ox1',     # Distance from subject right to object left (horizontal spacing)
    'rr_edge': 'sx2-ox2',     # Distance from subject right to object right

    # Edge distance keywords (vertical)
    'bb_edge': 'sy1-oy1',     # Distance from subject bottom to object bottom
    'bt_edge': 'sy1-oy2',     # Distance from subject bottom to object top
    'tb_edge': 'sy2-oy1',     # Distance from subject top to object bottom (vertical spacing)
    'tt_edge': 'sy2-oy2',     # Distance from subject top to object top

    # Size keywords (subject matches object)
    'swidth': 'sx2-sx1',      # Subject width (use with =value or =ox2-ox1)
    'sheight': 'sy2-sy1',     # Subject height
    'owidth': 'ox2-ox1',      # Object width
    'oheight': 'oy2-oy1',     # Object height
    'width': 'x2-x1',         # Width (for self-constraints)
    'height': 'y2-y1',        # Height (for self-constraints)

    # Position keywords
    'sx': 'sx1',              # Subject X (left edge)
    'sy': 'sy1',              # Subject Y (bottom edge)
    'ox': 'ox1',              # Object X (left edge)
    'oy': 'oy1',              # Object Y (bottom edge)
}


def expand_constraint_keywords(constraint_str):
    """
    Expand constraint keywords to full constraint syntax

    Args:
        constraint_str: Constraint string with keywords

    Returns:
        Expanded constraint string

    Examples:
        'xcenter' → 'sx1+sx2=ox1+ox2'
        'xcenter, ycenter' → 'sx1+sx2=ox1+ox2, sy1+sy2=oy1+oy2'
        'xcenter, swidth=10' → 'sx1+sx2=ox1+ox2, sx2-sx1=10'
        'left, swidth=owidth' → 'sx1=ox1, sx2-sx1=ox2-ox1'
        'sx=ox+10, sy=oy' → 'sx1=ox1+10, sy1=oy1'
    """
    if not constraint_str:
        return constraint_str

    result = constraint_str

    # Replace each keyword with its expansion
    # Use word boundaries (\b) to avoid replacing parts of other words (e.g., 'sx' in 'sx2')
    # Sort by length (longest first) to avoid partial replacements (e.g., 'xcenter' before 'center')
    for keyword in sorted(CONSTRAINT_KEYWORDS.keys(), key=len, reverse=True):
        replacement = CONSTRAINT_KEYWORDS[keyword]
        # The pattern looks for the keyword as a whole word.
        result = re.sub(r'\b' + re.escape(keyword) + r'\b', replacement, result)

    return result


# Create reverse mapping for documentation
def get_keyword_table():
    """
    Generate a formatted table of all keywords

    Returns:
        String containing formatted keyword reference table
    """
    table = """
╔════════════════════════════════════════════════════════════════════════════╗
║                     CONSTRAINT KEYWORD REFERENCE                           ║
╚════════════════════════════════════════════════════════════════════════════╝

┌─────────────────────────────────────────────────────────────────────────────┐
│ CENTER KEYWORDS                                                             │
├──────────────────────────┬──────────────────────────────────────────────────┤
│ xcenter                  │ sx1+sx2=ox1+ox2  (center X)                     │
│ ycenter                  │ sy1+sy2=oy1+oy2  (center Y)                     │
│ center                   │ sx1+sx2=ox1+ox2, sy1+sy2=oy1+oy2  (center both) │
└──────────────────────────┴──────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│ ALIGNMENT KEYWORDS                                                          │
├──────────────────────────┬──────────────────────────────────────────────────┤
│ left                     │ sx1=ox1  (align left edges)                     │
│ right                    │ sx2=ox2  (align right edges)                    │
│ top                      │ sy2=oy2  (align top edges)                      │
│ bottom                   │ sy1=oy1  (align bottom edges)                   │
└──────────────────────────┴──────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│ SINGLE EDGE DISTANCE KEYWORDS (Object to Subject)                         │
├──────────────────────────┬──────────────────────────────────────────────────┤
│ l_edge                   │ ox1-sx1  (object left to subject left)          │
│ r_edge                   │ ox2-sx2  (object right to subject right)        │
│ t_edge                   │ oy2-sy2  (object top to subject top)            │
│ b_edge                   │ oy1-sy1  (object bottom to subject bottom)      │
└──────────────────────────┴──────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│ EDGE DISTANCE KEYWORDS (Horizontal)                                        │
├──────────────────────────┬──────────────────────────────────────────────────┤
│ ll_edge                  │ sx1-ox1  (subject left to object left)          │
│ lr_edge                  │ sx1-ox2  (subject left to object right)         │
│ rl_edge                  │ sx2-ox1  (subject right to object left) ⭐      │
│ rr_edge                  │ sx2-ox2  (subject right to object right)        │
│                          │ ⭐ Most useful for horizontal spacing!          │
└──────────────────────────┴──────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│ EDGE DISTANCE KEYWORDS (Vertical)                                          │
├──────────────────────────┬──────────────────────────────────────────────────┤
│ bb_edge                  │ sy1-oy1  (subject bottom to object bottom)      │
│ bt_edge                  │ sy1-oy2  (subject bottom to object top)         │
│ tb_edge                  │ sy2-oy1  (subject top to object bottom) ⭐      │
│ tt_edge                  │ sy2-oy2  (subject top to object top)            │
│                          │ ⭐ Most useful for vertical spacing!            │
└──────────────────────────┴──────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│ SIZE KEYWORDS                                                               │
├──────────────────────────┬──────────────────────────────────────────────────┤
│ swidth                   │ sx2-sx1  (subject width)                        │
│ sheight                  │ sy2-sy1  (subject height)                       │
│ owidth                   │ ox2-ox1  (object width)                         │
│ oheight                  │ oy2-oy1  (object height)                        │
│ width                    │ x2-x1    (width for self-constraints)           │
│ height                   │ y2-y1    (height for self-constraints)          │
└──────────────────────────┴──────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│ POSITION KEYWORDS                                                           │
├──────────────────────────┬──────────────────────────────────────────────────┤
│ sx                       │ sx1  (subject X position)                       │
│ sy                       │ sy1  (subject Y position)                       │
│ ox                       │ ox1  (object X position)                        │
│ oy                       │ oy1  (object Y position)                        │
└──────────────────────────┴──────────────────────────────────────────────────┘

╔════════════════════════════════════════════════════════════════════════════╗
║                           USAGE EXAMPLES                                   ║
╚════════════════════════════════════════════════════════════════════════════╝

Example 1: Center child in parent
    Before: parent.constrain(child, 'sx1+sx2=ox1+ox2, sy1+sy2=oy1+oy2', parent)
    After:  parent.constrain(child, 'center', parent)

Example 2: Center X and set width
    Before: parent.constrain(child, 'sx1+sx2=ox1+ox2, sx2-sx1=10', parent)
    After:  parent.constrain(child, 'xcenter, swidth=10', parent)

Example 3: Align left and match height
    Before: parent.constrain(child2, 'sx1=ox1, sy2-sy1=oy2-oy1', child1)
    After:  parent.constrain(child2, 'left, sheight=oheight', child1)

Example 4: Position to the right with spacing
    Before: parent.constrain(child2, 'sx1=ox2+10, sy1=oy1', child1)
    After:  parent.constrain(child2, 'sx=ox2+10, sy=oy', child1)

Example 5: Match size
    Before: parent.constrain(child2, 'sx2-sx1=ox2-ox1, sy2-sy1=oy2-oy1', child1)
    After:  parent.constrain(child2, 'swidth=owidth, sheight=oheight', child1)

Example 6: Self-constraint with keywords
    Before: cell.constrain('x2-x1=100, y2-y1=50')
    After:  cell.constrain('width=100, height=50')

Example 7: Horizontal spacing using edge keywords ⭐
    Before: parent.constrain(child2, 'sx1=ox2+10', child1)
    After:  parent.constrain(child2, 'rl_edge=10', child1)
    Note:   rl_edge measures from subject's right to object's left

Example 8: Vertical spacing using edge keywords ⭐
    Before: parent.constrain(child2, 'sy1=oy2+5', child1)
    After:  parent.constrain(child2, 'tb_edge=5', child1)
    Note:   tb_edge measures from subject's top to object's bottom

Example 9: Check for overlap
    Before: parent.constrain(child2, 'sx1-ox2<0', child1)  # overlap check
    After:  parent.constrain(child2, 'lr_edge<0', child1)   # more readable!

Example 10: Combined edge constraints
    Before: parent.constrain(child2, 'sx1=ox2+10, sy1=oy1', child1)
    After:  parent.constrain(child2, 'rl_edge=10, bb_edge=0', child1)

╔════════════════════════════════════════════════════════════════════════════╗
║                        COMBINING KEYWORDS                                  ║
╚════════════════════════════════════════════════════════════════════════════╝

Keywords can be combined with commas:

    'xcenter, ycenter'           → center both axes
    'left, top'                  → align left and top edges
    'xcenter, swidth=20'         → center X and set width
    'sx=ox2+5, sy=oy, swidth=10' → position to right with spacing
    'center, swidth=30'          → center and set width
    'left, sheight=oheight'      → align left and match height

Keywords work with any operators and values:

    'swidth=10'              → set width to 10
    'swidth=owidth'          → match object width
    'swidth>=10'             → width at least 10
    'sx=ox+10'               → 10 units to the right
    'xcenter, swidth=owidth+5' → center and width = object width + 5

"""
    return table


def print_keyword_reference():
    """Print the keyword reference table"""
    print(get_keyword_table())


# Export for use in other modules
__all__ = [
    'CONSTRAINT_KEYWORDS',
    'expand_constraint_keywords',
    'get_keyword_table',
    'print_keyword_reference',
]

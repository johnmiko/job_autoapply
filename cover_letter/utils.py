def get_posting_lines(fname):
    with open(fname, 'r') as f:
        content = f.read()
    content_lower = content.lower()
    lines = content_lower.split('\n')
    return lines

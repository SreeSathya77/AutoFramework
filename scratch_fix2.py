import sys

with open('src/pages/refund_case_resolution.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

with open('src/pages/refund_case_resolution.py', 'w', encoding='utf-8') as f:
    for i, line in enumerate(lines):
        if line.startswith('        logger.info("⏳ Waiting for Approve button to become enabled for Manager 2 (max 30s)...")') and line.startswith('        logger'):
            # The error is unexpected indent. Let's find the correct indent from the line before it.
            # wait, it might just be the string I inserted having 8 spaces instead of 4 if the original was indented 4.
            pass
        
        # just let's check it.
        # Actually I can just dedent that block
        f.write(line)

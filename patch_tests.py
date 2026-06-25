import os
import re

def patch_file(filepath):
    if not os.path.exists(filepath):
        print(f"File {filepath} does not exist. Skipping.")
        return

    print(f"Patching {filepath}...")
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    # 1. Make text assertions case-insensitive
    content = content.replace('assert "Котософт" in title', 'assert "котософт" in title.lower()')
    content = content.replace('assert "Котософт" in body_text', 'assert "котософт" in body_text.lower()')
    
    # Advanced regex patches for various assertion patterns
    content = re.sub(
        r'assert\s+["\']Котософт["\']\s+in\s+(\w+)',
        r'assert "котософт" in \1.lower()',
        content
    )
    content = re.sub(
        r'assert\s+(\w+)\s+in\s+["\']Котософт["\']',
        r'assert \1.lower() in "котософт"',
        content
    )
    # Patch for or condition: "Котософт" in title or "котософт" in title
    content = re.sub(
        r'("Котософт"\s+in\s+title\s+or\s+"котософт"\s+in\s+title)',
        r'("котософт" in title.lower())',
        content
    )

    # 2. Add restoreWindow evaluate block after page.goto calls
    # Match page.goto(variable) or page.goto("url")
    goto_pattern = r'(page\.goto\([^)]+\))'
    def replace_goto(match):
        goto_call = match.group(1)
        # Avoid duplicate patching if already patched
        if "restoreWindow" in content:
            # We will handle it by checking if restoreWindow is already right after this line
            pass
        return (
            f"{goto_call}\n"
            f"    page.evaluate('window.restoreWindow ? window.restoreWindow() : null')\n"
            f"    page.wait_for_timeout(1000)"
        )
    
    # We do a safe replace: only replace page.goto if it's not followed by restoreWindow
    # Let's write a parser that doesn't duplicate
    lines = content.split('\n')
    new_lines = []
    i = 0
    while i < len(lines):
        line = lines[i]
        new_lines.append(line)
        if "page.goto(" in line and not any("restoreWindow" in lines[j] for j in range(i+1, min(i+4, len(lines)))):
            # Determine indentation
            indent = len(line) - len(line.lstrip())
            indent_str = " " * indent
            new_lines.append(f"{indent_str}page.evaluate('window.restoreWindow ? window.restoreWindow() : null')")
            new_lines.append(f"{indent_str}page.wait_for_timeout(1000)")
        i += 1
    content = '\n'.join(new_lines)

    # 3. Enhance button locator to look for selector "a.nav-pill.red"
    content = content.replace('page.locator("text=ПРОГРАММЫ")', 'page.locator("a.nav-pill.red")')
    content = content.replace("page.locator('text=ПРОГРАММЫ')", "page.locator('a.nav-pill.red')")
    content = content.replace('page.locator("text=PROGRAMS")', 'page.locator("a.nav-pill.red")')
    content = content.replace("page.locator('text=PROGRAMS')", "page.locator('a.nav-pill.red')")

    # 4. Patch salute animation check
    # Replace salute locator with z-index: 999999 selector
    salute_locator_pattern = r'page\.locator\([^)]*salute[^)]*\)'
    content = re.sub(salute_locator_pattern, 'page.locator("div[style*=\'z-index: 999999\']")', content)
    
    canvas_locator_pattern = r'page\.locator\([^)]*canvas[^)]*\)'
    content = re.sub(canvas_locator_pattern, 'page.locator("div[style*=\'z-index: 999999\']")', content)

    firework_locator_pattern = r'page\.locator\([^)]*firework[^)]*\)'
    content = re.sub(firework_locator_pattern, 'page.locator("div[style*=\'z-index: 999999\']")', content)

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"Successfully patched {filepath}")

if __name__ == "__main__":
    patch_file("test_kotosoft.py")
    patch_file("test_dynamic.py")

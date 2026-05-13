import os
import re

files = [
    'frontend/components/kpi_cards.py',
    'frontend/components/data_tables.py',
    'pages/01_User_Dashboard.py',
    'pages/02_Analyst_Dashboard.py',
    'pages/03_Admin_Dashboard.py',
    'pages/04_Settings.py',
    'app.py'
]

# This pattern matches:
# st.markdown(
#    f"""...""",
#    unsafe_allow_html=True
# )
# It captures the string literal (including the optional f prefix and quotes)
pattern = re.compile(r'st\.markdown\(\s*(f?"""[\s\S]*?""")\s*,\s*unsafe_allow_html=True\s*\)')

# Another pattern for single quotes just in case
pattern2 = re.compile(r"st\.markdown\(\s*(f?'''[\s\S]*?''')\s*,\s*unsafe_allow_html=True\s*\)")

# Also single line strings with unsafe_allow_html
pattern3 = re.compile(r'st\.markdown\(\s*(f?"[^"]*")\s*,\s*unsafe_allow_html=True\s*\)')
pattern4 = re.compile(r"st\.markdown\(\s*(f?'[^']*')\s*,\s*unsafe_allow_html=True\s*\)")


for path in files:
    if not os.path.exists(path):
        continue
        
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    modified = False
    
    # We only apply textwrap.dedent to the multiline ones (pattern and pattern2)
    if pattern.search(content) or pattern2.search(content):
        if 'import textwrap' not in content:
            content = 'import textwrap\n' + content
            
        content = pattern.sub(r'st.markdown(textwrap.dedent(\1), unsafe_allow_html=True)', content)
        content = pattern2.sub(r'st.markdown(textwrap.dedent(\1), unsafe_allow_html=True)', content)
        modified = True
        
    if modified:
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f'Fixed {path}')

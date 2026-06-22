import glob, os, re
dest_dir = r'r:\Craft\MicroServices Craft\services\admin-service\sysadmin_dashboard\js\pages'
files = glob.glob(os.path.join(dest_dir, '*.js'))
for f in files:
    content = open(f, 'r', encoding='utf-8').read()
    if r'\${' in content:
        content = content.replace(r'\${', '${')
        open(f, 'w', encoding='utf-8').write(content)
print('Done fixing $!')

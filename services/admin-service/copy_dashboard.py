import shutil
import os

src = r"r:\Craft\MicroServices Craft\services\admin-service\dashboard"
dest = r"r:\Craft\MicroServices Craft\services\admin-service\sysadmin_dashboard"

if os.path.exists(dest):
    shutil.rmtree(dest)

shutil.copytree(src, dest)
print("Dashboard copied to sysadmin_dashboard.")

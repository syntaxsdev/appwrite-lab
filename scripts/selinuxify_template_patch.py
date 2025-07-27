from pathlib import Path
import os
from ruamel.yaml import YAML

yaml = YAML()
yaml.preserve_quotes = True

volume_skip = ["/tmp"]

templates_dir = Path(__file__).parent.parent / "appwrite_lab" / "templates"
list_of_templates = [f for f in os.listdir(templates_dir) if f.endswith(".yml")]

changes_made = False

for template in list_of_templates:
    with open(templates_dir / template) as f:
        data = yaml.load(f)
        original_data = yaml.load(f.read())
        f.seek(0)

    for service in data.get("services", {}).values():
        if "volumes" in service:
            new_vols = []
            for v in service["volumes"]:
                # Only process if it's a string (not dict/advanced mount)
                if isinstance(v, str):
                    split = v.split(":")
                    # If any item in split is in volume_skip, skip the volume
                    skip = False
                    for item in split:
                        if item in volume_skip:
                            skip = True
                            break
                        # Skip if item already has SELinux label (:Z or ,Z)
                        if item.endswith("Z"):
                            skip = True
                            break
                    if not skip:
                        v = v + ":Z" if len(split) == 2 else v + ",Z"
                        changes_made = True
                new_vols.append(v)
            service["volumes"] = new_vols

    with open(templates_dir / template, "w") as f:
        yaml.dump(data, f)

if not changes_made:
    print("✅ All templates are already patched.")
else:
    print("✅ Templates updated with SELinux labels.")

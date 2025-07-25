from pathlib import Path
import os
from ruamel.yaml import YAML

yaml = YAML()
yaml.preserve_quotes = True

volume_skip = ["/tmp"]

templates_dir = Path(__file__).parent.parent / "appwrite_lab" / "templates"
list_of_templates = [f for f in os.listdir(templates_dir) if f.endswith(".yml")]
# print(list_of_templates)
for template in list_of_templates:
    with open(templates_dir / template) as f:
        data = yaml.load(f)

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
                    if not skip:
                        v = v + ":Z" if len(split) == 2 else v + ",Z"
                new_vols.append(v)
            service["volumes"] = new_vols

    with open(templates_dir / template, "w") as f:
        yaml.dump(data, f)

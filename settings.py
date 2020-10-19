#!/usr/bin/env python3

import yaml

# with open('settings.yaml') as f:
    
#     list_doc = yaml.load(f, Loader=yaml.FullLoader)
#     #print(data['doe'])

#     # for sense in list_doc:
#     #     if sense["name"] == "sense2":
#     #         sense["value"] = 1234

#     #with open("my_file.yaml", "w") as f:
#     yaml.dump(list_doc, "test.yaml")

data = {"announce":False,
        "card location":"/mnt/path",
        "database location":"/mnt/database/path/name.db"
}

with open('settings.yaml', 'w') as outfile:
    yaml.dump(data, outfile, default_flow_style=False)
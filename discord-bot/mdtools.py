import re

def extract_code_fences(text):
    #regex = r"```[a-z]*\n([\s\S]*?\n)```"
    regex = r"```(.*[\s\S]*?)```"
    matches = re.finditer(regex, text, re.MULTILINE)

    code_fences = []
    for matchNum, match in enumerate(matches, start=1):
        for groupNum in range(0, len(match.groups())):
            groupNum = groupNum + 1
            code_fences.append(match.group(groupNum).strip())
    return code_fences

# if __name__ == "__main__":
#    Do something here
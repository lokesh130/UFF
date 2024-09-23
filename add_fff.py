import sys
import os
import subprocess
import requests
from datetime import datetime

def update_file(file_path, search_text, new_content, is_map=False, is_set=False):
    if not os.path.exists(file_path):
        print(f"File {file_path} does not exist.")
        return
    
    with open(file_path, 'r') as file:
        content = file.read()

    if is_map:
        search_text_index = content.find(search_text)
        if search_text_index == -1:
            print(f"Search text not found in {file_path}.")
            return
        map_start_index = content.find("Map(", search_text_index)
        insert_index = content.find("(", map_start_index) + 1
        updated_content = content[:insert_index] + new_content + content[insert_index:]
    elif is_set:
        search_text_index = content.find(search_text)
        if search_text_index == -1:
            print(f"Search text not found in {file_path}.")
            return
        set_start_index = content.find("Set(", search_text_index)
        insert_index = content.find("(", set_start_index) + 1
        updated_content = content[:insert_index] + "\n " + new_content + content[insert_index:]
    else:
        if search_text in content:
            updated_content = content.replace(search_text, search_text + new_content)
        else:
            print(f"Search text not found in {file_path}.")
            return

    with open(file_path, 'w') as file:
        file.write(updated_content)

    print(f"Updated {file_path} successfully.")

def main(feature_flag_name, description):
    new_ff_enum_entry = f"""
  # {description}
  {feature_flag_name}
"""

    new_ff_case = f"""
  case object {feature_flag_name}
      extends UffInfo(
        "{feature_flag_name}",
        DataType.BOOL,
        "False",
      )
"""

    new_ff_feature_flag_name = f"""
  case object {feature_flag_name}
      extends FeatureFlagName("{feature_flag_name}")
"""

    new_ff_set_entry = f"""
      {feature_flag_name},"""

    new_enum_map_entry = f"""
          FeatureFlagName.{feature_flag_name} ->
            "{description}","""

    # File Paths
    files_to_update = {
        "/Users/Lokesh.Kumar/code/sdmain/polaris/src/rubrik/api-server/documentation/schema/schema-internal.graphql": ("enum FeatureFlagName {", new_ff_enum_entry),
        "/Users/Lokesh.Kumar/code/sdmain/polaris/src/rubrik/api-server/app/models/graphql/UnifiedFeatureFlag.scala": ("object UffInfo extends Enumerator[UffInfo] {", new_ff_case),
        "/Users/Lokesh.Kumar/code/sdmain/polaris/src/rubrik/api-server/app/models/graphql/FeatureFlag.scala": ("object FeatureFlagName extends Enumerator[FeatureFlagName] {", new_ff_feature_flag_name),
        "/Users/Lokesh.Kumar/code/sdmain/polaris/src/rubrik/api-server/app/models/graphql/FeatureFlag.scala#Set": ("def uffFlags: Set[FeatureFlagName] =", new_ff_set_entry, False, True),
        "/Users/Lokesh.Kumar/code/sdmain/polaris/src/rubrik/api-server/app/apps/featureflag/schema/Enums.scala": ("implicit val FeatureFlagNameEnum: EnumType[FeatureFlagName] =", new_enum_map_entry, True, False),
    }

    for file_path, file_info in files_to_update.items():
        is_map = False
        is_set = False
        if len(file_info) == 4:
            search_text, new_content, is_map, is_set = file_info
        else:
            search_text, new_content = file_info

        if "#Set" in file_path:
            file_path = file_path.replace("#Set", "")  # Adjusting for the special case for `uffFlags` set
            search_text = search_text.split("#")[0]
            new_content = f"    {new_content}"  # Adding indentation for set values
        
        update_file(file_path, search_text, new_content, is_map, is_set)

def generate_branch_name():
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    branch_name = f"feature-flag-{timestamp}"
    return branch_name

def create_pr(feature_flag_name, description, base_branch='main'):
    github_token = "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"  # hardcoded GitHub token
    repo_name = "scaledata/sdmain"  # static repository name
    branch_name = generate_branch_name()  # generate unique branch name
    
    # Push changes to a new branch
    subprocess.run(["git", "checkout", "-b", branch_name])
    subprocess.run(["git", "add", "."])
    commit_message = f"Add feature flag {feature_flag_name}"
    subprocess.run(["git", "commit", "-m", commit_message])
    subprocess.run(["git", "push", "--set-upstream", "origin", branch_name])

    # Create a pull request
    # url = f"https://api.github.com/repos/{repo_name}/pulls"
    # headers = {
    #     "Authorization": f"token {github_token}",
    #     "Accept": "application/vnd.github.v3+json"
    # }
    
    # payload = {
    #     "title": f"Add feature flag {feature_flag_name}",
    #     "body": description,
    #     "head": branch_name,
    #     "base": base_branch
    # }

    # response = requests.post(url, json=payload, headers=headers)
    # if response.status_code == 201:
    #     print(f"Pull request created successfully: {response.json()['html_url']}")
    # else:
    #     print(f"Failed to create pull request: {response.text}")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: script.py <FeatureFlagName> <Description>")
        sys.exit(1)

    feature_flag_name = sys.argv[1]
    description = sys.argv[2]

    main(feature_flag_name, description)
    create_pr(feature_flag_name, description)
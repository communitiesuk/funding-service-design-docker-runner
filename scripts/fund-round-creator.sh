#!/bin/bash

set -e  # Exit on errors

# Define directories
FUND_ROUND_DIR="fund-round"
APPS_DIR="apps"
BRANCHES_CREATED=()  # Array to track created branches

print_header() {
    echo -e "\n\e[1;34m$1\e[0m"
}

print_prompt() {
    echo -e -n "\e[1;33m$1\e[0m"
}

print_message() {
    echo -e "\e[1;37m$1\e[0m"
}

print_error() {
    echo -e "\e[1;31m$1\e[0m"
}

print_end() {
    echo -e "\n\e[1;36m$1\e[0m"
}

# Function to cleanup branches
cleanup_branches() {
    echo -e "\n\e[1;31mAn error occurred. Cleaning up created branches...\e[0m"
    for branch_info in "${BRANCHES_CREATED[@]}"; do
        repo_path=$(echo "$branch_info" | cut -d '|' -f 1)
        branch_name=$(echo "$branch_info" | cut -d '|' -f 2)
        echo "Deleting branch $branch_name in $repo_path..."
        cd "$repo_path"
        git checkout main  # Fallback to main/master
        git branch -D "$branch_name" || true  # Force delete branch if it exists
        cd - >/dev/null
    done
}

# Trap to handle script errors
trap cleanup_branches ERR

create_git_branch() {
    local repo_path=$1
    local branch_name=$2

    cd "$repo_path"

    # Check if branch already exists
    if git branch --list $branch_name | grep -q $branch_name; then
        print_message "Branch $branch_name already exists in $repo_path. Deleting existing branch..."
        git checkout main
        git branch -D "$branch_name"
        git checkout -b "$branch_name"
    else
        print_message "Creating and switching to new branch $branch_name in $repo_path..."
        git checkout -b "$branch_name"
    fi

    BRANCHES_CREATED+=("$repo_path|$branch_name")  # Track created branch

    cd - >/dev/null
}

commit_changes() {
    local repo_path=$1
    local commit_message=$2

    cd "$repo_path"

    print_message "Git status:"
    git status -u
    print_message "Git diff:"
    git --no-pager diff
    git add .
    git commit --no-verify -m "$commit_message"

    cd - >/dev/null
}


###############################################################################
#   Main script
###############################################################################

# List all directories inside the fund-round directory
print_header "Available directories in $FUND_ROUND_DIR:"
dirs=()
i=1
for dir in "$FUND_ROUND_DIR"/*; do
    if [[ -d "$dir" ]]; then
        dirs+=("$dir")
        echo "$i) $(basename "$dir")"
        ((i++))
    fi
done

# Prompt the user to select a directory
print_prompt "Select a directory by number: "
read -p "" choice

# Validate the user's choice
if [[ "$choice" -ge 1 && "$choice" -le ${#dirs[@]} ]]; then
    SELECTED_DIR="${dirs[$choice-1]}"
    print_message "Selected directory: $(basename "$SELECTED_DIR")"
else
    print_error "Invalid choice. Exiting."
    exit 1
fi

# Navigate to the fund_store directory
FUND_STORE_DIR="$SELECTED_DIR/fund_store"
if [[ ! -d "$FUND_STORE_DIR" ]]; then
    print_error "Error: fund_store directory not found in $(basename "$SELECTED_DIR")."
    exit 1
fi

print_header "Step 1: Extract and confirm fund and round information"
FUND_STORE_FILE="$SELECTED_DIR/fund_store/round_config.py"
if [[ ! -f "$FUND_STORE_FILE" ]]; then
    print_error "Error: $FUND_STORE_FILE not found!"
    exit 1
fi

# Extract fund and round information from the fund_store file
extracted_data=$(python3 -c "
import sys, json
with open('$FUND_STORE_FILE') as f:
    content = f.read()
    start = content.find('LOADER_CONFIG = {')
    if start == -1:
        sys.exit('LOADER_CONFIG dictionary not found')
    start += len('LOADER_CONFIG = ')
    loader_config = eval(content[start:])
    data = {
        'fund_id': loader_config['fund_config']['id'],
        'fund_short_name': loader_config['fund_config']['short_name'],
        'round_id': loader_config['round_config']['id'],
        'round_short_name': loader_config['round_config']['short_name'],
        'contact_email': loader_config['round_config']['contact_email'],
        'sections': [
            {
                'name': sec['section_name']['en'],
                'form': sec['form_name_json']['en'] if 'form_name_json' in sec else None
            }
            for sec in loader_config['sections_config']
        ]
    }
    print(json.dumps(data))
")

# Parse extracted data
fund_id=$(echo "$extracted_data" | jq -r '.fund_id')
fund_short_name=$(echo "$extracted_data" | jq -r '.fund_short_name')
round_id=$(echo "$extracted_data" | jq -r '.round_id')
round_short_name=$(echo "$extracted_data" | jq -r '.round_short_name')
contact_email=$(echo "$extracted_data" | jq -r '.contact_email')
fund_short_name_uppercase=$(echo "$fund_short_name" | tr 'a-z' 'A-Z')

echo -e "Fund ID: \e[32m$fund_id\e[0m"
echo -e "Fund Short Name: \e[32m$fund_short_name\e[0m"
echo -e "Round ID: \e[32m$round_id\e[0m"
echo -e "Round Short Name: \e[32m$round_short_name\e[0m"
echo -e "Sections:"
echo "$extracted_data" | jq -r '.sections[] | "  - Section Name: \(.name)\n    Form Name: \(.form // "N/A")"'

print_prompt "Is this information correct? (1/0): "
read -p "" confirm

if [[ "$confirm" != "1" ]]; then
    print_error "Exiting script. Please check the LOADER_CONFIG file."
    exit 1
fi

print_prompt "Press [Enter] to continue."
read

print_header "Step 2: Working on 'digital-form-builder-adapter'"
print_message "Create new branch if needed"
create_git_branch \
    "$APPS_DIR/digital-form-builder-adapter" \
    "run-${fund_short_name,,}-${round_short_name,,}"

print_message "Copy form_runner files to 'digital-form-builder-adapter'"
FORM_JSON_DIR="$APPS_DIR/digital-form-builder-adapter/fsd_config/form_jsons"
FORM_DIR_NAME="${fund_short_name,,}_${round_short_name,,}"

print_message "Copying form_runner files to $FORM_JSON_DIR/$FORM_DIR_NAME"
FORM_DEST_DIR="$FORM_JSON_DIR/$FORM_DIR_NAME"
mkdir -p "$FORM_DEST_DIR"
cp -r "$SELECTED_DIR/form_runner/"* "$FORM_DEST_DIR/"

print_message "Commit changes"
commit_changes \
    "$APPS_DIR/digital-form-builder-adapter" \
    "Adding ${fund_short_name}-${round_short_name} forms"

print_prompt "Press [Enter] to continue."
read

print_header "Step 3: Working on 'funding-service-design-frontend'"
print_message "Create new branch if needed"
create_git_branch \
    "$APPS_DIR/funding-service-design-frontend" \
    "run-${fund_short_name,,}-${round_short_name,,}"

print_message "Copy html files to 'funding-service-design-frontend'"
TEMPLATES_DIR="$APPS_DIR/funding-service-design-frontend/app/templates/all_questions/en"
cp -r "$SELECTED_DIR/html/"* "$TEMPLATES_DIR/"

print_message "Commit changes"
commit_changes \
    "$APPS_DIR/funding-service-design-frontend" \
    "Adding ${fund_short_name}-${round_short_name} template"

print_prompt "Press [Enter] to continue."
read

print_header "Step 4: Working on 'funding-service-pre-award-stores':"
print_message "Create new branch if needed"
create_git_branch \
    "$APPS_DIR/funding-service-pre-award-stores" \
    "run-${fund_short_name,,}-${round_short_name,,}"

print_message "Copy fund_store file to 'funding-service-pre-award-stores':"
FUND_STORE_DEST_DIR="$APPS_DIR/funding-service-pre-award-stores/fund_store/config/fund_loader_config/FAB"

print_message "Copying form_runner files to $FUND_STORE_DEST_DIR"
mkdir -p "$FUND_STORE_DEST_DIR"
FUND_STORE_FILE_DEST="$FUND_STORE_DEST_DIR/${fund_short_name,,}_${round_short_name,,}.py"  # Lowercase
cp "$FUND_STORE_FILE" "$FUND_STORE_FILE_DEST"

ASSESS_STORE_CONFIG_FILE="apps/funding-service-pre-award-stores/assessment_store/config/mappings/assessment_mapping_fund_round.py"
echo "Editing  $ASSESS_STORE_CONFIG_FILE"

unscored_sections="[]"
if [[ -f "$SELECTED_DIR/mapping/unscored_sections.py" ]]; then
    print_message "unscored_sections file found"
    unscored_sections=$(cat "$SELECTED_DIR/mapping/unscored_sections.py")
    unscored_sections=$(printf '%s' "$unscored_sections" | sed '1s/^//; 2,$s/^/        /; s/[\/&]/\\&/g; s/"/\\"/g; s/$/\\/')
else
    print_message "No unscored_sections"
fi

scored_sections="[]"
if [[ -f "$SELECTED_DIR/mapping/scored_sections.py" ]]; then
    print_message "scored_sections file found"
    scored_sections=$(cat "$SELECTED_DIR/mapping/scored_sections.py")
    scored_sections=$(printf '%s' "$scored_sections" | sed '1s/^//; 2,$s/^/        /; s/[\/&]/\\&/g; s/"/\\"/g; s/$/\\/')
else
    print_message "No scored_sections"
fi

sed -i "/fund_round_to_assessment_mapping = {/a \\
    \"$fund_id:$round_id\": {\\
        \"schema_id\": \"${fund_short_name}_${round_short_name}_assessment\",\\
        \"unscored_sections\": ${unscored_sections},\\
        \"scored_criteria\": ${scored_sections},\\
    }," "$ASSESS_STORE_CONFIG_FILE"

sed -i "/fund_round_data_key_mappings = {/a \\
    \"${fund_short_name}${round_short_name}\": {\\
        \"location\": None,\\
        \"asset_type\": None,\\
        \"funding_one\": None,\\
        \"funding_two\": None,\\
    }," "$ASSESS_STORE_CONFIG_FILE"

sed -i "/fund_round_mapping_config = {/a \\
    \"${fund_short_name}${round_short_name}\": {\\
        \"fund_id\": \"$fund_id\",\\
        \"round_id\": \"$round_id\",\\
        \"type_of_application\": \"$fund_short_name\",\\
    }," "$ASSESS_STORE_CONFIG_FILE"

print_message "Commit changes"
commit_changes \
    "$APPS_DIR/funding-service-pre-award-stores" \
    "Adding ${fund_short_name}-${round_short_name} config"

print_prompt "Press [Enter] to continue."
read

print_header "Step 5: Working on 'funding-service-design-assessment':"
print_message "Create new branch if needed"
create_git_branch \
    "$APPS_DIR/funding-service-design-assessment" \
    "run-${fund_short_name,,}-${round_short_name,,}"

ASSESS_CONFIG_FILE="apps/funding-service-design-assessment/config/envs/development.py"
echo "Editing  $ASSESS_CONFIG_FILE"
sed -i "/\"roles\": \[/a \\
            \"${fund_short_name_uppercase}_LEAD_ASSESSOR\",\\" "$ASSESS_CONFIG_FILE"
sed -i "/\"roles\": \[/a \\
            \"${fund_short_name_uppercase}_ASSESSOR\",\\" "$ASSESS_CONFIG_FILE"
sed -i "/\"highest_role_map\": {/a \\
            \"${fund_short_name_uppercase}\": \"DEBUG_USER_ROLE\",\\" "$ASSESS_CONFIG_FILE"

print_message "Commit changes"
commit_changes \
    "$APPS_DIR/funding-service-design-assessment" \
    "Adding ${fund_short_name}-${round_short_name} config"

print_prompt "Press [Enter] to continue."
read

print_header "Step 6: Working on 'funding-service-design-notification':"
print_message "Create new branch if needed"
create_git_branch \
    "$APPS_DIR/funding-service-design-notification" \
    "run-${fund_short_name,,}-${round_short_name,,}"

NOTIFICATION_CONFIG_FILE="apps/funding-service-design-notification/config/envs/default.py"
echo "Editing  $NOTIFICATION_CONFIG_FILE"

template_id="6441da8a-1a42-4fe1-ad05-b7fb5f46a761"
print_prompt "Provide a template id [$template_id]: "
read -p "" choice

if [[ -z "$choice" ]]; then
    print_message "No input provided, using default: $template_id"
else
    template_id=$choice
fi

email_id="10668b8d-9472-4ce8-ae07-4fcc7bf93a9d"
print_prompt "Provide an email id [$email_id]: "
read -p "" choice

if [[ -z "$choice" ]]; then
    print_message "No input provided, using default: $email_id"
else
    email_id=$choice
fi

sed -i "/APPLICATION_RECORD_TEMPLATE_ID = {/a \\
        \"${fund_id}\": {\\
            \"fund_name\": \"${fund_short_name_uppercase}\",\\
            \"template_id\": {\\
                \"en\": \"$template_id\",\\
                \"cy\": \"\"\\
            }\\
        }," "$NOTIFICATION_CONFIG_FILE"
sed -i "/REPLY_TO_EMAILS_WITH_NOTIFY_ID = {/a \\
        \"${contact_email}\": \"$email_id\",\\" "$NOTIFICATION_CONFIG_FILE"

print_message "Commit changes"
commit_changes \
    "$APPS_DIR/funding-service-design-notification" \
    "Adding ${fund_short_name}-${round_short_name} config"

print_prompt "Press [Enter] to continue."
read

# print_header "Step 8: Seed fund on 'make up':"
# docker exec funding-service-pre-award-stores-1 python -m scripts.fund_round_loaders.load_fund_round_from_fab --fund_short_code $fund_short_name

print_end "All steps completed successfully!"

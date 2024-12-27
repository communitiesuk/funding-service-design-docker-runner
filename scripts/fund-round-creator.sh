#!/bin/bash

set -e  # Exit on errors

print_header() {
    echo -e "\n\033[1;34m$1\033[0m"
}

print_prompt() {
    echo -e -n "\033[1;33m$1\033[0m"
}

print_message() {
    echo -e "\033[1;37m$1\033[0m"
}

print_error() {
    echo -e "\033[1;31m$1\033[0m"
}

create_git_branch() {
    print_message "Create new branch if needed"
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
    print_message "Commit changes"
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

# Function to select Fund Round directory
select_directory() {
    local dirs=()
    local i=1

    # List all directories inside the fund-round directory
    echo "Available directories in $1:" >&2
    for dir in "$1"/*; do
        if [[ -d "$dir" ]]; then
            dirs+=("$dir")
            echo "$i) $(basename "$dir")" >&2
            ((i++))
        fi
    done

    # Prompt the user to select a directory
    print_prompt "Select a directory by number: " >&2
    read -p "" choice

    # Validate the user's choice
    if [[ "$choice" -lt 1 || "$choice" -gt ${#dirs[@]} ]]; then
        print_error "Invalid choice. Exiting." >&2
        exit 1
    fi

    # Return the selected directory
    echo "$(basename ${dirs[$choice-1]})"
}

#######################################
#   Main script
#######################################

FUND_ROUND_DIR="fund-round"
APPS_DIR="apps"
BRANCHES_CREATED=()  # Array to track created branches

print_header "Step 0: Select Fund Round directory"
FUND_ROUND=$(select_directory $FUND_ROUND_DIR)
print_message "Selected directory: $FUND_ROUND"

#######################################
#   Step 1: Extract and confirm fund and round information
#######################################

print_header "Step 1: Extract and confirm fund and round information"
FUND_STORE_DIR="$FUND_ROUND_DIR/$FUND_ROUND/fund_store"
FUND_STORE_FILE=$(find $FUND_STORE_DIR -maxdepth 1 -type f -print -quit)
print_message "fund_store file: $FUND_STORE_FILE"

echo "Format fund_store file"
uv tool run ruff format $FUND_STORE_DIR

FUND_ID=$(sed -n 's/.*"fund_id": *"\([^"]*\)".*/\1/p' "$FUND_STORE_FILE")
FUND_SHORT_NAME=$(sed -n 's/.*"short_name": *"\([^"]*\)".*/\1/p' "$FUND_STORE_FILE" | head -n 1)
ROUND_ID=$(sed -n 's/.*"id": *"\([^"]*\)".*/\1/p' "$FUND_STORE_FILE" | tail -n 1)
ROUND_SHORT_NAME=$(sed -n 's/.*"short_name": *"\([^"]*\)".*/\1/p' "$FUND_STORE_FILE" | tail -n 1)
CONTACT_EMAIL=$(sed -n 's/.*"contact_email": *"\([^"]*\)".*/\1/p' "$FUND_STORE_FILE")
FUND_SHORT_NAME_LOWERCASE=$(echo "$FUND_SHORT_NAME" | tr 'A-Z' 'a-z')
ROUND_SHORT_NAME_LOWERCASE=$(echo "$ROUND_SHORT_NAME" | tr 'A-Z' 'a-z')

echo -e "Fund ID: \033[32m$FUND_ID\033[0m"
echo -e "Fund Short Name: \033[32m$FUND_SHORT_NAME\033[0m"
echo -e "Round ID: \033[32m$ROUND_ID\033[0m"
echo -e "Round Short Name: \033[32m$ROUND_SHORT_NAME\033[0m"
echo -e "Contact email: \033[32m$CONTACT_EMAIL\033[0m"

print_prompt "Is this information correct? (1/0): "
read -p "" confirm

if [[ "$confirm" != "1" ]]; then
    print_error "Exiting script. Please check LOADER_CONFIG."
    exit 1
fi

print_prompt "Press [Enter] to continue."
read

#######################################
#   Step 2: Working on 'digital-form-builder-adapter'
#######################################

print_header "Step 2: Working on 'digital-form-builder-adapter'"
FORM_JSON_DIR="$APPS_DIR/digital-form-builder-adapter/fsd_config/form_jsons"
FORM_DEST_DIR="$FORM_JSON_DIR/${FUND_SHORT_NAME_LOWERCASE}_${ROUND_SHORT_NAME_LOWERCASE}"

create_git_branch \
    "$APPS_DIR/digital-form-builder-adapter" \
    "run-${FUND_SHORT_NAME_LOWERCASE}-${ROUND_SHORT_NAME_LOWERCASE}"

print_message "Copy form_runner files to 'digital-form-builder-adapter'"
print_message "Copying form_runner files to $FORM_JSON_DIR/${FUND_SHORT_NAME_LOWERCASE}_${ROUND_SHORT_NAME_LOWERCASE}"
mkdir -p "$FORM_DEST_DIR"
cp -r "$FUND_ROUND_DIR/$FUND_ROUND/form_runner/"* "$FORM_DEST_DIR/"

commit_changes  \
    "$APPS_DIR/digital-form-builder-adapter" \
    "Adding ${FUND_SHORT_NAME_LOWERCASE}-${ROUND_SHORT_NAME_LOWERCASE} forms"

print_prompt "Press [Enter] to continue."
read

#######################################
#   Step 3: Working on 'funding-service-pre-award-frontend'
#######################################

print_header "Step 3: Working on 'funding-service-pre-award-frontend'"
TEMPLATES_DIR="$APPS_DIR/funding-service-pre-award-frontend/apply/templates/apply/all_questions/en"
ASSESS_CONFIG_FILE="$APPS_DIR/funding-service-pre-award-frontend/config/envs/development.py"

create_git_branch \
    "$APPS_DIR/funding-service-pre-award-frontend" \
    "run-$FUND_SHORT_NAME_LOWERCASE-$ROUND_SHORT_NAME_LOWERCASE"

print_message "Clean up html file of empty html classes 'funding-service-pre-award-frontend'"
for file in "$FUND_ROUND_DIR/$FUND_ROUND/html"/*; do
    if  [[ "$OSTYPE" == "linux-gnu" ]]; then
        sed -i 's/ <li class="">/<li>/g' $file
    else
        sed -i '' -e 's/ <li class="">/<li>/g' $file
    fi
done

print_message "Copy html files to 'funding-service-pre-award-frontend'"
cp -r "$FUND_ROUND_DIR/$FUND_ROUND/html/"* "$TEMPLATES_DIR/"

commit_changes \
    "$APPS_DIR/funding-service-pre-award-frontend" \
    "Adding ${FUND_SHORT_NAME_LOWERCASE-$ROUND_SHORT_NAME_LOWERCASE} template"

print_prompt "Is it a new Fund? (1/0): "
read -p "" confirm

if [[ "$confirm" == "1" ]]; then
    echo "Editing  $ASSESS_CONFIG_FILE"

    if [[ "$OSTYPE" == "linux-gnu" ]]; then
        sed -i'' -e "/\"roles\": \[/a \\
            \"${FUND_SHORT_NAME}_LEAD_ASSESSOR\",\\" "$ASSESS_CONFIG_FILE"
        sed -i'' -e "/\"roles\": \[/a \\
            \"${FUND_SHORT_NAME}_ASSESSOR\",\\" "$ASSESS_CONFIG_FILE"
        sed -i'' -e "/\"roles\": \[/a \\
            \"${FUND_SHORT_NAME}_COMMENTER\",\\" "$ASSESS_CONFIG_FILE"
        sed -i'' -e "/\"highest_role_map\": {/a \\
            \"${FUND_SHORT_NAME}\": DEBUG_USER_ROLE,\\" "$ASSESS_CONFIG_FILE"
    else
        sed -i '' -e "/\"roles\": \[/a \\
            \"${FUND_SHORT_NAME}_LEAD_ASSESSOR\",\\" "$ASSESS_CONFIG_FILE"
        sed -i '' -e "/\"roles\": \[/a \\
            \"${FUND_SHORT_NAME}_ASSESSOR\",\\" "$ASSESS_CONFIG_FILE"
        sed -i '' -e "/\"roles\": \[/a \\
            \"${FUND_SHORT_NAME}_COMMENTER\",\\" "$ASSESS_CONFIG_FILE"
        sed -i '' -e "/\"highest_role_map\": {/a \\
            \"${FUND_SHORT_NAME}\": DEBUG_USER_ROLE,\\" "$ASSESS_CONFIG_FILE"
    fi

    commit_changes \
        "$APPS_DIR/funding-service-pre-award-frontend" \
        "Adding ${FUND_SHORT_NAME_LOWERCASE}-${ROUND_SHORT_NAME_LOWERCASE} config"
fi

print_prompt "Press [Enter] to continue."
read

#######################################
#   Step 4: Working on 'funding-service-pre-award'
#######################################

print_header "Step 4: Working on 'funding-service-pre-award':"
FUND_STORE_DEST_DIR="$APPS_DIR/funding-service-pre-award/fund_store/config/fund_loader_config/FAB"
FUND_STORE_FILE_DEST="$FUND_STORE_DEST_DIR/${FUND_SHORT_NAME_LOWERCASE}_${ROUND_SHORT_NAME_LOWERCASE}.py"
ASSESS_STORE_CONFIG_FILE="apps/funding-service-pre-award/assessment_store/config/mappings/assessment_mapping_fund_round.py"

create_git_branch \
    "$APPS_DIR/funding-service-pre-award" \
    "run-$FUND_SHORT_NAME_LOWERCASE-$ROUND_SHORT_NAME_LOWERCASE"

print_message "Copying form_runner files to $FUND_STORE_DEST_DIR"
mkdir -p "$FUND_STORE_DEST_DIR"
cp "$FUND_STORE_FILE" "$FUND_STORE_FILE_DEST"

echo "Editing  $ASSESS_STORE_CONFIG_FILE"

echo "Format assessment_store files"
uv tool run ruff format "$FUND_ROUND_DIR/$FUND_ROUND/assessment_store"

unscored_sections="[]"
if [[ -f "$FUND_ROUND_DIR/$FUND_ROUND/assessment_store/unscored.py" ]]; then
    print_message "unscored_sections file found"
    unscored_sections=$(cat "$FUND_ROUND_DIR/$FUND_ROUND/assessment_store/unscored.py")
    unscored_sections=$(printf '%s' "$unscored_sections" | sed '1s/^//; 2,$s/^/        /; s/[\/&]/\\&/g; s/"/\\"/g; s/$/\\/')
else
    print_message "No unscored_sections"
fi

scored_sections="[]"
if [[ -f "$FUND_ROUND_DIR/$FUND_ROUND/assessment_store/scored.py" ]]; then
    print_message "scored_sections file found"
    scored_sections=$(cat "$FUND_ROUND_DIR/$FUND_ROUND/assessment_store/scored.py")
    scored_sections=$(printf '%s' "$scored_sections" | sed '1s/^//; 2,$s/^/        /; s/[\/&]/\\&/g; s/"/\\"/g; s/$/\\/')
else
    print_message "No scored_sections"
fi

if [[ "$OSTYPE" == "linux-gnu" ]]; then
    sed -i'' -e "/fund_round_to_assessment_mapping = {/a \\
    \"$FUND_ID:$ROUND_ID\": {\\
        \"schema_id\": \"${FUND_SHORT_NAME_LOWERCASE}_${ROUND_SHORT_NAME_LOWERCASE}_assessment\",\\
        \"unscored_sections\": ${unscored_sections},\\
        \"scored_criteria\": ${scored_sections},\\
    }," "$ASSESS_STORE_CONFIG_FILE"

    sed -i'' -e "/fund_round_data_key_mappings = {/a \\
    \"${FUND_SHORT_NAME}${ROUND_SHORT_NAME}\": {\\
        \"location\": None,\\
        \"asset_type\": None,\\
        \"funding_one\": None,\\
        \"funding_two\": None,\\
    }," "$ASSESS_STORE_CONFIG_FILE"

    sed -i'' -e "/fund_round_mapping_config = {/a \\
    \"${FUND_SHORT_NAME}${ROUND_SHORT_NAME}\": {\\
        \"fund_id\": \"$FUND_ID\",\\
        \"round_id\": \"$ROUND_ID\",\\
        \"type_of_application\": \"$FUND_SHORT_NAME\",\\
    }," "$ASSESS_STORE_CONFIG_FILE"
else
    sed -i '' -e "/fund_round_to_assessment_mapping = {/a \\
    \"$FUND_ID:$ROUND_ID\": {\\
        \"schema_id\": \"${FUND_SHORT_NAME_LOWERCASE}_${ROUND_SHORT_NAME_LOWERCASE}_assessment\",\\
        \"unscored_sections\": ${unscored_sections},\\
        \"scored_criteria\": ${scored_sections},\\
    }," "$ASSESS_STORE_CONFIG_FILE"

    sed -i '' -e "/fund_round_data_key_mappings = {/a \\
    \"${FUND_SHORT_NAME}${ROUND_SHORT_NAME}\": {\\
        \"location\": None,\\
        \"asset_type\": None,\\
        \"funding_one\": None,\\
        \"funding_two\": None,\\
    }," "$ASSESS_STORE_CONFIG_FILE"

    sed -i '' -e "/fund_round_mapping_config = {/a \\
    \"${FUND_SHORT_NAME}${ROUND_SHORT_NAME}\": {\\
        \"fund_id\": \"$FUND_ID\",\\
        \"round_id\": \"$ROUND_ID\",\\
        \"type_of_application\": \"$FUND_SHORT_NAME\",\\
    }," "$ASSESS_STORE_CONFIG_FILE"
fi


print_message "Commit changes"
commit_changes \
    "$APPS_DIR/funding-service-pre-award" \
    "Adding ${FUND_SHORT_NAME_LOWERCASE}-${ROUND_SHORT_NAME_LOWERCASE} config"

print_prompt "Press [Enter] to continue."
read

print_header "Step 6: Working on 'funding-service-design-notification':"
create_git_branch \
    "$APPS_DIR/funding-service-design-notification" \
    "run-$FUND_SHORT_NAME_LOWERCASE-$ROUND_SHORT_NAME_LOWERCASE"

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

contact_email_exists="false"
if ! grep $CONTACT_EMAIL $NOTIFICATION_CONFIG_FILE; then
    if [[ "$OSTYPE" == "linux-gnu" ]]; then
        sed -i'' -e "/REPLY_TO_EMAILS_WITH_NOTIFY_ID = {/a \\
        \"${CONTACT_EMAIL}\": \"$email_id\",\\" "$NOTIFICATION_CONFIG_FILE"
    else
        sed -i '' -e "/REPLY_TO_EMAILS_WITH_NOTIFY_ID = {/a \\
        \"${CONTACT_EMAIL}\": \"$email_id\",\\" "$NOTIFICATION_CONFIG_FILE"
    fi

    print_message "Commit changes"
    commit_changes \
        "$APPS_DIR/funding-service-design-notification" \
        "Adding ${FUND_SHORT_NAME_LOWERCASE}-${ROUND_SHORT_NAME_LOWERCASE} config"
fi


print_prompt "Press [Enter] to continue."
read

echo -e "\n\033[1;36mAll steps completed successfully!\033[0m"

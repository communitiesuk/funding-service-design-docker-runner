#!/bin/bash
reset_venv=false
install_pre_commit=false
build_static_files=false

repo_root=$(dirname $(dirname $(realpath $0)))
workspace_dir="${repo_root}/apps"
declare -a repos=("funding-service-design-fund-application-builder" "funding-service-design-authenticator" "funding-service-design-assessment" "funding-service-design-assessment-store" "funding-service-design-account-store" "funding-service-design-application-store" "funding-service-design-frontend" "funding-service-design-fund-store" "funding-service-design-notification" "funding-service-design-post-award-data-store")

while getopts 'vps' OPTION; do
    case "$OPTION" in
        v)
            echo Will reset all virtual environments
            reset_venv=true
            ;;
        p)
            echo Will install pre-commit hooks in the repo
            install_pre_commit=true
            ;;
        s)
            echo "Will build static files(only for frontend, assessment & authenticator repos)"
            build_static_files=true
            ;;
        ?)
            echo "script usage: $(basename §$0) [-v -p -s ]"
            exit 1
    esac
done
shift "$(($OPTIND -1))"

echo ============================================
echo Workspace dir: $workspace_dir
echo Reset virtual environments: $reset_venv
echo Install pre-commit hooks: $install_pre_commit
echo Build static files: $build_static_files
echo ============================================

echo Creating virtual environments

for repo in "${repos[@]}"
do
    echo -------------------------------------------------------------------------
    cd $workspace_dir/$repo
    echo $(pwd)

    if [ "$reset_venv" = true ] ; then
        echo Removing the Virtual environment for $repo ...
        rm -rf .venv
    fi

    uv sync

    if [ "$install_pre_commit" = true ] ; then
        echo Installing the pre-commit hooks...
        uv run pre-commit install
    fi

    if [ "$build_static_files" = true ] ; then
        static_repos_array=("funding-service-design-fund-application-builder" "funding-service-design-authenticator" "funding-service-design-assessment" "funding-service-design-frontend" "funding-service-design-post-award-data-store")
        if [[ " ${static_repos_array[*]} " =~ " $repo " ]]; then
            echo Building the static files...
            export FLASK_ENV=development
            uv run python build.py
        fi
    fi

    echo -------------------------------------------------------------------------
done

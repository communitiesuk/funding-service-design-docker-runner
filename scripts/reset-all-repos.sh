#!/bin/bash
wipe_postgres=false
reset_to_main=false
while getopts 'wma:' OPTION; do
    case "$OPTION" in
        w)
            wipe_postgres=true
            ;;
        m)
            echo Will reset all repos to main
            reset_to_main=true
            ;;
        ?)
            echo "script usage: $(basename §$0) [-w -m ] workspace_dir"
            exit 1
    esac
done
shift "$(($OPTIND -1))"

workspace_dir=$1
fsd="funding-service-design"

echo ============================================
echo Workspace dir: $workspace_dir
echo Wipe postgres: $wipe_postgres
echo Reset all to main: $reset_to_main
echo ============================================

if [ "$wipe_postgres" = true ] ; then
    echo Wiping postgres
    echo ...not implemented yet...
    echo docker compose down
    echo docker rm postgres --force
fi

if [ "$reset_to_main" = true ] ; then
    echo Resetting all repos to main

    cd $workspace_dir

    declare -a repos=("authenticator" "assessment" "assessment-store" "account-store" 
                    "application-store" "audit" "frontend" "fund-store" "notification" "digital-form-builder")

    for repo in "${repos[@]}"
    do
    echo -------------------------------------------------------------------------
    echo ========= Resetting "$repo" =======
    cd $workspace_dir/$fsd-$repo
    git status
    git checkout main
    git pull
    echo -------------------------------------------------------------------------
    done
fi

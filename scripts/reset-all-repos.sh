#!/bin/bash
wipe_postgres=false
reset_to_main=false
fresh_clone=false
git_log=false
while getopts 'wmfal:' OPTION; do
    case "$OPTION" in
        w)
            wipe_postgres=true
            ;;
        m)
            echo Will reset all repos to main
            reset_to_main=true
            ;;
        f)
            echo """Will do a git clone of ("authenticator" "assessment" "assessment-store" "account-store" "application-store" "frontend" "fund-store" "notification" "digital-form-builder")"""
            fresh_clone=true
            wipe_postgres=false
            reset_to_main=false
            ;;
        l)
            echo "Running git log for all repos"
            git_log=true
            ;;
        ?)
            echo "script usage: $(basename §$0) [-w -m -f -l] workspace_dir"
            exit 1
    esac
done
shift "$(($OPTIND -1))"

workspace_dir=${1:-$(dirname $(pwd))}
fsd="funding-service-design"

echo ============================================
echo Workspace dir: $workspace_dir
echo Wipe postgres: $wipe_postgres
echo Reset all to main: $reset_to_main
echo Fresh clone repos: $fresh_clone
echo ============================================

if [ "$fresh_clone" = true ] ; then

    declare -a repos=("authenticator" "assessment" "assessment-store" "account-store"
                    "application-store" "frontend" "fund-store" "notification")

    git_remote_prefix=https://github.com/communitiesuk/funding-service-design-

    for repo in "${repos[@]}"
    do
    echo -------------------------------------------------------------------------
    echo ========= Cloning repo "$repo" =======
    cd $workspace_dir
    repo_path="${git_remote_prefix}${repo}.git"
    git clone ${repo_path}
    echo -------------------------------------------------------------------------
    done

    echo -------------------------------------------------------------------------
    echo ========= Cloning repo digital-form-builder =======
    cd $workspace_dir
    git clone https://github.com/communitiesuk/digital-form-builder.git
    echo -------------------------------------------------------------------------
fi

if [ "$wipe_postgres" = true ] ; then
    echo Wiping postgres
    echo ...not implemented yet...
    echo docker compose down
    echo docker rm postgres --force
fi

declare -a repos=("authenticator" "assessment" "assessment-store" "account-store"
                "application-store" "frontend" "fund-store" "notification")

if [ "$reset_to_main" = true ] ; then
    echo Resetting all repos to main

    cd $workspace_dir


    for repo in "${repos[@]}"
    do
    echo -------------------------------------------------------------------------
    echo ========= Resetting "$repo" =======
    cd $workspace_dir/$fsd-$repo
    git status
    git checkout main
    git pull
    done

    echo ========= Resetting "digital-form-builder" =======
    cd $workspace_dir/digital-form-builder
    git status
    git checkout main
    git pull
    echo -------------------------------------------------------------------------
fi
if [ "$git_log" = true ] ; then
    echo Running git log

    cd $workspace_dir


    for repo in "${repos[@]}"
    do
    echo -------------------------------------------------------------------------
    cd $workspace_dir/$fsd-$repo
    echo $repo
    git log -n 1 --format=format:%H
    done
    echo -------------------------------------------------------------------------
    cd $workspace_dir/digital-form-builder
    echo digital-form-builder
    git log -n 1 --format=format:%H
    echo -------------------------------------------------------------------------
    
fi

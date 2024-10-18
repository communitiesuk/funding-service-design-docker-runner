#!/bin/bash

wipe_postgres=false
reset_to_main=false
fresh_clone=false
git_log=false
repo_root=$(dirname $(dirname $(realpath $0)))
apps_dir="${repo_root}/apps"
declare -a repos=("funding-service-design-authenticator" "funding-service-design-assessment" "funding-service-design-assessment-store" "funding-service-design-account-store" "funding-service-design-application-store" "funding-service-design-frontend" "funding-service-design-fund-store" "funding-service-design-notification" "digital-form-builder-adapter")

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
            echo -e "Will do a git clone of:"
            printf '* %s\n' "${repos[@]}"
            fresh_clone=true
            wipe_postgres=false
            reset_to_main=false
            ;;
        l)
            echo "Running git log for all repos"
            git_log=true
            ;;
        ?)
            echo "script usage: $(basename §$0) [-w -m -f -l]"
            exit 1
    esac
done
shift "$(($OPTIND -1))"

echo ============================================
echo Wipe postgres: $wipe_postgres
echo Reset all to main: $reset_to_main
echo Fresh clone repos: $fresh_clone
echo ============================================

if [ "$fresh_clone" = true ] ; then

    git_remote_prefix=https://github.com/communitiesuk/

    for repo in "${repos[@]}"
    do
    echo -------------------------------------------------------------------------
    echo ========= Cloning repo "$repo" =======
    repo_path="${git_remote_prefix}${repo}.git"
    git clone ${repo_path} ${apps_dir}/${repo}
    echo -------------------------------------------------------------------------
    done
fi

if [ "$wipe_postgres" = true ] ; then
    echo Wiping postgres
    echo ...not implemented yet...
    echo docker compose down
    echo docker rm postgres --force
fi

if [ "$reset_to_main" = true ] ; then
    echo Resetting all repos to main

    for repo in "${repos[@]}"
    do
    echo -------------------------------------------------------------------------
    echo ========= Resetting "$repo" =======
    cd ${apps_dir}/$repo
    git status
    git checkout main
    git pull
    done

    echo -------------------------------------------------------------------------
    cd ${repo_root}
fi

if [ "$git_log" = true ] ; then
    echo Running git log

    for repo in "${repos[@]}"
    do
    echo -------------------------------------------------------------------------
    cd ${apps_dir}/$repo
    echo $repo
    git log -n 1 --format=format:%H
    done
    echo -------------------------------------------------------------------------
    cd ${repo_root}
fi

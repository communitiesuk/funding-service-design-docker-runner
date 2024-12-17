#!/bin/bash

wipe_postgres=false
reset_to_main=false
fresh_clone=false
git_log=false
repo_root=$(dirname $(dirname $(realpath $0)))
apps_dir="${repo_root}/apps"
declare -a repos=("funding-service-design-fund-application-builder" "funding-service-pre-award-stores" "funding-service-pre-award-frontend" "funding-service-design-notification" "digital-form-builder-adapter" "funding-service-design-post-award-data-store" "funding-service-design-utils" "funding-service-design-workflows")

show_help() {
    echo "Usage: $(basename $0) [-f] [-m] [-l] [-h]"
    echo
    echo "Options:"
    echo "  -f    Fresh clone of all repositories"
    echo "  -m    Reset all repositories to main branch"
    echo "  -l    Show latest commit hash for all repositories"
    echo "  -h    Show this help message"
    echo
    echo "Repositories that will be managed:"
    printf '* %s\n' "${repos[@]}"
}

while getopts 'fmlh' OPTION; do
    case "$OPTION" in
        f)
            echo -e "Will do a git clone of:"
            printf '* %s\n' "${repos[@]}"
            fresh_clone=true
            ;;
        m)
            echo Will reset all repos to main
            reset_to_main=true
            ;;
        l)
            echo "Showing latest commit hash for all repos"
            git_log=true
            ;;
        h)
            show_help
            exit 0
            ;;
        ?)
            show_help
            exit 1
    esac
done
shift "$(($OPTIND -1))"

# Show help if no options are provided
if [ $OPTIND -eq 1 ]; then
    show_help
    exit 1
fi

echo ============================================
echo Fresh clone repos: $fresh_clone
echo Reset all to main: $reset_to_main
echo Show latest commit: $git_log
echo ============================================

if [ "$fresh_clone" = true ] ; then

    git_remote_prefix=git@github.com:communitiesuk/

    for repo in "${repos[@]}"
    do
    echo -------------------------------------------------------------------------
    echo ========= Cloning repo "$repo" =======
    repo_path="${git_remote_prefix}${repo}.git"
    git clone ${repo_path} ${apps_dir}/${repo}
    echo -------------------------------------------------------------------------
    done
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
    echo -e "Running git log\n"

    outfile=$(mktemp)

    echo $'Repository\tBranch name\tCommit hash' > ${outfile}

    for repo in "${repos[@]}"
    do
    cd ${apps_dir}/$repo
    echo -e "$repo\t$(git rev-parse --abbrev-ref HEAD)\t$(git rev-parse --short=8 HEAD)" >> ${outfile}
    done
    cd ${repo_root}

    cat ${outfile} | sort | column -t -s $'\t'
fi

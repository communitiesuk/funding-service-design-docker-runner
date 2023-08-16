#!/bin/bash
reset_venv=false
install_pre_commit=false
build_static_files=false

while getopts 'vps:' OPTION; do
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
            echo "script usage: $(basename §$0) [-v -p -s ] workspace_dir"
            exit 1
    esac
done
shift "$(($OPTIND -1))"

workspace_dir=${1:-$(dirname $(pwd))}
fsd="funding-service-design"

echo ============================================
echo Workspace dir: $workspace_dir
echo Reset virtual environments: $reset_venv
echo Install pre-commit hooks: $install_pre_commit
echo Build static files: $build_static_files
echo ============================================

echo Creating virtual environments

cd $workspace_dir

declare -a repos=("authenticator" "assessment" "assessment-store" "account-store"
                "application-store" "frontend" "fund-store" "notification")

# declare -a repos=("authenticator")

for repo in "${repos[@]}"
do
echo -------------------------------------------------------------------------
cd $workspace_dir/$fsd-$repo
echo $(pwd)

if [ "$reset_venv" = true ] ; then
    echo Removing the Virtual environment for $fsd-$repo ...
    rm -rf .venv
fi

echo ========= Creating virtual environments for "$repo" =======
if [ -d ".venv" ]
then
    echo Virtual environment already exists for $fsd-$repo ...
    echo Upgrading the dependencies...

    # Activate venv
    if [ -d ".venv/bin" ];then
        source .venv/bin/activate # mac pc
    else
        source .venv/Scripts/activate # windows pc
    fi

    # Upgrade the dependencies
    pip install -r requirements-dev.txt --upgrade
else
    # Create venv
    python -m venv .venv

    # Activate venv
    if [ -d ".venv/bin" ];then
        source .venv/bin/activate # mac pc
    else
        source .venv/Scripts/activate # windows pc
    fi

    # Install the dependencies
    python -m pip install --upgrade pip && pip install pip-tools
    pip-compile requirements.in
    pip-compile requirements-dev.in
    echo Installing the dependencies...
    pip install -r requirements-dev.txt
fi

if [ "$install_pre_commit" = true ] ; then
    echo Installing the pre-commit hooks...
    pre-commit install
fi

if [ "$build_static_files" = true ] ; then
    static_repos_array=("authenticator" "assessment" "frontend")
    if [[ " ${static_repos_array[*]} " =~ " $repo " ]]; then
        echo Building the static files...
        export FLASK_ENV=development
        python build.py
    fi
fi

# deactivate python venv
deactivate

echo -------------------------------------------------------------------------
done

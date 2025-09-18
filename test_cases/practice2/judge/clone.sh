#!/usr/bin/env bash

RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m'

STUDENTS_FILE='repos.json'
DEADLINE='2025-03-16 23:59:00'
DIR_RUN='temp'
EXE='main.out'

function error() {
    echo -e "${RED}[ERROR] ${NC}$1"
    exit
}

function info() {
    echo -e "${GREEN}[INFO] ${NC}$1"
}

function check_dependency() {
    dep=$1
    if ! command -v $dep &>/dev/null; then
        error "$dep could not be found"
        exit
    fi
}

function assure_repo_exists() {
    repo=$1
    if ! git ls-remote $repo &>/dev/null; then
        error "$repo does not exist or is not accessible"
        exit
    fi
}

function assure_commit_exists() {
    if ! git cat-file -e $1 &>/dev/null; then
        error "$1 commit does not exist"
        exit
    fi
}

function clone_and_checkout() {
    repo=$1
    commit=$2
    dir=$3
    info "Cloning $repo to $dir"
    assure_repo_exists "$repo"
    git clone "$repo" "$dir"
    if [[ -n "$commit" ]]; then
        info "here"
        info "Checking out commit $commit"
        pushd "$dir" >/dev/null || exit 2
        assure_commit_exists "$commit"
        git config --local advice.detachedHead false
        git checkout "$commit"
        popd >/dev/null || exit 2
    fi
}

function https_to_ssh() {
    url=$1
    ssh_url=${url/https:\/\/github.com\//git@github.com:}
    echo $ssh_url
}

function get_user_statistic() {
    info "Getting user statistic"
    git log --format='%aN' | sort | uniq -c | while read count author; do
        echo "Author: $author"
        echo "Commits: $count"
        echo "Lines added/removed:"
        git log --author="$author" --pretty=tformat: --numstat | awk '/(\.cpp|\.hpp|\.c|\.cc|\.h|\.hh|makefile|Makefile)$/ { add += $1; subs += $2; loc += $1 + $2 } END { printf "Added: %s\nRemoved: %s\nTotal: %s\n", add, subs, loc }'
        echo "---------------------------------------------"
    done
}

function get_commit_delay() {
    current_commit_date=$(git show -s --format=%ci)
    current_commit_timestamp=$(date -d "$current_commit_date" +%s)
    deadline_timestamp=$(date -d "$DEADLINE" +%s)
    delay=$((current_commit_timestamp - deadline_timestamp))
    if ((delay < 0)); then
        echo 0
    else
        delay_in_days=$(((delay + 86399) / 86400)) # Round up to the nearest day
        echo $delay_in_days
    fi
}

function get_changed_lines_count() {
    commit1=$1
    commit2=$2
    git diff --numstat $commit1 $commit2 | awk '/(\.cpp|\.hpp|\.c|\.cc|\.h|\.hh|makefile|Makefile)$/ { if ($1 > max) max = $1; if ($2 > max) max = $2 } END { print max }'
}

function get_repo_url_and_commit() {
    sid=$1
    result=$(jq -r --arg sid "$sid" '
        .[] |
        select( any(.students[]; . == $sid) or any(.githubs[]; . == $sid) ) |
        [.repo_url, .commit_sha] | @tsv
    ' "$STUDENTS_FILE" | head -n 1)

    if [[ -z "$result" ]]; then
        error "Student with sid $sid not found"
    fi

    repo=$(echo "$result" | awk -F'\t' '{print $1}')
    commit=$(echo "$result" | awk -F'\t' '{print $2}')

    echo "$repo"
    echo "$commit"
}

function list_commits() {
    git log --oneline --abbrev-commit --format='%h %an %s' | cat
}

function clone() {
    local sid=$1
    result=$(get_repo_url_and_commit "$sid")
    repo_url=$(echo "$result" | head -n 1)
    if [[ $(echo "$result" | wc -l) -eq 1 ]]; then
        commit_sha=""
    else
        commit_sha=$(echo "$result" | tail -n 1)
    fi
    url=$(https_to_ssh "$repo_url")
    clone_and_checkout "$url" "$commit_sha" "$DIR_RUN"

    pushd "$DIR_RUN" >/dev/null || exit 2
    info "Listing commits"
    list_commits
    echo "---------------------------------------------"
    get_user_statistic
    info "Getting commit delay"
    echo "Commit delay: $(get_commit_delay) days"
    popd >/dev/null || exit 2
}

function make_and_run() {
    pushd $DIR_RUN >/dev/null
    make
    if [[ $? -ne 0 ]]; then
        error "Make failed"
    fi
    ./$EXE
    popd >/dev/null
}

function edit_code() {
    sid=$1
    new_commit_sha=$2
    repo_url=$(get_repo_url_and_commit $sid | head -n 1)
    commit_sha=$(get_repo_url_and_commit $sid | tail -n 1)
    url=$(https_to_ssh $repo_url)
    clone_and_checkout $url $commit_sha $DIR_RUN
    pushd $DIR_RUN >/dev/null
    get_changed_lines_count $commit_sha $new_commit_sha
    popd >/dev/null
}

# -------------------------------

check_dependency jq
check_dependency git
check_dependency date
check_dependency awk

if [[ $# -eq 0 ]]; then
    error "No arguments provided"
fi

case $1 in
clone)
    if [[ $# -ne 2 ]]; then
        error "Invalid number of arguments"
    fi
    clone $2
    ;;
run)
    make_and_run
    ;;
edit)
    if [[ $# -ne 3 ]]; then
        error "Invalid number of arguments"
    fi
    edit_code $2 $3
    ;;
--help)
    echo "Usage: $0 [command] [args]"
    echo "Commands:"
    echo "  clone [sid] - clone student's repository and checkout to the commit"
    echo "  run - make and run the code"
    echo "  edit [sid] [new_commit_sha] - edit code and get changed lines count"
    ;;
*)
    error "Invalid command"
    ;;
esac

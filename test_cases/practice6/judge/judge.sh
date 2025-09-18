#!/bin/bash

CONFIG_FILE="./config.sh"

source $CONFIG_FILE

function remove_colors() {
    sed -r "s/\x1B\[[0-9;]*[mK]//g"
}

function toplevel_zips() {
    local temp_folder=".temp_toplevel_zips"

    local count=0
    for f in *.zip; do
        [[ -e $f ]] || continue
        ((count++))
        echo "Processing file #${count}: ${f}..."

        unzip "$f" -d "$temp_folder" >/dev/null || exit 1
        pushd "$temp_folder" >/dev/null || exit 2

        find . -mindepth 2 -type f -exec mv -i -t ./ {} +
        find . -type d -empty -delete

        rm -rf "../$f"

        zip "../$f" -r -0 . >/dev/null || exit 1
        popd >/dev/null || exit 2
        rm -rf "$temp_folder"
    done
}

function rar_to_zip() {
    local temp_folder=".temp_rar_to_zip"

    local count=0
    for f in *.rar; do
        mkdir -p "$temp_folder"
        [[ -e $f ]] || continue
        ((count++))
        echo "Processing file #${count}: ${f}..."

        unrar x "$f" "$temp_folder" >/dev/null || exit 1
        pushd "$temp_folder" >/dev/null || exit 2

        zip -r -0 "../${f%.rar}.zip" . >/dev/null || exit 1
        popd >/dev/null || exit 2

        rm -rf "$temp_folder"
        rm -f "$f"
    done
}

function cxx_compile {
    local file_name=$1
    echo -e "${C_CYN}${C_ULN}Compiling $file_name...${C_CLR}"
    if [[ ! -e "$file_name" ]]; then
        echo -e "${C_RED}File $file_name does not exist${C_CLR}" >&2
        return 1
    fi
    if ! $COMPILER "$file_name" -o $EXE >/dev/null 2>&1; then
        echo -e "${C_RED}Compile Error${C_CLR}" >&2
        return 1
    fi
    echo -e "Compiled Successfully"
    return 0
}

function cxx_make {
    echo -e "${C_CYN}${C_ULN}Running Make...${C_CLR}"
    if [[ ! -f Makefile && ! -f makefile ]]; then
        echo -e "${C_RED}Makefile not found${C_CLR}" >&2
        return 1
    fi
    make clean
    if ! make; then
        echo -e "${C_RED}Compile Error${C_CLR}" >&2
        return 1
    fi
    echo -e "Compiled Successfully"
    return 0
}

function compile_and_run {
    local verbose="false"
    [[ $3 == "true" ]] && verbose="true"

    local file_name=$1
    local test_dir=$2
    local passed=0
    local failed=0

    if [[ $file_name == "Makefile" ]]; then
        cxx_make || return
    else
        cxx_compile "$file_name" || return
    fi

    if [[ ! -f "$EXE" ]]; then
        echo -e "${C_RED}EXE not found${C_CLR}" >&2
        return 1
    fi

    if [[ $TEST_CASE == "true" ]]; then
        echo -e "Running tests [DIR: $test_dir]"

        for testcase in "$test_dir"/[0-9]*; do
            [[ -d "$testcase" ]] || continue
            [[ "$testcase" == "csv" ]] && continue

            local number=$(basename "$testcase")
            local input="$testcase/$number.in"
            local solution="$testcase/$number.out"

            local restaurant_csv="$test_dir/csv/restaurants.csv"
            local district_csv="$test_dir/csv/districts.csv"
            local discount_csv="$test_dir/csv/discounts.csv"

            echo -e "${C_YLW}Running test: $number${C_CLR}"

        #     if ! timeout $TIME_LIMIT ./$EXE "$restaurant_csv" "$district_csv" "$discount_csv" < "$input" >"$EXE_OUTPUT" 2>&1; then
        #         echo -e "${C_RED}Timed out${C_CLR}"
        #         ((failed++))
        #             echo "Last few lines of output:"
        # tail -n 5 "$EXE_OUTPUT"
        #         continue
        #     fi

            base_command="timeout $TIME_LIMIT ./$EXE \"$restaurant_csv\" \"$district_csv\""

            if [[ "${DIR_BASE}" == "P1" ]]; then
                if ! eval "$base_command" < "$input" >"$EXE_OUTPUT" 2>&1; then
                    echo -e "${C_RED}Timed out${C_CLR}"
                    ((failed++))
                    echo "Last few lines of output:"
                    tail -n 5 "$EXE_OUTPUT"
                    continue
                fi
            else
                if ! eval "$base_command \"$discount_csv\"" < "$input" >"$EXE_OUTPUT" 2>&1; then
                    echo -e "${C_RED}Timed out${C_CLR}"
                    ((failed++))
                    echo "Last few lines of output:"
                    tail -n 5 "$EXE_OUTPUT"
                    continue
                fi
            fi

            if $DIFF_TOOL "$EXE_OUTPUT" "$solution" > /dev/null; then
                echo -e "${C_GRN}Accepted${C_CLR}"
                ((passed++))
            else
                echo -e "${C_RED}Wrong Answer${C_CLR}"
                ((failed++))
                if [[ $verbose == "true" ]]; then
                    printf "%28s | %28s\n" "< $EXE_OUTPUT" "> solution"
                    $VERBOSE_DIFF_TOOL "$EXE_OUTPUT" "$solution"
                fi
            fi
        done

        echo
        echo -e "        Passed: ${C_GRN}$passed${C_CLR} out of $((passed + failed))"
        echo -e "        Failed: ${C_RED}$failed${C_CLR} out of $((passed + failed))"
        echo

    else
        echo -e "Running Program"
        ./$EXE "$test_dir/csv/restaurants.csv" "$test_dir/csv/districts.csv" "$test_dir/csv/discounts.csv"
    fi

    rm -f "$EXE_OUTPUT"
}

function run_multi_file_tests {
    local verbose="false"
    [[ $1 == "true" ]] && verbose="true"

    for (( i = 0; i < ${#MULTI_FILE_NAMES[@]}; i++ )); do
        local file_name=${MULTI_FILE_NAMES[i]}
        local curr_tests="$DIR_TESTS/$i"
        compile_and_run "$file_name" "$curr_tests" "$verbose"
    done
}

function run_single_file_tests {
    local verbose="false"
    [[ $1 == "true" ]] && verbose="true"

    if [[ $(find . -maxdepth 1 -type f | wc -l) -ge 1 ]]; then
        local file_name=$(find . -maxdepth 1 -type f -name "*.cpp" -print -quit)
        echo -e "${C_YLW}Found single file: $file_name${C_CLR}"
        compile_and_run "$file_name" "$DIR_TESTS" "$verbose"
        return
    fi
    echo -e "${C_YLW}No file found, or found multiple candidates.${C_CLR}"
    compile_and_run "$SINGLE_FILE_NAME" "$DIR_TESTS" "$verbose"
}

function run_make_file_tests {
    local verbose="false"
    [[ $1 == "true" ]] && verbose="true"
    compile_and_run "Makefile" "$DIR_TESTS" "$verbose"
}

function create_git_repo {
    pushd $DIR_RUN > /dev/null

    git init > /dev/null 2>&1
    git add . > /dev/null 2>&1
    git commit -m "Init" > /dev/null 2>&1

    popd > /dev/null
}

function number_of_edited_lines {
    pushd $DIR_RUN > /dev/null

    git init > /dev/null 2>&1
    git add . > /dev/null 2>&1
    git commit -m "Edit" > /dev/null 2>&1

    diff_output=$(git diff --shortstat HEAD HEAD~1)
    insertions=$(echo $diff_output | grep -oP "\d+ insertions?" | grep -oP "\d+")
    deletions=$(echo $diff_output | grep -oP "\d+ deletions?" | grep -oP "\d+")

    popd > /dev/null

    insertions=${insertions:-0}
    deletions=${deletions:-0}

    total=$((insertions + deletions))
    echo "$total"
}

function unzip_code() {
    local unzip_filename=$1
    rm -rf "$DIR_RUN"
    echo -e "${C_BLU}${C_ULN}Unzipping...${C_CLR} [FILE: $unzip_filename]"
    if [[ ! -e $unzip_filename ]]; then
        echo -e "${C_RED}File not found.${C_CLR}" >&2
        exit 1
    elif ! unzip "$unzip_filename" -d "$DIR_RUN" >/dev/null 2>&1; then
        echo -e "${C_RED}Unzip Error${C_CLR}" >&2
        exit 1
    fi
}

function move_code() {
    local move_filename=$1

    rm -rf "$DIR_RUN"
    mkdir -p "$DIR_RUN"
    echo -e "${C_BLU}${C_ULN}Moving...${C_CLR} [FILE: $move_filename]"
    if [[ ! -e $move_filename ]]; then
        echo -e "${C_RED}File not found.${C_CLR}" >&2
        exit 1
    elif ! cp "$move_filename" "$DIR_RUN" >/dev/null 2>&1; then
        echo -e "${C_RED}Move Error${C_CLR}" >&2
        exit 1
    fi
}

function test_code() {
    echo -e "${C_BLU}${C_ULN}Testing...${C_CLR} [DIR: $dir_run]"
    if [[ ! -d $dir_run ]]; then
        echo -e "${C_RED}Directory not found.${C_CLR} [${dir_run}]" >&2
        exit 1
    fi
    pushd "$DIR_RUN" >/dev/null
    if [[ $MAKE_FILE == "true" ]]; then
        run_make_file_tests "$verbose"
    elif [[ $MULTI_FILE == "true" ]]; then
        run_multi_file_tests "$verbose"
    else
        run_single_file_tests "$verbose"
    fi
    popd >/dev/null
}

function clone {
    echo -e "${C_CYN}${C_ULN}Cloning...${C_CLR}"
    echo -e "${C_YLW}SID: $git_sid${C_CLR}"
    export git_sid
    ./clone.sh clone "$git_sid"
    echo -e "${C_GRN}Done${C_CLR}"
}

function print_help() {
    echo "Usage: ./judge.sh [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  -h, --help"
    echo "        Shows this help message"
    echo "  -s, --show-options"
    echo "        Prints the chosen arguments"
    echo "  -t, --test [FOLDER (default:DIR_RUN)]"
    echo "        Compiles the files in FOLDER and runs the testcases in DIR_TESTS"
    echo "  -g, --git [SID]"
    echo "        Clones the repo with the given SID"
    echo "  -e, --edit [SID] [FILE]"
    echo "        Clones the repo with the given SID and new commit"
    echo "  -m, --move [FILE]"
    echo "        Moves the cpp file to DIR_RUN"
    echo "  -u, --unzip [FILE]"
    echo "        Unzips FILE into DIR_RUN"
    echo "  -c, --clean"
    echo "        Cleans DIR_RUN and temp folders in DIR_CODES in case the script failed"
    echo "  -v, --verbose (not)"
    echo "        Do not print test result's comparison with the solution output"
    echo "  -a, --all"
    echo "        Runs every submission in the codes directory and save the result grades in the results.csv"
    echo "  --raw-to-code"
    echo "        Copies all files from DIR_RAW to DIR_CODES"
    echo "  --rar-to-zip"
    echo "        Re-archives rar files to zip files in DIR_CODES"
    echo "  --under-to-dash"
    echo "        Renames files in DIR_CODES to use - instead of _"
    echo "  --toplevel-zips"
    echo "        Re-zips DIR_CODES files and moves all of their content to the toplevel folder"
    echo "  --preprocess"
    echo "        Runs raw-to-code, rar-to-zip, under-to-dash, and toplevel-zips"
    echo "  --edit-code [FILE]"
    echo "        Compares the FILE in edit-code with the FILE in codes and runs it of the edit code limits are met"
    echo ""
    echo "Current Variables:"
    echo "  DIR_CODES:  $DIR_CODES"
    echo "  DIR_RAW:    $DIR_RAW"
    echo "  DIR_RUN:    $DIR_RUN"
    echo "  DIR_TESTS:  $DIR_TESTS"
    echo "  TIME_LIMIT: $TIME_LIMIT"
}

## Script ##

if [[ $# -eq 0 ]]; then
    print_help
    exit 0
fi

while [[ $# -gt 0 ]]; do
    case $1 in
    -s | --show-options)
        show_options="true"
        shift
        ;;
    -t | --test)
        test="true"
        if [[ -n $2 && ! $2 =~ ^-.* ]]; then
            unzip_filename="${DIR_CODES}/A6-$2.zip"
            echo "unzip_filename: $unzip_filename"
            unzip="true"
            shift
        fi
        shift
        ;;
    -g|--git)
        is_git="true"
        git_sid=$2
        shift; shift;;
    -e|--edit)
        is_edit="true"
        git_sid=$2
        commit_sha=$3
        shift; shift; shift;;
    -r | --run)
        run_all_phases="true"
        sid=$2
        shift
        shift
        ;;
    -m | --move)
        move="true"
        move_filename=$2
        shift
        shift
        ;;
    -u | --unzip)
        unzip="true"
        unzip_filename=$2
        shift
        shift
        ;;
    -c | --clean)
        clean="true"
        shift
        ;;
    -v | --verbose)
        verbose="false"
        shift
        ;;
    -h | --help)
        print_help
        exit 0
        ;;
    -p | --phase)
        change_phase="true"
        phase=$2
        shift
        shift
        ;;
    --raw-to-code)
        raw_to_code="true"
        shift
        ;;
    --rar-to-zip)
        rar_to_zip="true"
        shift
        ;;
    --under-to-dash)
        under_to_dash="true"
        shift
        ;;
    --toplevel-zips)
        toplevel_zips="true"
        shift
        ;;
    --preprocess)
        preprocess="true"
        shift
        ;;
    -*)
        echo "Unknown option: $1" >&2
        exit 1
        ;;
    *)
        echo "Script takes no positional arguments: $1" >&2
        exit 1
        ;;
    esac
done

: ${show_options:="false"}
: ${test:="false"}
: ${dir_run:="$DIR_RUN"}
: ${is_git:="false"}
: ${move:="false"}
: ${unzip:="false"}
: ${clean:="false"}
: ${verbose:="true"}
: ${preprocess:="false"}
: ${all:="false"}
: ${raw_to_code:=$preprocess}
: ${rar_to_zip:="false"}
: ${under_to_dash:=$preprocess}
: ${toplevel_zips:="false"}
: ${edit:="false"}

if [[ $show_options == "true" ]]; then
    echo -e "--     ${C_ULN}JUDGE.sh${C_CLR}     --"
    echo "| Verbose:       ${verbose^^}"
    echo "| Clean:         ${clean^^}"
    echo "| Raw to Code:   ${raw_to_code^^}"
    echo "| Rar to Zip:    ${rar_to_zip^^}"
    echo "| Under to Dash: ${under_to_dash^^}"
    echo "| Toplevel Zips: ${toplevel_zips^^}"
    echo "| Unzip:         ${unzip^^}"
    echo "| Move:          ${move^^}"
    echo "| Test:          ${test^^}"
    echo "----------------------"
fi

if [[ $clean == "true" ]]; then
    echo -e "${C_BLU}${C_ULN}Cleaning temp directories...${C_CLR}"
    rm -rf "$DIR_RUN"
    mkdir "$DIR_RUN"
    rm -rf "$DIR_CODES/.temp_toplevel_zips" \
           "$DIR_CODES/.temp_rar_to_zip"
fi

if [[ $change_phase == "true" ]]; then
    echo -e "${C_BLU}${C_ULN}Changing phase...${C_CLR} [PHASE: $phase]"
    sed -i "s/DIR_BASE=.*/DIR_BASE=\"P$phase\"/" "$CONFIG_FILE"
    echo -e "${C_GRN}Phase changed successfully.${C_CLR}"
fi

if [[ $is_git == "true" ]]; then
    # run the clone.sh script with the provided git SID
    rm -rf "$DIR_RUN"
    mkdir -p "$DIR_RUN"
    echo -e "${C_BLU}${C_ULN}Running clone.sh...${C_CLR}"
    if ! clone; then
        echo -e "${C_RED}Error while running clone.sh.${C_CLR}" >&2
        exit 1
    fi
fi

if [[ $is_edit == "true" ]]; then
    # run the clone.sh edit script with the provided git SID and new commit sha
    echo -e "${C_BLU}${C_ULN}Running clone.sh edit...${C_CLR}"
    if ! clone_edit; then
        echo -e "${C_RED}Error while running clone.sh edit.${C_CLR}" >&2
        exit 1
    fi
fi

if [[ $raw_to_code == "true" ]]; then
    echo -e "${C_BLU}${C_ULN}Copying raws to the codes folder...${C_CLR}"
    rm -rf "$DIR_CODES"
    mkdir "$DIR_CODES"
    find "$DIR_RAW" -type f -iname "*.zip" -exec cp -t "$DIR_CODES" {} +
    find "$DIR_RAW" -type f -iname "*.rar" -exec cp -t "$DIR_CODES" {} +
fi

if [[ $rar_to_zip == "true" ]]; then
    echo -e "${C_BLU}${C_ULN}Converting rar to zip...${C_CLR}"
    pushd "$DIR_CODES" >/dev/null || exit 2
    if ! rar_to_zip; then
        echo -e "${C_RED}Error while converting.${C_CLR}" >&2
        exit 1
    fi
    popd >/dev/null || exit 2
fi

if [[ $under_to_dash == "true" ]]; then
    echo -e "${C_BLU}${C_ULN}Converting underscores to dash...${C_CLR}"
    for f in "$DIR_CODES"/*_*; do
        [[ -e $f ]] || continue
        echo "Renaming $f..."
        mv -- "$f" "${f//_/-}"
    done
fi

if [[ $toplevel_zips == "true" ]]; then
    pushd "$DIR_CODES" >/dev/null || exit 2
    echo -e "${C_BLU}${C_ULN}Moving files to the toplevel in zips...${C_CLR}"
    if ! toplevel_zips; then
        echo -e "${C_RED}Error while moving.${C_CLR}" >&2
        exit 1
    fi
    popd >/dev/null || exit 2
fi

if [[ $unzip == "true" ]]; then
    rm -rf "$DIR_RUN"
    echo -e "${C_BLU}${C_ULN}Unzipping...${C_CLR} [FILE: $unzip_filename]"
    if [[ ! -e $unzip_filename ]]; then
        echo -e "${C_RED}File not found.${C_CLR}" >&2
        exit 1
    elif ! unzip "$unzip_filename" -d "$DIR_RUN" >/dev/null 2>&1; then
        echo -e "${C_RED}Unzip Error${C_CLR}" >&2
        exit 1
    fi
fi

if [[ $move == "true" ]]; then
    rm -rf "$DIR_RUN"
    mkdir -p "$DIR_RUN"
    echo -e "${C_BLU}${C_ULN}Moving...${C_CLR} [FILE: $move_filename]"
    if [[ ! -e $move_filename ]]; then
        echo -e "${C_RED}File not found.${C_CLR}" >&2
        exit 1
    elif ! cp "$move_filename" "$DIR_RUN" >/dev/null 2>&1; then
        echo -e "${C_RED}Move Error${C_CLR}" >&2
        exit 1
    fi
fi

if [[ $test == "true" ]]; then
    echo -e "${C_BLU}${C_ULN}Testing...${C_CLR} [DIR: $dir_run]"
    if [[ ! -d $dir_run ]]; then
        echo -e "${C_RED}Directory not found.${C_CLR} [${dir_run}]" >&2
        exit 1
    fi
    pushd "$dir_run" >/dev/null
    if [[ $MAKE_FILE == "true" ]]; then
        run_make_file_tests "$verbose"
    elif [[ $MULTI_FILE == "true" ]]; then
        run_multi_file_tests "$verbose"
    else
        run_single_file_tests "$verbose"
    fi
    popd >/dev/null

    # code $DIR_RUN
fi

if [[ $run_all_phases == "true" ]]; then
    for ((i = 1; $i <= $NUM_OF_PHASES; i++)); do
        ./judge.sh -p $i
        ./judge.sh -t $sid
        echo ==============================================================
    done
fi

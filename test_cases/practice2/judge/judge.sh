#!/bin/bash


C_RED="\033[31m"
C_GRN="\033[32m"
C_YLW="\033[33m"
C_BLU="\033[34m"
C_CYN="\033[36m"
C_ULN="\033[4m"
C_CLR="\033[0m"

DIR_CODES="codes"
DIR_RAW="raw"
DIR_RUN="temp"
DIR_TESTS="$(pwd)/tests"
DIR_CSVS="$(pwd)/csvs"

MULTI_FILE="false"
MULTI_FILE_NAMES=()
SINGLE_FILE_NAME="src/main.cpp"

STUDENTS_CSV_FILE_NAME="students.csv"
TABLES_CSV_FILE_NAME="tables.csv"

is_git="false"

EXE="a.out"
EXE_OUTPUT="out.txt"
COMPILER="g++ -std=c++2a"

TIME_LIMIT=10s
DIFF_TOOL="diff -bBq"
VERBOSE_DIFF_TOOL="sdiff -Wsw 60"


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

function compile_and_run {
    local verbose="false"
    [[ $4 == "true" ]] && verbose="true"

    local file_name=$1
    local test_dir=$2
    local csv_dir=$3
    local passed=0
    local failed=0

    echo -e "${C_CYN}${C_ULN}Compiling $file_name...${C_CLR}"
    if [[ ! -e "$file_name" ]]; then
        echo -e "${C_RED}File does not exist${C_CLR}" >&2
        return
    fi
    if ! $COMPILER "$file_name" -o $EXE >/dev/null 2>&1; then
        echo -e "${C_RED}Compile Error${C_CLR}" >&2
        ((failed++))
        return
    fi
    echo -e "Compiled Successfully"

    echo -e "Running tests [DIR: $test_dir]"
    for testcase in "$test_dir"/*; do
        [[ -d "$testcase" ]] || continue

        local number=$(basename "$testcase")
        local input="$testcase/$number.in"
        local solution="$testcase/$number.out"
        local cars_csv="$testcase/cars.csv"
        local slots_csv="$testcase/slots.csv"
        local prices_csv="$testcase/prices.csv"

        echo -e "${C_YLW}Running test: $number${C_CLR}"

        # find "$testcase" -name "*.csv" -exec cp {} . \;

        # This assignment required two arg vars and no stdin input. Change this
        # behavior from here
        if ! timeout $TIME_LIMIT ./$EXE "$csv_dir/$TABLES_CSV_FILE_NAME" "$csv_dir/$STUDENTS_CSV_FILE_NAME" < "$input" >"$EXE_OUTPUT" 2>&1; then
            echo -e "${C_RED}Timed out${C_CLR}"
            ((failed++))
            continue
        fi

        # Use diff if you don't need a verifier
        # python3 ../verifier.py $solution $EXE_OUTPUT

        if $DIFF_TOOL "$EXE_OUTPUT" "$solution" >/dev/null; then
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

        # rm ./*.csv
    done

    echo
    echo -e "        Passed: ${C_GRN}$passed${C_CLR} out of $((passed + failed))"
    echo -e "        Failed: ${C_RED}$failed${C_CLR} out of $((passed + failed))"
    echo

    rm -f "$EXE" "$EXE_OUTPUT"
}

function run_multi_file_tests {
    local verbose="false"
    [[ $1 == "true" ]] && verbose="true"

    for (( i = 0; i < ${#MULTI_FILE_NAMES[@]}; i++ )); do
        local file_name=${MULTI_FILE_NAMES[i]}
        local curr_tests="$DIR_TESTS/$i"
        compile_and_run "$file_name" "$curr_tests" "$DIR_CSVS" "$verbose"
    done
}

function run_single_file_tests {
    local verbose="false"
    [[ $1 == "true" ]] && verbose="true"

    if [[ $(find . -maxdepth 1 -type f | wc -l) -eq 1 ]]; then
        local file_name=$(find . -maxdepth 1 -type f -print -quit)
        echo -e "${C_YLW}Found single file: $file_name${C_CLR}"
        compile_and_run "$file_name" "$DIR_TESTS" "$DIR_CSVS" "$verbose"
        return
    fi
    compile_and_run "$SINGLE_FILE_NAME" "$DIR_TESTS" "$DIR_CSVS" "$verbose"
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
    echo "  -m, --move [FILE]"
    echo "        Moves the cpp file to DIR_RUN"
    echo "  -u, --unzip [FILE]"
    echo "        Unzips FILE into DIR_RUN"
    echo "  -c, --clean"
    echo "        Cleans DIR_RUN and temp folders in DIR_CODES in case the script failed"
    echo "  -v, --verbose (not)"
    echo "        Do not print test result's comparison with the solution output"
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
        -s|--show-options)
            show_options="true"
            shift;;
        -t|--test)
            test="true"
            if [[ -n $2 && ! $2 =~ ^-.* ]]; then
                dir_run=$2
                shift
            fi
            shift;;
        -g|--git)
            is_git="true"
            git_sid=$2
            SINGLE_FILE_NAME="src/main.cpp"
            shift; shift;;
        -m|--move)
            move="true"
            move_filename=$2
            shift; shift;;
        -u|--unzip)
            unzip="true"
            unzip_filename=$2
            shift; shift;;
        -c|--clean)
            clean="true"
            shift;;
        -v|--verbose)
            verbose="false"
            shift;;
        -h|--help)
            print_help
            exit 0;;
        --raw-to-code)
            raw_to_code="true"
            shift;;
        --rar-to-zip)
            rar_to_zip="true"
            shift;;
        --under-to-dash)
            under_to_dash="true"
            shift;;
        --toplevel-zips)
            toplevel_zips="true"
            shift;;
        --preprocess)
            preprocess="true"
            shift;;
        -*)
            echo "Unknown option: $1" >&2
            exit 1;;
        *)
            echo "Script takes no positional arguments: $1" >&2
            exit 1;;
    esac
done

: ${show_options:="false"}
: ${test:="false"}
: ${dir_run:="$DIR_RUN"}
: ${move:="false"}
: ${is_git:="false"}
: ${unzip:="false"}
: ${clean:="false"}
: ${verbose:="true"}
: ${preprocess:="false"}
: ${raw_to_code:=$preprocess}
: ${rar_to_zip:=$preprocess}
: ${under_to_dash:=$preprocess}
: ${toplevel_zips:=$preprocess}

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
    echo "| Preprocess:    ${preprocess^^}"
    echo "----------------------"
fi

if [[ $clean == "true" ]]; then
    echo -e "${C_BLU}${C_ULN}Cleaning temp directories...${C_CLR}"
    rm -rf "$DIR_RUN"
    mkdir "$DIR_RUN"
    rm -rf "$DIR_CODES/.temp_toplevel_zips" \
           "$DIR_CODES/.temp_rar_to_zip"
fi

if [[ $raw_to_code == "true" ]]; then
    echo -e "${C_BLU}${C_ULN}Copying raws to the codes folder...${C_CLR}"
    rm -rf "$DIR_CODES"
    mkdir "$DIR_CODES"
    find "$DIR_RAW" -type f -iname "*.zip" -exec cp -t "$DIR_CODES" {} +
    find "$DIR_RAW" -type f -iname "*.rar" -exec cp -t "$DIR_CODES" {} +
    find "$DIR_RAW" -type f -iname "*.cpp" -exec cp -t "$DIR_CODES" {} +
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

if [[ $test == "true" ]]; then
    echo -e "${C_BLU}${C_ULN}Testing...${C_CLR} [DIR: $dir_run]"
    if [[ ! -d $dir_run ]]; then
        echo -e "${C_RED}Directory not found.${C_CLR} [${dir_run}]" >&2
        exit 1
    fi
    pushd "$dir_run" >/dev/null
    if [[ $MULTI_FILE == "true" ]]; then
        run_multi_file_tests "$verbose"
    else
        run_single_file_tests "$verbose"
    fi
    popd >/dev/null

    # code $DIR_RUN
fi

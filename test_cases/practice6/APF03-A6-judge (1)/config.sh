C_RED="\033[31m"
C_GRN="\033[32m"
C_YLW="\033[33m"
C_BLU="\033[34m"
C_CYN="\033[36m"
C_ULN="\033[4m"
C_CLR="\033[0m"

NUM_OF_PHASES=3
DIR_BASE="P3"
TEST_CASE="true"

if [[ "${DIR_BASE}" == "P3" ]]; then
    TEST_CASE="false"
fi

DIR_CODES="$(pwd)/${DIR_BASE}/codes"
DIR_RAW="$(pwd)/${DIR_BASE}/raw"
DIR_TESTS="$(pwd)/${DIR_BASE}/tests"
DIR_RUN="$(pwd)/temp-${DIR_BASE}"
RESULT_FILE="$(pwd)/result-${DIR_BASE}.txt"

MAKE_FILE="true"
MULTI_FILE="false"
MULTI_FILE_NAMES=()
SINGLE_FILE_NAME="A6-?????????.cpp"

EXE="UTaste"
COMPILER="make"
EXE_OUTPUT="out.txt"
RESTAURANT_CSV="${DIR_BASE}/tests/csv/restaurants.csv"
DISTRICT_CSV="${DIR_BASE}/tests/csv/districts.csv"
DISCOUNT_CSV="${DIR_BASE}/tests/csv/discounts.csv"
CSV2_PATH="../csv/file2.csv"

TIME_LIMIT=10s
DIFF_TOOL="sdiff -sWBi"
VERBOSE_DIFF_TOOL="sdiff -Wsiw 60"
PORT=5000

STUDENTS_FILE="repos_${DIR_BASE}.json"
DEADLINE=""

if [[ "${DIR_BASE}" == "P1" ]]; then
    DEADLINE="2024-12-24 23:59:00"
elif [[ "${DIR_BASE}" == "P2" ]]; then
    DEADLINE="2025-01-04 23:59:00"
else
    DEADLINE="2025-01-14 23:59:00"
fi

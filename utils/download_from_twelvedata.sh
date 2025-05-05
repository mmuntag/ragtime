#!/bin/bash

API_KEY="244d1ba8c89e4b91ab0ea66ea9da30d8"
SYMBOL="EUR/HUF"
INTERVAL="1min"
FORMAT="CSV"
TIMEZONE="exchange"
OUTPUT_FILE="eur_huf_full.csv"

START_DATE="2025-01-02"
END_DATE="2025-01-10"

current_date="$START_DATE"
first_day=true

# Remove output file if it exists
rm -f "$OUTPUT_FILE"

while [[ "$current_date" < "$END_DATE" || "$current_date" == "$END_DATE" ]]; do
    next_date=$(date -I -d "$current_date + 1 day")

    echo "Fetching data for $current_date..."

    # Construct URL
    url="https://api.twelvedata.com/time_series?apikey=$API_KEY&interval=$INTERVAL&symbol=$SYMBOL&start_date=${current_date}%2000:00:00&end_date=${next_date}%2000:00:00&format=$FORMAT&timezone=$TIMEZONE"

    if echo "$response" | grep -q '"code":400'; then
        echo "Error 400 on $current_date: $(echo "$response" | grep '"message"')"
    else

        # Fetch data
        if $first_day; then
            curl -s "$url" >> "$OUTPUT_FILE"
            first_day=false
        else
            curl -s "$url" | tail -n +2 >> "$OUTPUT_FILE"
        fi
    fi

    current_date="$next_date"
    sleep 7s
done

echo "Data fetching complete. Saved to $OUTPUT_FILE."


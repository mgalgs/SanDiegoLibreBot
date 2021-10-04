#!/bin/bash

# Reads env var key=val pairs from STDIN
# Writes k8s Secret to STDOUT

usage() {
    cat <<EOF
$0 <secret_name>

You should pass in stdin a list of key=val pairs to be stored as keys in
the Secret, e.g.:

MYKEY1=cool value
MYKEY2=other cool value

EOF
}

[[ "$1" = "-h" || "$1" = "--help" ]] && { usage; exit 1; }

SECRET_NAME=$1

[[ -n "$SECRET_NAME" ]] || { echo "Missing secret name"; usage; exit 1; }

cat <<EOF
apiVersion: v1
kind: Secret
metadata:
  name: $SECRET_NAME
type: Opaque
data:
EOF

while read l; do
    # https://stackoverflow.com/a/918931/209050
    IFS="=" read -ra splitted <<<"$l"
    key=${splitted[0]}
    val=${splitted[1]}
    val64=$(echo -n "$val" | base64)
    echo "  ${key}: ${val64}"
done

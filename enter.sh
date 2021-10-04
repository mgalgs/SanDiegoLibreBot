# SOURCE ME...

set -a
source env.sh
set +a

# disable writing of .pyc files
export PYTHONDONTWRITEBYTECODE=1

echo "Activating virtualenv..."
source ./venv/bin/activate

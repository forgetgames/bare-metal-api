# curl -sSL https://install.python-poetry.org | python -

# poetry self update

poetry config virtualenvs.in-project true
sudo pip install --upgrade setuptools
poetry install
git config --global --add safe.directory /workspaces/bare-metal-api

URL="https://downloads.python.org/pypy/pypy3.11-v7.3.21-win64.zip"
OUTDIR="dist/"
TMPZIP="pypy.zip"

rm -rf dist/
mkdir dist/
cp -r src/ dist/

rm -f "$TMPZIP"

echo "Downloading $URL..."
curl -fSL "$URL" -o "$TMPZIP"

echo "Creating target directory: $OUTDIR"
mkdir -p "$OUTDIR"

echo "Extracting archive to $OUTDIR..."
unzip -q "$TMPZIP" -d "$OUTDIR"


cat <<EOF > dist/run.bat
@echo off
set PYTHON_EXEC="pypy3.11-v7.3.21-win64\pypy.exe"
set SCRIPT_PATH="src\hotseat_gui.py"

%PYTHON_EXEC% %SCRIPT_PATH%
EOF

zip -r hotseat_tool.zip dist/

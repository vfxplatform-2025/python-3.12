#!/bin/bash
set -e

VERSION=3.12.10
ARCHIVE=Python-$VERSION.tgz
URL=https://www.python.org/ftp/python/$VERSION/$ARCHIVE

cd source

if [ ! -f "$ARCHIVE" ]; then
    echo "⬇️  Downloading $ARCHIVE"
    wget "$URL"
else
    echo "✅ Archive already exists: $ARCHIVE"
fi

if [ ! -d "Python-$VERSION" ]; then
    echo "📦 Extracting $ARCHIVE"
    tar -xzf $ARCHIVE
else
    echo "📁 Source already extracted: Python-$VERSION"
fi


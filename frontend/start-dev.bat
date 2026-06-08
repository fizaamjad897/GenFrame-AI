@echo off
set NODE_OPTIONS=--max-old-space-size=8192
node node_modules/next/dist/bin/next dev

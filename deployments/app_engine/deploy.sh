#!/usr/bin/env bash

rm -rf target || true
mkdir target

j2 app.yaml.jinja2 > target/app.yaml
cp main.py target
cp ../../requirements.txt target
cp -r ../../mdwiki_gae target

gcloud app deploy target/app.yaml --project $GOOGLE_CLOUD_PROJECT --quiet

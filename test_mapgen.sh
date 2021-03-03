#!/bin/sh

curl --header "Content-Type: application/json" \
  --request POST \
  --data '{"players":"6","tiles":"tiles.json","layout":"standard_hex.json"}' \
  http://localhost:8000/mapgen/generate_map \
  | sed 's/\\n/\
'/g

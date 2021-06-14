#!/bin/bash

base_directory="$(dirname "$(readlink -f "$0")")"
pushd $base_directory

SEPARATOR='--------------------------------------------------------------------------------'
INDENT='  '

echo "$SEPARATOR"
echo "-- ${0##*/} Started!"
echo ""

in_folder="./../input/selection"
out_images="./../input/selection_crop"

img_ext="jpg"
crop="408:194:0:86"

enable_crop=true


files=$(ls $in_folder)

# Iterate the string array using for loop
for fname in $files; do
  # crop video
  if [ "$enable_crop" = "true" ]; then
    if [ ! -d "$out_images" ]; then
      mkdir $out_images
    fi
    cmd="ffmpeg -y -i $in_folder/$fname -vf "crop=843:632:349:263" $out_images/$fname"
  fi
  echo $cmd
  $cmd
done

#

echo ""
echo "-- ${0##*/} Finished!"
echo "$SEPARATOR"
popd

exit 0

#!/usr/bin/bash
#Authors: Brady Theisen, modified by Group 7

#Define categories
categories=("backward" "forward" "land" "left" "right" "takeoff")

#Base directory
base_dir=$1

echo "Base directory: $base_dir"

#Process each category
for category in "${categories[@]}"; do
    echo "Processing category: $category"
    
    #Move all files to the category directory and delete subdirectories
    find "$base_dir/$category" -mindepth 2 -type f -exec mv {} "$base_dir/$category" \;
    find "$base_dir/$category" -mindepth 1 -type d -delete;

    #Rename files sequentially to avoid overwrites on subsequent reruns
    readarray -d '' -t files < <(find "$base_dir/$category" -maxdepth 1 -type f -print0)
    count=1
    for file in "${files[@]}"; do
        mv "$file" "${file%/*}/temp$count.${file##*.}"
        ((count++))
    done
    
    #Rename files to a random number between 1 and the number of files
    readarray -d '' -t files < <(find "$base_dir/$category" -maxdepth 1 -type f -print0)
    num_files=${#files[@]}
    for file in "${files[@]}"; do
        random_number=$(( RANDOM % num_files + 1 ))
        while test -f "${file%/*}/$random_number.${file##*.}"; do
            random_number=$(( RANDOM % num_files + 1 ))
        done
        mv "$file" "${file%/*}/$random_number.${file##*.}"
    done
    
    #Change timestamp and display before and after
    for file in "$base_dir/$category"/*; do
        # Display the original timestamp
        original_timestamp=$(stat -c %y "$file")
        echo "Original timestamp of $file: $original_timestamp"
        
        #Generate a random date in the last 10 days and change the timestamp
        rand_time=$(date -d "$((RANDOM % 10)) days ago $((RANDOM % 24)) hour $((RANDOM % 60)) minute" +"%Y%m%d%H%M")
        touch -t "$rand_time" "$file"
        
        #Display the modified timestamp
        modified_timestamp=$(stat -c %y "$file")
        echo "Modified timestamp of $file: $modified_timestamp"
    done
done
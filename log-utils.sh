#!/bin/bash

function print_disk_space {
	containers=$(docker ps | awk '{if(NR>1) print $NF}')
	host=$(hostname)
  
	for container in $containers
	do
	  echo "Container: $container"
	  percentages=($(docker exec $container /bin/sh -c "df -h | grep -vE '^Filesystem|shm|boot' | awk '{ print +\$5 }'"))
	  mounts=($(docker exec $container /bin/sh -c "df -h | grep -vE '^Filesystem|shm|boot' | awk '{ print \$6 }'"))

	  for index in ${!mounts[*]}; do
	    echo "Mount ${mounts[index]}: ${percentages[index]}%"

	    if (( ${percentages[index]} > 70 )); then
	      message="[ERROR] At $host and Docker container $container the mount ${mounts[index]} is at ${percentages[index]}% of its disk space. Please check this."
	      echo $message
	      echo $message | mail -s "Docker container $container at $host is out of disk space" "r.sonke@maxxton.com"
	    fi
	  done
	  echo ================================
	done
}

function log {
		containers=$(docker ps --format "{{.ID}}")
		container_names=$(docker ps --format "{{.Image}}")
	osascript <<-EOF
    	set containers to the words of "$containers[@]"
    	set container_names to the paragraphs of "$container_names[@]"
    	set docker_command to "docker logs --follow "

	    tell application "iTerm2"
	        activate
	        tell current window
	        	create tab with default profile
	    	end tell
	    	
	        set myterm to (current window)

	        tell myterm
	            launch session "Default Session"

	        set counter_of_containers to count of containers
	        set y to counter_of_containers / 2
	        repeat with x from 1 to y
	        	# split vertically
            	tell application "System Events" to keystroke "d" using command down
	            delay 0.5
	            # previus panel
	            tell application "System Events" to keystroke "[" using command down
	            delay 0.5
	            # split horizontally
	            tell application "System Events" to keystroke "d" using {shift down, command down}
	            delay 0.5
	            # next panel
	            tell application "System Events" to keystroke "]" using command down
	            delay 0.5
            end repeat
         
	        set n to count of containers
            repeat with i from 1 to n
	                # next panel
	                tell application "System Events" to keystroke "]" using command down
	                delay 0.5
	                tell the current session to set name to (item i of container_names)
	                tell the current session to write text (docker_command & item i of containers)
	                delay 0.5
	            end repeat
	        end tell

	        tell application "System Events" to keystroke "]" using command down
            delay 0.5
            tell current window to close current session

	    end tell  
	EOF
}


function help {
	echo "Provide arg one of:"
	echo "-d | --disk-space - lists disk space for running containers"
	echo "-h | --help - shows this guide"
}


while [[ $# -gt 0 ]]; do
    case $1 in
        -d|--disk-space)
			print_disk_space
			shift
		exit 1;;
		-h|--help) 
			help
			shift
		exit 1;;
		-l|--log) 
			log
			shift
		exit 1;;
		*) help
		exit 1;;
    esac
done
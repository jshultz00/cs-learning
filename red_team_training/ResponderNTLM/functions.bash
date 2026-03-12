#!/usr/bin/bash

cr_checkprocess () {
	if [[ -z "${1}" || -z "${2}" || -z "${3}" ]]; then
        echo ""
        echo "Usage: cr_checkprocess hostname search_term seconds_to_sleep"
        echo ""
        echo "Example: cr_checkprocess hn-wks-01 xcopy 10"
        echo ""
        echo "The command above will check if \"xcopy\" is running on hn-wks-01. If so, it will sleep for 10 seconds and check again until it has completed."
        echo ""
        exit 1
	fi

	while [[ true ]]; do
		sudo salt "${1}" ps.pgrep "${2}" | grep None 
		if [[ $? -eq 0 ]]; then
			sleep ${3}
			echo "..."
			continue
		else 
			echo "${1} is running."
			sleep 2
			echo ""
			break
		fi
	done
}

cr_checkfile () {
	if [[ -z "${1}" || -z "${2}" || -z "${3}" ]]; then
		echo ""
		echo "Usage: cr_checkfile hostname filename seconds_to_sleep"
		echo ""
		echo 'Example: cr_checkfile hn-wks-01 "c:\Program Files\feefee.exe" 10'
		echo ""
		echo "The command above will check for the file c:\Program Files\feefee.exe on hn-wks-01 every 10 seconds."
		echo ""
		exit 1
	fi

	while true; do
		sudo salt "${1}" file.access "${2}" f | grep True

		if [[ $? -ne 0 ]]; then
			sleep "${3}"
			echo "..."
			continue
		else
			echo "${2} Found!"
			echo ""
			break
		fi
	done
}

# Function to copy a file to a target system and confirm via SHA256 checksum
function copy_file_to_target() {
    local source_file_path="$1"
    local target_system="$2"
    local target_file_path="$3"
    file_hash=`sha256sum "$source_file_path" | awk '{print $1}'`
    file_name=$(basename "$source_file_path")
    echo "    - Copying $file_name to $target_file_path on $target_system..."
    sudo cp "$source_file_path" /srv/salt
    sudo salt "$target_system" cp.get_file salt://"$file_name" "$target_file_path" > /dev/null 2>&1
    echo "    - Confirming SHA256 checksum of $target_file_path on $target_system..."
    if [ "$(sudo salt "$target_system" hashutil.digest_file "$target_file_path" checksum=sha256 | grep -o $file_hash)" != "$file_hash" ]; then
        echo "[!] SHA256 checksum does not match!"
        echo "Exiting..."
        exit 1
    else
        echo "    - SHA256 checksum matches!"
        echo "    - $file_name copied to $target_file_path on $target_system successfully."
    fi
}

# Function to confirm connectivity to Salt target
function confirm_salt_connectivity() {
    local target_salt_name="$1"
    if [ "$(sudo salt "$target_salt_name" test.ping | grep -o "True")" = "True" ]; then
        echo "    - Salt connectivity confirmed!"
    else
        echo "[!] Unable to connect to Salt target \"$target_salt_name\"!"
        echo "Exiting..."
        exit 1
    fi
}
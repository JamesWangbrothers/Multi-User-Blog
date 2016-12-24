# Multi User Blog
Using Google App Engine for the web server host and database connection, and Jinja2 for the html templates. This project is designed to create a simple multi user blog. Users should be able to create account with login and logout functionality, as well as editing and commenting on post. Not registered users can only be able to read the blogs, but no authorization on editing or delete the post. Only registered users can leave a comment. The [live](https://digital-shadow-666.appspot.com) version of the project is listed below.

Application Website: https://digital-shadow-666.appspot.com

### how to run the the App
1. Clone the project (git clone https://github.com/sxw031/Multi-User-Blog.git)
2. Install Google App Engine
3. Import the application into the Google App Engine laucher.
4. Click on run button, or open command prompt in project folder and run following command: $dev_appserver.py .
5. App will start running on configured port.

### Set up the computer enviornment
1. [Install Python](https://www.python.org/downloads/) if necessary.
2. [Install Google App Engine SDK.](https://cloud.google.com/appengine/downloads)
3. Open GoogleAppEngineLauncher.
4. Sign Up for a Google App Engine Account.
5. Create a new project in Google’s Developer Console using a unique name.
6. Create a new project from the file menu and choose this project's folder.
7. Deploy this project by pressing deploy in GoogleAppEngineLauncher.
8. When developing locally, click “Run” in GoogleAppEngineLauncher and visit localhost:Port in your favorite browser, where Port is the number listed in GoogleAppEngineLauncher’s table under the column Port.








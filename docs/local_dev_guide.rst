Getting Started with CommCare Form Submissions
==============================================

Prerequisites
-------------

- You have followed the `CommCare HQ "Getting Started" guide <https://raw.githubusercontent.com/dimagi/commcare-hq/master/DEV_SETUP.md>`_ to set up a local development environment.
- You have the CommCare Android app installed on an Android device.

1. Expose CommCare HQ to the Public Web
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

To allow your Android device to communicate with the local CommCare HQ instance, you need to expose it to the public web using Nginx. For detailed instructions and advanced tips on exposing your local environment, refer to the `detailed instructions and advanced tips <https://github.com/dimagi/commcare-hq/blob/425893628254b119602e00b35d0ab761488ff359/corehq/apps/builds/README.rst>`_.

- Install Nginx
- Add the CommCare HQ Nginx config to your Nginx config file:

  - Edit ``/etc/nginx/nginx.conf``
  - At the bottom of the ``http{}`` block, add: ``include /path/to/commcarehq/deployment/nginx/cchq_local_nginx.conf;``

- Start Nginx: ``sudo nginx``
- Set ``BASE_ADDRESS`` in ``localsettings.py`` to your local IP.
- Modify ``cchq_local_nginx.conf`` to use your IP as the ``server_name``.
- Reload Nginx config: ``sudo nginx -s reload``

2. Create a Mobile Worker
~~~~~~~~~~~~~~~~~~~~~~~~~

- Login to your local CommCare HQ instance.
- Go to Users -> Mobile Workers -> Create Mobile Worker.
- Enter a username and password for the new mobile worker.

3. Create and Build a New Application
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- Go to Applications -> New Application.
- Choose "Survey" for a basic form app.
- Design your form/survey.
- Publish the application.
- For more guidance on app creation and configuration, refer to the `CommCare onboarding YouTube series <https://www.youtube.com/watch?v=ng4zGf1PGxM&list=PLVmwIEfrcKqkZsRuWVXL-Djsj2JlROvpU&index=1&ab_channel=Dimagi>`_.

4. Set up CommCare Android in Local Environment
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- Fetch the `commcare-android repository <https://github.com/dimagi/commcare-android>`_.
- Ensure you have the latest version of JDK installed
- Open the Project in Android Studio:

  - Click on "Open an Existing Project" or use the "File" > "Open" menu option.
  - Navigate to the directory where you cloned the repository and select the project folder.
  - Android Studio will start importing the project.

- Configure SDK and Gradle:

  - Follow on-screen instructions to install missing SDK components or update Gradle settings.

- Build the Project:

  - Once imported, Android Studio will start syncing Gradle and building the project.

5. Run and Debug the App
~~~~~~~~~~~~~~~~~~~~~~~~

- Select a Run Configuration:

  - Android Studio supports various run configurations, including running the app on an emulator or a connected device. You can configure these options in the toolbar or the "Run" menu.

- Run the App:

  - Click on the green "Run" button or select "Run" from the menu.
  - Choose the device (emulator or physical device) to run the app.
  - Android Studio will compile the code, build the APK, and deploy it to the device.

- Debug the App:

  - To debug the app, set breakpoints in the code by clicking on the left gutter of the editor window next to the line where you want to pause execution.
  - Run the app in debug mode by clicking on the bug icon in the toolbar or selecting the "Debug" option from the "Run" menu.
  - When the app reaches a breakpoint, it will pause execution, and you can inspect variables, step through code, and analyze the app's behavior using the debugging tools provided by Android Studio.

- Monitor Logcat:

  - View system logs and debug messages using Logcat to troubleshoot issues and track app behavior during runtime.

4. Install App on CommCare and Rest Form Submission
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- On the Android device, open CommCare and scan the QR code to install the app you built in step No 3.
- Login to the app using the Mobile Worker credentials created in step No 2.
- Fill out and submit the form.
- Data should be submitted to your local CommCare HQ instance.

You've now completed a basic "hello world" form submission workflow with CommCare HQ! Next steps could include reviewing the `CommCare fundamentals documentation <https://academy.dimagi.com/store>`_ to learn more about app building and data management.

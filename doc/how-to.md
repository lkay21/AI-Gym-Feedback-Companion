# How-To Guide for AI-Feedback-Gym-Companion

---

## How-to AI-Feedback-Gym-Companion for End Users

---

### How to Login

#### Purpose
The purpose of this task is to enter the application via the Login screen as a user account.

#### Preconditions
- A returning user must have the credentials used to create their account initially

#### Steps
1. If you are a returning user, jump to step 7.
2. Under "AI Workout Companion", find and click the link "Sign up"
3. After clicking the link, you should be redirected to a page with 4 input fields: Email, Username, Password, and Confirm Password. Fill out each field accordingly for the user details you wish for the application.
4. Once each field is filled out, click the **SIGN UP** button.
5. Review your email inbox for the email you used in the field for step 3. There should be a "Confirm Your Signup" email from Supabase Auth. You must click the link found in the email to confirm your email address and allow future login into the application.
6. Return to the login page of the application.
7. Enter your username and password.
8. Click the **Sign in** button.

#### Expected Result
- For a returning user, you should now be taken to the **Fitness Dashboard** screen.
- For new users, you should now be taken to a Chatbot screen with a greeting saying "Hello! I'm Fred, your AI Fitness Companion."

---

### How to Generate a Fitness Plan

#### Purpose
The purpose of this task is to generate a Fitness Plan that will map to the rest of the application for the user.

#### Preconditions
- Logged in

#### Steps
1. If you are a new user (this is your first login), jump to step 4.
2. Navigate to the "Chatbot" screen using the application menu. You should see a Chatbot screen with a greeting saying "Hello! I'm Fred, your AI Fitness Companion."
3. Prompt the Chatbot with a phrase indicating a wish to update your current fitness plan.
4. The Chatbot will ask you a series of questions pertaining to your fitness, experience, and health. Respond accordingly.

#### Expected Result
You will now have a current version of your Fitness Plan that can be seen mapped onto your calendar in the **Snapshot** page, selectable from the application menu.

---

### How to Generate a Form Score for a Given Exercise

#### Purpose
To get a normalized score (0–100) and insights on a selected exercise's form for an example "one-rep" video uploaded by the user.

#### Preconditions
- Logged in
- Have a pre-recorded video performing a target exercise, ensuring the video is only of doing one repetition

#### Steps
1. Login to the application and navigate to **Fitness Dashboard**.
2. Find and click the **Upload Video** button within the "Form Score" block. You should be immediately directed to a list of targeted exercises.
3. Click on the targeted exercise you would like to get a form score on. You should be immediately directed to a "Record Video" screen.
4. Click on the **Upload Video** button. Your system file directory will open automatically. Select the pre-recorded video of yourself performing the target exercise for only one repetition. Afterwards, you will be taken back to the "Record Video" screen.
5. Select the **Upload Video** button again. It should turn to "Uploading…". Wait until you are redirected to the **Fitness Dashboard** screen and review your Form Score and Form Insights.

#### Expected Result
A normalized score (0–100) for form performed on the targeted exercise is outputted, along with insights on what went well, what went poorly, and what to focus on for next time.

---

### How to Troubleshoot a Failure

#### Purpose
To have a method of retrial and investigation that will eventually lead to the success of a component of the application that previously failed.

#### Preconditions
- N/A

#### Steps
1. Attempt to replicate the failure, documenting each step taken to reach or attempted to reach the desired endpoint.
2. If the issue is resolved, no further action needed.
3. If the failure persists, note the error and consult the relevant how-to guide for any missteps.
4. If a wrong step is found, correct it and replicate the process again.
5. If the issue is resolved, no further action needed.
6. If the failure still persists, reach out to the application help communication line.
7. Once a response is received from the help line, follow the newly outlined steps.

#### Expected Result
The previously failing component is resolved, either through self-correction via the how-to guide or through escalation to the help communication line.

---

## How-to AI-Feedback-Gym-Companion for Developers

---

### How to Setup a Development Environment

#### Purpose
To enable an environment where a developer is capable of adding to already existing code for various use.

#### Preconditions
- Git installed and available for development in IDE of choice
- Python and Node.js installed

#### Steps
1. Go to [https://github.com/lkay21/AI-Gym-Feedback-Companion](https://github.com/lkay21/AI-Gym-Feedback-Companion)
2. Click the blue **Code** dropdown and copy the HTTPS link shown.
3. Go to your IDE of choice and open a new terminal in the directory where you would like the project.
4. Run `git clone -b develop {HTTPS link}` to clone the `develop` branch inside the target directory, which has the latest working code.
5. Inside the now up-to-date project directory, run `pip install -r requirements.txt` to install backend dependencies.
6. Run `cd mobile` and then run `npm install` for frontend dependencies.

#### Expected Result
A local directory containing project source code and files that can be edited.

---

### How to Configure Environment Variables for Development and Testing

#### Purpose
To securely create and store all necessary external credentials and variables for the application's use to access external services.

#### Preconditions
- Development environment is set up
- Google Cloud AI Account and API Key
- AWS Account
- Supabase Account

#### Steps
1. Locate or create a `.env` file inside the project directory within the development environment.
2. Add your Google Cloud AI API key:
   ```
   GEMINI_API_KEY=key_here
   ```
3. Add your AWS credentials:
   ```
   AWS_REGION=region_here
   AWS_ACCESS_KEY_ID=key_id_here
   AWS_SECRET_ACCESS_KEY=secret_key_here
   DYNAMODB_USER_PROFILES_TABLE=user_profiles
   DYNAMODB_HEALTH_DATA_TABLE=health_data
   ```
4. Add your Supabase credentials:
   ```
   SUPABASE_URL=url_here
   SUPABASE_ANON_KEY=anon_key_here
   ```
5. Save the edited `.env` file and ensure it is included in the `.gitignore` file so credentials are never committed to version control.

#### Expected Result
The `.env` file is correctly populated and the application can run with proper access to all external services needed.

---

### How to Run Application Locally to View Changes in Web Version

#### Purpose
To be able to view a local version of the fully integrated application in a browser.

#### Preconditions
- Development environment is set up

#### Steps
1. Open two separate terminals, each pointed at the root project directory.
2. In one terminal, run `cd mobile` to move into the mobile directory of the project.
3. In the terminal **not** pointed to the mobile directory, run `python -m app.main` and leave it running.
4. In the terminal pointed to mobile, run `npm start` and wait until the Expo server is ready, indicated by a QR code and key binding options.
5. Press `w` to open the web version of the application in your default browser.

#### Expected Result
The application is running in the web version, fully capable of user interaction with the integrated frontend and backend as they are currently written.

---

### How to Update Standard Exercise Video Data

#### Purpose
To update the data file used for exercise form comparison between user videos and "standard" form videos in the CV FormScoring pipeline.

#### Preconditions
- Development environment is set up
- Have a set of separate "standard" form video files

#### Steps
1. Navigate to `./app/exercises/video_in` from inside the project root directory.
2. Upload the set of "standard" form video files into the `video_in` folder.
3. Navigate to the script `openpose.py` inside the exercises folder.
4. After the `if __name__ == "__main__"` conditional, find the source code beginning with 4 lists named `train_exercises`, `train_vids`, `test_exercises`, and `test_vids`.
5. Complete `train_exercises` with the exercises for each form video in the set of video files uploaded in step 2.
6. Complete `train_vids` with the video file names for each form video uploaded in step 2. Ensure that the index of each video file matches the index of the target exercise in `train_exercises`.
7. Past the lists and two assert statements, find the variable `test` and set it equal to `0`.
8. Open a terminal pointed to the exercises folder (`./app/exercises`).
9. Run `python openpose.py`.

#### Expected Result
The data inside `./app/exercises/exercise_data` should be updated for already existing exercises and created for new exercises. The data should present itself as a dictionary of numbers for each joint pertaining to a given exercise.

#### GENAI Statement
For this documentation, GenAI was used to convert an original docx file consisting of this content, into the appropriate .md markdown file. It was also used, on occasion, to ensure there were no holes in described
steps for a given how-to.

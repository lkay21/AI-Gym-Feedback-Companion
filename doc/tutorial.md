# Tutorial – AI Fitness Coach

## Overview  
The **AI Fitness Coach** is a mobile application that helps users improve their workout form and get fitness advice from our AI chatbot companion Fred. This tutorial will explain how to set up the app, navigate its features, and complete a workout form analysis.

By the end of this tutorial, you should be able to:
- Open and navigate from the Sign-in screen, Create an Account screen, Chatbot screen, and the Dashboard screen 
- Upload a workout video  
- Receive AI-generated fitness advice  

---

## Prerequisites  

Make sure you have these before starting:

- **Expo Go** app installed  
- Node.js installed  
- Git installed  
- A code editor like VS Code (optional)
- A stable internet connection  
- Access to the project repository  
 
---

## Setup / Installation  

### Step 1: Clone the Repository  

In your terminal run:

```
git clone https://github.com/lkay21/AI-Gym-Feedback-Companion.git
cd AI-Gym-Feedback-Companion/mobile
```
---
### Step 2: Install Dependencies  

In your terminal run:

```
npm install
```

---
### Step 3: Start the App  

```
python -m app.main
cd AI-Gym-Feedback-Companion/mobile
npx expo start
```
The first command will run the backend, and the other two will start the frontend.

---

### Step 4: Open the host link  

- Open the web browser version to see the website version of the application
- If you have a macbook you should have an iphone simulator where you can open the application there  

The app should now be launched on your device.

---

## First Workflow (Step-by-Step Guide)  

This will be a short tutorial on how to navigate and interact with the app.

---

### Step 1: Sign Up  

When the app loads, you will land on the **Login screen**.
Here you should click **Create an Account** and sign up for an account.
Next you will sign in. 

---

### Step 2: ChatBot LLM Screen Questions 

You will be taken to our chatbot Fred who will ask some questions about your height, weight, and fitness goals. 
After these questions are answered, Fred will generate your first workout plan.  

---

### Step 3: Navigate to the Dashboard Screen  

Click the 3 bars for the Menu dropdown and navigate to the **Dashboard Screen**

Here you will see:

- Your weekly workout summary  
- Form score section  
- Navigation options  

---

### Step 4: Form Analysis 

**On the Dashboard Screen**
- Tap “Upload Video”  
- Choose which exercise you attempting to do
- Select a workout video from your phone  

---

### Step 5: Select Exercise Type  

After recording/uploading:
- Choose the exercise type (e.g., shoulder-flys, bicep curl)  

This helps the AI model understand what to analyze.

---

### Step 6: Submit for Analysis  

- Tap **Upload Video**  
- Wait while the app processes your video  

---

### Step 6: View AI Feedback  

After processing, you will see:
- Form feedback  
- Suggestions for improvement  
- Performance insights  

---

## Expected Results  

After completing this workflow, you should've:

- Successfully run the app on your laptop or iphone simulator 
- Record or upload a workout video  
- Receive a workout plan from Fred
- Navigate between Dashboard and ChatBot screens  

The app should feel smooth and interactive, with clear user workflow.

---

## Troubleshooting  

### App does not start  
- Make sure you ran `npm install`  
- Ensure Node.js is properly installed  
- Try restarting with:
  ```
  npx expo start --clear
  ```

---

### App crashes or freezes  
- Restart Expo  
- Check terminal logs for errors  

---

## GenAI Usage Statement  

GenAI tools were used to help refine the structure of this documentation. All of the steps and details were written by me.

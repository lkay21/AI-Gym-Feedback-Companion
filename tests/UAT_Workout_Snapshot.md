# UAT: Workout Snapshot / Intro-Workout Interaction

## Objective
Validate that users can easily locate their daily workout, interact with the workout snapshot, and correctly input or verify exercise data provided by their fitness plan. The test also ensures users understand how their inputs affect analytics

## Test Process**
1) Login & Setup
  - User logs into the application
  - Confirm that fitness plan has already been generated and assigned
2) Locate Workout Snapshot
  - User navigates through app to find the "Workout Snapshot" or equivalent dashboard
  - Record: time taken to locate the snapshot, number of clicks required
3) Access Daily Workout
  - From workout snapshot, user selects the workout assigned for the current day
  - Confirm workout details (exercises, sets, reps, weights) are visible
4) Interact with Exercise Data
  - User attempts to: input weights/reps for at least one exercise OR verify (confirm/complete) pre-filled workout data
  - Observe: are inputs intuitive, any restrictions (such as locked fields) are clear
5) Submit/Save Workout Data
  - User saves or confirms the workout completion
  - Ensure no errors occur during submission
6) Verify Data Persistence
  - User refreshes or revisits the workout page
  - Confirm that entered or verified data is retained
7) Check Analytics Update
  - Navigate to analytics/dashboard section
  - Verify that: workout data is reflected, metrics (progress, volume, etc.) update accordingly
8) Usability Feedback
  - User provides feedback on: ease of navigation, clarity of input vs. verification actions, overall experience

## Participant Script
**Introduction**
You will be testing a fitness application feature that helps you view and complete your daily workout. Your goal is to find your assigned workout, interact with it by either entering or verifying exercise data, and observe how the system responds. Please think out loud as you go through the process.

**Tasks for Participants**
1) Log into the application
2) Find where your workout for today is located
3) Open today's workout
4) For at least one exercise: enter your own data (such as weights/reps) OR verify the suggested workout data
5) Save or complete the workout
6) Navigate to any analytics or progress section and review changes

**Post-Test Questions**
- How easy was it to find your daily workout?
- Did you understand whether you were supposed to input or verify data?
- Were any steps confusing or unclear?
- How long did the process feel?
- What would you improve?

**Data to Record**
- Time to locate workout snapshot
- Number of clicks to reach workout
- Errors encountered (if any)
- Completion success rate
- User feedback (qualitative)

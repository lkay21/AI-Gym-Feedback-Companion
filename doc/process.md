## Development Processes

**Repository Architecture**
AI_fitness_planner/
├── app/
│   ├── auth/                     # login & signup APIs
│   ├── chatbot/                  # AI coach flow
│   ├── dashboard/                # user dashboard APIs
│   ├── fitness/                  # workout + nutrition logic
│   ├── form_score/               # Form Scoring CV Pipeline  
│   ├── workout_snapshot/         # Workout Snapshot Page  
│   ├── database/                 # db models + connection
│   ├── api/                      # REST endpoints (v1)     
│   └── config.py                 # app config
├── mobile/                       # React Native frontend  
│   ├── App.tsx
│   ├── package.json
│   ├── assets/
│   └── src/
│       ├── screens/
│       └── services/
├── instance/                     # config + database (gitignored)
├── doc/                          # documentation + design files
├── test/
├── app.py                        # main backend entrypoint
└── requirements.txt

**Branching / Workflow Model**
1) Branching Model 
  - Our team plans on using a Feature Branch Workflow, so all work happens on small specific branches created off “develop”.
  - Team members will open a Pull Request back into “develop” when their assigned task is complete. The PullRequest will need to be reviewed and pass checks.
  - Once we are ready, we will merge “develop” into “main”.
  - Other urgent fixes will branch off of main and merge back into “main” and “develop”.
2) Naming Convention
  - The naming conventions will be clear and use feature/, bugfix/, and hotfix/ prefixes.
  - feature/<area>  → this means adding something new.
  - bugfix/<area>  → this means fixing a bug found during development or testing.
  - hotfix/<area>  → this means that there is an urgent fix for something that is broken in production and is usually branched from main.
  - docs/<short-description>  → this is for documentation only changes (such as api instructions or deployment notes)
3) Main Branches and Purposes
  - main - production-read and stable code only that has been tested.
  - develop - integration branch where completed features accumulate for pending testing and review.

**Code Development & Review Policy**
1) Pull Requests
  - ALL code changes MUST be made via a pull request and NO code changes shall be made directly to the main branch of the repository. 
  - All changes made inside a pull request shall be reasonable in size, quantified by number of lines of code. 
  - Each pull request shall only be related to serving the completion of one defined functionality/sub-functionality. This functionality/sub-functionality must be identifiable upon viewing the pull request.
  - Each pull request must contain the following,
    * A descriptive title
    * A concise but informative description of the request and the functionality being completed. 
    * If it is necessary to provide an image showing how the request affects the project design or user interface, the request must contain such an image.
    * Link to any Github issues related to the above defined functionality
    * Mention to potential reviewers. More often than not, reviewers will be the whole team, but in special cases, there may be a single, specific reviewer required.
2) Code Review
  - For any given pull request, a minimum of ONE team member, that is NOT the author for the change, MUST properly review and approve said change. 
  - For any given pull request, it is expected that it will be given a thorough code review in 48 to 72 hours. 
  - Pull Requests of higher priority or those that satisfy any dependencies shall be given priority for review. 
  - Reviewers must check at a minimum, that the following are up to the team standards in any given request being reviewed,
    * Readability
    * Correctness
    * Test Coverage
    * Performance
    * Security/Dependencies
  - Reviewers MUST remain respectful in their review but shall do their best to provide constructive and thorough reviews before approval.
3) Continuous Integration Checks
  - All CI checks MUST be passed before any code merge.
  - CI checks must include but are not limited to, verification of build, unit and integration testing, code formatting tests, and security/dependency checks.
4) Merging
  - Before a change can officially be merged, the pull request of the change MUST have been successfully reviewed and have passed all required Continuous Integration checks. 
  - Authors of Pull Requests may merge their changes ONLY after successful review and passing of CI checks.
5) Branching
  - The team’s repository will follow a branch naming convention using prefixes feature/, for new features,  bugfix/, for non-critical bug fixes, and hotfix/, for urgent issue resolution.
  - The primary branches in the repository shall be main, which stores stable production-ready code and develop, which is used for ongoing integration.
  - ALL new features, bug-fixes, and hotfixes MUST be developed in separate branches created from develop and have naming(past prefix) related to the issue being completed. 
  - Once a branch’s changes are completed, past review, and its code merged in totality, the branch can safely be deleted.

# UAT: LLM Init Interaction & Fitness Plan Generation

## Scope
Confirm that the user is presented with a conversation between them and an LLM, and can successfully arrive at a generated fitness plan through conversation and completion of onboarding prompts.

## Goal
Affirm that the LLM can hold up and perform as expected in conversation with the user. Validate that the generated fitness plan is reliable, feasible, and aligned with the context provided by the user during the conversation.

## Test Method
Iterative conversations with the LLM from the initial first-login interaction across different user profiles, including:
- Test profiles created specifically for UAT
- Real user test profiles (where available and approved)

## Entry Criteria
- User is logged in.

## Exit Criteria
- User is redirected to the workout calendar page.
- User can visibly see the generated fitness plan mapped out.

## Test Participants
- Developers
- Test users

## Timeline for Execution
Execution and documentation completed within 3 weeks of the Week 8 demonstration.

## Test Scenarios
1) New User - Beginner
   - Limited training history
   - Basic equipment access
   - General fat-loss or consistency goal
2) Intermediate User - Mixed Goals
   - Some resistance training history
   - Gym access
   - Strength + hypertrophy focus
3) Advanced User - Specific Constraints
   - High training age
   - Tight schedule constraints
   - Injury history or movement limitations
4) Real User Validation (if available)
   - Natural language responses with realistic detail and ambiguity

## UAT Execution Steps
1) Login and Start Initial Conversation
   - Confirm first-login flow presents the LLM conversation screen.
   - Verify greeting/onboarding prompt appears without error.
2) Complete Conversational Intake
   - User answers prompts about goals, schedule, equipment, experience, and constraints.
   - Observe if the LLM asks relevant follow-up questions when user context is incomplete.
3) Assess Conversation Quality
   - Evaluate response coherence, context retention, and tone.
   - Verify the LLM does not contradict previously provided user inputs.
4) Trigger Plan Generation
   - Complete required conversation flow and submit.
   - Confirm plan generation starts and completes successfully.
5) Validate Redirect and Plan Visibility
   - Verify redirect to workout calendar page occurs.
   - Confirm generated plan appears mapped out on the calendar.
6) Validate Plan Quality
   - Check whether plan frequency, intensity, and exercise selection align with declared profile inputs.
   - Confirm obvious infeasible recommendations are not present.
7) Collect User Feedback
   - Record qualitative feedback on trust, clarity, and perceived usefulness of generated plan.

## Pass/Fail Criteria
- **Pass**
  - LLM onboarding conversation loads and completes.
  - LLM maintains context across the full intake conversation.
  - Generated plan reflects user-provided goals, constraints, and schedule.
  - User is redirected to workout calendar and sees mapped plan.
- **Fail**
  - Conversation fails to load, breaks, or loses critical user context.
  - Plan generation errors or does not complete.
  - Redirect fails or plan is not visible on calendar.
  - Plan is materially misaligned with provided constraints/goals.

## Data to Record Per Session
- Participant type (dev/test user/real user)
- Profile type (beginner/intermediate/advanced/custom)
- Time to complete onboarding conversation
- Number of conversational turns
- Whether follow-up prompts were appropriate
- Plan generation success/failure
- Redirect success/failure
- Plan visibility success/failure
- Context alignment rating (1-5)
- Feasibility rating (1-5)
- Notes on any hallucinations, contradictions, or unsafe suggestions

## Results Log
| Date | Tester | Profile | Conversation Completed | Plan Generated | Redirected to Calendar | Plan Visible | Alignment (1-5) | Feasibility (1-5) | Issues Found | Status |
|------|--------|---------|------------------------|----------------|------------------------|-------------|------------------|-------------------|-------------|--------|
| YYYY-MM-DD | Name | Beginner / Intermediate / Advanced / Real | Yes/No | Yes/No | Yes/No | Yes/No | X | X | Notes | Pass/Fail |

## Risks and Notes
- Real-user responses can be inconsistent; ensure the LLM handles ambiguity with clarifying follow-up questions.
- Track recurring failure patterns by profile type to isolate prompt or plan-generation logic gaps.
- Escalate any unsafe exercise recommendations immediately.

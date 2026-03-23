# Manual Test Documentation

## General Information
- **Tester Name:** Mythrai Kapidi
- **Date:** 2026-02-08
- **Test Name:** Video Upload Test
- **Component Issue Number:** N/A
- **Build / Commit / PR:** main @ <commit-sha-or-pr-link>

## Environment
- **Device:** Windows 10 laptop
- **Version / Branch:** main
- **Backend (Local/Dev/Prod):** Dev
- **Network:** Wi-Fi

## Purpose
- **User workflow validated (critical?):** Yes  
- **What this test validates:**  
  Validates video upload workflow

## Test Steps

### A) Manual UI Upload (primary)
1. Launch the app and navigate to the **video upload**
2. Select `bicep_curl_user_10s.mp4`(dummy file) from device storage
3. Start upload and wait for it to finish
4. Confirm that the UI shows a success state
5. Confirm backend response shows that file is received

### B) Upload Script (secondary regression path)
1. Run the upload script
   - `python upload_video.py --file bicep_curl_user_10s.mp4 --exercise bicep_curl`
2. Confirm script returns HTTP success
3. Verify the uploaded asset is visible in backend logs

## Expected Results
- **Expected output:**
  - Upload completes without error for a standard small video
  - Backend returns success response like HTTP 200/201
  - No crash, freeze, or unhandled exception

## Actual Results
- **Observed output:**
  - Upload completed
  - UI showed success state and proceeded to next step.
  - Returned HTTP 201 

## Expected vs. Actual Comparison
- **Matches expectation?:** Yes  
- **Differences:** None observed

## Outcome
- **Pass/Fail:** PASS  
- **If failed, severity of failure:** N/A

## Evidence
- **Links:**  
- **Screenshots:**  
  - `upload_success.png` *(dummy image)*
- **Log:**  

## Additional Issues
- **GitHub Issue Link (if created):** N/A  

## Next Steps
- [x] No action needed
- [ ] Create/Update GitHub issue
- [ ] Retest after fix

## Additional Notes
- Repeat every 3–4 weeks or after any changes to upload endpoints

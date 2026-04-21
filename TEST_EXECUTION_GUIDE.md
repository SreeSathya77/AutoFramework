# 🚀 TEST EXECUTION GUIDE - QA QM BOS Regression Framework

## Quick Start Command

### **Run the Login Test with Full Logging:**
```bash
pytest tests/ui/test_login.py -v -s --tb=short
```

---

## 📋 Command Breakdown

| Component | Meaning |
|-----------|---------|
| `pytest` | Test execution framework |
| `tests/ui/test_login.py` | Path to the test file |
| `-v` | Verbose output (shows each test) |
| `-s` | Show print statements and logger output |
| `--tb=short` | Show short traceback for errors |

---

## 🎯 What This Test Will Do

### **Test Sequence:**
1. ✅ Start Chromium browser (non-headless, 500ms slow motion)
2. ✅ Navigate to: http://operator-qa.qmaastech.com/
3. ✅ Fill email: superadmin_qm@yopmail.com
4. ✅ Fill password: Superadmin@1234
5. ✅ Click login button
6. 📸 **[POP-UP CAPTURE ZONE]** Log DOM elements to identify pop-up selector
7. 📸 Take screenshot: `02_Just_After_Login_Click`
8. ⏳ Wait for dashboard URL redirect
9. 📸 Take screenshots and log DOM during dashboard transition
10. 📸 Take final screenshot: `01_Login_Success_Dashboard`
11. ⏸️ **PAUSE**: Browser stays open - Press ENTER to close

---

## 📁 Output Files

After running the test, check these locations:

### **Logs:**
```
logs/execution_YYYYMMDD.log
```
This file will contain:
- ✅ Browser navigation logs
- ✅ Login attempt details
- ✅ **[IMPORTANT]** DOM element snapshots with pop-up selectors
- ✅ Timing information
- ✅ Error messages (if any)

### **Screenshots:**
```
reports/RUN_YYYYMMDD_HHMMSS/screenshots/
├── 01_Login_Success_Dashboard_HHMMSS.png
├── 02_Just_After_Login_Click_HHMMSS.png
└── [other screenshots]
```

### **Videos:**
```
reports/RUN_YYYYMMDD_HHMMSS/videos/
├── [recording of entire test]
```

---

## 🔍 Finding Pop-up Information

### **After running the test, look at the log file:**

```bash
# On Windows (Command Prompt)
type logs/execution_20260403.log | findstr /I "popup\|notification\|toast\|success\|DOM SNAPSHOT"

# Or open it directly
notepad logs/execution_YYYYMMDD.log
```

### **Look for these log patterns:**

```
================================================================================
DOM SNAPSHOT AT STAGE: After_Login_Click
================================================================================

✓ Found X element(s) matching selector: div[class*="toast"]
  Element 1:
    - Selector: div[class*="toast"]
    - Visible: True
    - Text: Login successful!
    - HTML: <div class="success-toast">...
```

---

## ✨ Key Features of Enhanced Code

### **Automatic Pop-up Detection:**
The code searches for these common pop-up types:
- Toast notifications (`div[class*="toast"]`)
- Alert boxes (`div[class*="alert"]`)
- Modal dialogs (`div[class*="modal"]`)
- Ant Design messages (`.ant-message`)
- Vuetify snackbars (`.v-snack`)
- Element UI messages (`.el-message`)
- ngx-toastr notifications (`.ng-toast`)
- Custom success messages (`div[class*="success"]`)

### **Multi-Stage Logging:**
- **Before_Login**: Login page HTML snapshot
- **After_Login_Click**: Pop-up appears here! (100ms after click)
- **Before_Dashboard_Navigation**: Just before URL changes
- **After_Dashboard_Loaded**: Final dashboard state

### **Screenshots at Key Moments:**
- Screenshot immediately after login click
- Screenshot when dashboard loads
- Failure screenshots for debugging

---

## 🛠️ Troubleshooting

### **Issue: "fixture 'browser' not found"**
**Solution:**
```bash
pip install -r requirements.txt
playwright install
```

### **Issue: "Connection refused to http://operator-qa.qmaastech.com/"**
**Solution:**
- Check internet connection
- Verify QA URL is accessible
- Check company VPN/proxy settings

### **Issue: "Invalid credentials"**
**Solution:**
- Verify .env file has correct credentials
- Check QA_USERNAME and QA_PASSWORD values in .env

### **Issue: Test runs but pop-up not captured**
**Solution:**
- Open the log file: `logs/execution_YYYYMMDD.log`
- Search for "DOM SNAPSHOT AT STAGE: After_Login_Click"
- This will show all visible elements - one of them is your pop-up!

---

## 📊 Expected Output

### **Console Output Will Show:**
```
============================= test session starts ==============================
platform win32 -- Python 3.11.x, pytest-8.1.1
...
tests/ui/test_login.py::test_user_authentication PASSED                  [100%]

============================== 1 passed in X.XXs ==============================

>>> Test execution finished. Press ENTER in this console to close the browser...
```

### **Log File Will Show:**
```
2026-04-03 12:00:30,123 - INFO - Navigating to Login Page: http://operator-qa.qmaastech.com/
2026-04-03 12:00:35,456 - INFO - Attempting login for user: superadmin_qm@yopmail.com
2026-04-03 12:00:35,789 - INFO - Logging DOM elements BEFORE login click...
================================================================================
DOM SNAPSHOT AT STAGE: Before_Login
================================================================================
...
2026-04-03 12:00:36,012 - INFO - Login button clicked.
2026-04-03 12:00:36,112 - INFO - Logging DOM elements AFTER login click...
================================================================================
DOM SNAPSHOT AT STAGE: After_Login_Click
================================================================================
✓ Found 1 element(s) matching selector: div[class*="success"]
  Element 1:
    - Selector: div[class*="success"]
    - Visible: True
    - Text: Login successful!
    - HTML: <div class="success-notification">Login successful!</div>
...
```

---

## 📝 Next Steps After Running Test

1. **Check Log File** for pop-up selector information
2. **Share Found Selector with Dev Team** for confirmation
3. **Add Confirmed Selector to Code** once identified
4. **Update LoginPage** to capture pop-up screenshot specifically

---

## 🎯 Alternative Commands

### **Run with HTML Report:**
```bash
pytest tests/ui/test_login.py -v -s --html=reports/test_report.html
```

### **Run with Allure Report:**
```bash
pytest tests/ui/test_login.py -v -s --alluredir=reports/allure-results
```

### **Run without pausing browser:**
Edit `conftest.py` and comment out the `input()` line before running.

### **Run with different environment:**
```bash
# Edit .env to change ENV=qa to ENV=dev or ENV=prod, then run
pytest tests/ui/test_login.py -v -s
```

---

## ✅ Verification Checklist

Before running, ensure:
- [ ] `.env` file exists in root directory
- [ ] `requirements.txt` packages installed (`pip install -r requirements.txt`)
- [ ] Playwright browsers installed (`playwright install`)
- [ ] QA URL is accessible from your network
- [ ] You're in the project root directory (`D:\QA_QM_BOS_REG`)

---

**Last Updated:** April 3, 2026
**Status:** Ready for execution


# 🚀 QUICK COMMANDS REFERENCE

## ⚡ IMMEDIATE TEST EXECUTION

### **Step 1: Open Command Prompt and navigate to project**
```cmd
cd D:\QA_QM_BOS_REG
```

### **Step 2: Run the test (MAIN COMMAND)**
```cmd
pytest tests/ui/test_login.py -v -s --tb=short
```

### **Step 3: When browser opens**
- ✅ Watch the automated login
- ✅ Check console for DOM logging
- ✅ Press ENTER when prompted to close browser

---

## 📋 VERIFICATION STEPS

### **Before running test, verify setup:**

```cmd
# Check if .env file exists
dir .env

# Check if requirements installed
pip list | findstr pytest

# Check if Playwright installed
playwright --version

# Verify current directory
cd
```

---

## 📊 AFTER TEST COMPLETES

### **View the logs (find pop-up information here):**
```cmd
# List available log files
dir logs\

# Open latest log file
notepad logs\execution_YYYYMMDD.log

# Search for pop-up information
findstr /I "DOM SNAPSHOT" logs\execution_YYYYMMDD.log
```

### **View screenshots:**
```cmd
# List all reports
dir reports\

# Navigate to latest report
cd reports\RUN_*
dir

# Check screenshots folder
cd screenshots
dir /s
```

### **View videos:**
```cmd
# Navigate to videos
cd reports\RUN_*\videos
dir
```

---

## 🔧 TROUBLESHOOTING COMMANDS

### **If fixtures not found:**
```cmd
pip install -r requirements.txt
playwright install
```

### **If you want to reinstall everything:**
```cmd
pip install --upgrade -r requirements.txt
playwright install --with-deps
```

### **View .env credentials (for verification):**
```cmd
type .env
```

### **Check Python version:**
```cmd
python --version
```

### **Check if port 80/443 accessible:**
```cmd
ping operator-qa.qmaastech.com
```

---

## 📈 ADDITIONAL TEST COMMANDS

### **Run all UI tests:**
```cmd
pytest tests/ui/ -v -s
```

### **Run with HTML report:**
```cmd
pytest tests/ui/test_login.py -v -s --html=reports/report.html
```

### **Run with verbose logging:**
```cmd
pytest tests/ui/test_login.py -vv -s --tb=long
```

### **Run without pausing browser (edit conftest.py first):**
```cmd
pytest tests/ui/test_login.py -v -s --tb=short
```

---

## 💾 FILE LOCATIONS

| Item | Location |
|------|----------|
| Main Test | `tests/ui/test_login.py` |
| Login Page Object | `src/pages/login_page.py` |
| Logs | `logs/execution_YYYYMMDD.log` |
| Screenshots | `reports/RUN_*/screenshots/` |
| Videos | `reports/RUN_*/videos/` |
| Config | `config/config.yaml` |
| Credentials | `.env` |

---

## 🎯 EXPECTED RESULT

✅ **SUCCESS:**
- Test passes
- Browser opens and closes automatically
- Screenshots saved to `reports/RUN_*/screenshots/`
- Logs contain DOM snapshots with pop-up information
- Log file shows: "✓ Found X element(s) matching selector: ..."

❌ **FAILURE:**
- Check log file: `logs/execution_YYYYMMDD.log`
- Look for error messages
- Verify credentials in `.env`
- Check if QA URL is accessible

---

**READY TO START? Run this command:**
```cmd
cd D:\QA_QM_BOS_REG && pytest tests/ui/test_login.py -v -s --tb=short
```



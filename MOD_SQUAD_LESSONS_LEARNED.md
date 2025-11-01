# MOD SQUAD Protocol Upgrades - Lessons from WolfPackAI
**Date:** October 30, 2025  
**Source:** WolfPackAI Implementation & Debugging Session

---

## 🎓 CRITICAL LESSONS & PROTOCOL ENHANCEMENTS

### Issue 1: Configuration Changes Not Reflected in Running Services
**Problem:** Changed appsettings.json (added 15 models) but services still showed 1 model  
**Root Cause:** Running containers use OLD config loaded at startup  
**Impact:** Users think changes didn't work, waste time debugging  

**NEW MOD SQUAD RULE:**
```markdown
## Service Restart Validation (MANDATORY)

After ANY configuration change:
1. STOP all running containers: `docker stop $(docker ps -q)`
2. REBUILD application: `dotnet build --no-incremental`
3. VERIFY config files regenerated (check timestamps)
4. RESTART services with new config
5. VALIDATE changes applied: query service APIs
6. NEVER assume config changes apply to running services

Pre-commit hook MUST warn:
"⚠️  Config changed. Running services need restart to apply changes."
```

---

### Issue 2: Generated Config Files Not Updated
**Problem:** `litellm-config.yaml` showed 1 model despite 15 in appsettings.json  
**Root Cause:** Config generation happens at AppHost startup, not build time  
**Impact:** LiteLLM loads incomplete configuration  

**NEW MOD SQUAD RULE:**
```markdown
## Generated File Validation (MANDATORY)

For ANY generated config file:
1. IDENTIFY source file (e.g., appsettings.json)
2. IDENTIFY generated file (e.g., litellm-config.yaml)
3. After source change: RUN generator (dotnet run or specific command)
4. VERIFY generated file contents match source
5. CHECK file timestamps (generated should be NEWER than source)
6. FAIL validation if generated file is stale

Add to repo_audit.py:
```python
def check_generated_files_freshness():
    """Verify generated files are newer than their sources."""
    mappings = {
        "WolfPackAI.AppHost/appsettings.json": "litellm-config.yaml",
        # Add more mappings per project
    }
    for source, generated in mappings.items():
        if os.path.exists(source) and os.path.exists(generated):
            source_time = os.path.getmtime(source)
            gen_time = os.path.getmtime(generated)
            if source_time > gen_time:
                error(f"STALE: {generated} older than {source}. Regenerate required!")
```
```

---

### Issue 3: Multi-Section Config Consistency Not Validated
**Problem:** Changed port in `services.dashboard.url` but not in `browser_tests.scenarios[].url`  
**Root Cause:** Same config file, different nested sections, no cross-validation  
**Impact:** Browser tests fail with wrong URL  

**NEW MOD SQUAD RULE:**
```markdown
## Cross-Section Config Validation (MANDATORY)

For config files with multiple sections referencing same entities:
1. EXTRACT all service names (dashboard, litellm, openwebui, etc.)
2. SCAN all sections for each service name
3. COMPARE ports/URLs across ALL sections
4. FLAG inconsistencies as CRITICAL
5. BLOCK commit until all references match

Enhanced check_port_url_consistency():
- Scan services{} section
- Scan browser_tests.scenarios[] section  
- Scan health_checks section
- Cross-reference ALL mentions of same service
- Flag if ANY port/URL differs
```

---

### Issue 4: Model Count vs Configuration Mismatch
**Problem:** Configured 15 models but service only loads 1  
**Root Cause:** No validation that runtime matches configuration  
**Impact:** Users expect 15 models, see 1, think system is broken  

**NEW MOD SQUAD RULE:**
```markdown
## Runtime Configuration Validation (MANDATORY)

After service startup:
1. QUERY service API for actual loaded config
2. COMPARE with expected config from files
3. CHECK model count: actual vs configured
4. VERIFY each model is accessible
5. FAIL health check if mismatch detected

Add to health_check.py:
```python
def validate_litellm_models():
    """Verify LiteLLM loaded all configured models."""
    # Read appsettings.json ModelList length
    expected_count = len(config["LiteLLM"]["ModelList"])
    
    # Query LiteLLM /models API
    response = requests.get("http://localhost:4000/models", 
                           headers={"Authorization": f"Bearer {master_key}"})
    actual_models = response.json()["data"]
    actual_count = len(actual_models)
    
    if actual_count != expected_count:
        CRITICAL_ERROR(f"Model mismatch! Configured: {expected_count}, Loaded: {actual_count}")
        return False
    
    # Verify each configured model is in loaded list
    for model in expected_models:
        if model not in actual_models:
            CRITICAL_ERROR(f"Model {model} configured but not loaded!")
    
    return True
```
```

---

### Issue 5: Windows Encoding Issues Not Caught Pre-commit
**Problem:** Emojis in Python scripts cause Unicode errors on Windows  
**Root Cause:** cp1252 encoding can't handle Unicode emojis  
**Impact:** Scripts fail at runtime with cryptic errors  

**NEW MOD SQUAD RULE:**
```markdown
## Windows Compatibility Validation (MANDATORY)

All Python scripts MUST:
1. NO EMOJIS anywhere in print() statements
2. Use ASCII-safe markers: [OK], [FAIL], [WARN], [INFO]
3. Use datetime.now(timezone.utc) not datetime.utcnow()
4. Test on Windows before committing

Pre-commit hook MUST scan:
```python
def check_windows_compatibility():
    """Scan Python files for Windows incompatible patterns."""
    issues = []
    for py_file in Path(".").rglob("*.py"):
        content = py_file.read_text(encoding='utf-8')
        
        # Check for emojis (Unicode > U+007F)
        if re.search(r'[^\x00-\x7F]', content):
            issues.append(f"{py_file}: Contains non-ASCII characters (emojis?)")
        
        # Check for deprecated datetime
        if 'datetime.utcnow()' in content:
            issues.append(f"{py_file}: Uses deprecated datetime.utcnow()")
        
    return issues
```
```

---

### Issue 6: No Visibility Into Console Errors Until Manual Test
**Problem:** User sees console errors in browser but MOD SQUAD didn't detect  
**Root Cause:** Browser tests run but don't capture ACTUAL browser console  
**Impact:** Issues slip through to production  

**NEW MOD SQUAD RULE:**
```markdown
## Enhanced Browser Error Capture (MANDATORY)

browser_mod.py MUST capture:
1. ALL console messages (log, warn, error, info)
2. ALL network requests with status codes
3. Specific 403/401/500 detection
4. Failed resource loads (CSS, JS, images)
5. CORS preflight failures
6. Screenshot on EVERY error

Enhanced implementation:
```python
def test_scenario_enhanced(browser, scenario):
    page = browser.new_page()
    
    # Capture EVERYTHING
    all_console = []
    all_network = []
    
    page.on("console", lambda msg: all_console.append({
        "type": msg.type,
        "text": msg.text,
        "location": msg.location
    }))
    
    page.on("response", lambda resp: all_network.append({
        "url": resp.url,
        "status": resp.status,
        "method": resp.request.method
    }))
    
    page.on("requestfailed", lambda req: all_network.append({
        "url": req.url,
        "failure": req.failure
    }))
    
    # Navigate and analyze
    response = page.goto(url)
    
    # Report ALL console messages (not just errors)
    # Flag 403, 401, 500 specifically
    # Save detailed report with screenshots
```
```

---

### Issue 7: Port Consistency Missed Nested Config
**Problem:** Port changed in one section, missed in browser_tests.scenarios  
**Root Cause:** Search-and-replace not deep enough  
**Impact:** Tests use wrong URL, fail mysteriously  

**ENHANCED MOD SQUAD RULE:**
```markdown
## Deep Config Scanning (MANDATORY)

When changing ANY port or URL:
1. Use AST/JSON parsing, not just text search
2. Scan ENTIRE config tree recursively
3. Find ALL references regardless of nesting depth
4. Generate list of ALL files/locations
5. Propose atomic commit changing ALL occurrences
6. Run port_consistency check BEFORE commit
7. BLOCK if any inconsistency remains

Implementation:
```python
def find_all_port_references(port_number, root_dir="."):
    """Recursively find ALL references to a port in configs."""
    references = []
    
    for json_file in Path(root_dir).rglob("*.json"):
        with open(json_file) as f:
            data = json.load(f)
        
        # Recursive JSON traversal
        def traverse(obj, path=""):
            if isinstance(obj, dict):
                for key, value in obj.items():
                    new_path = f"{path}.{key}" if path else key
                    traverse(value, new_path)
            elif isinstance(obj, list):
                for i, item in enumerate(obj):
                    traverse(item, f"{path}[{i}]")
            elif isinstance(obj, str):
                if f":{port_number}" in obj or f'"{port_number}"' in obj:
                    references.append({
                        "file": json_file,
                        "path": path,
                        "value": obj
                    })
        
        traverse(data)
    
    return references
```
```

---

## 🔧 UPGRADED MOD SQUAD PROTOCOL (v2.0)

### Pre-Commit Checks (Enhanced):
```bash
1. Secrets scan (existing)
2. Config validation (existing)  
3. Port consistency (existing)
4. Windows compatibility (NEW)
5. Generated file freshness (NEW)
6. Cross-section consistency (NEW)
7. Service restart warning (NEW)
```

### Health Check (Enhanced):
```bash
1. Service endpoint health (existing)
2. Response time P95/P99 (existing)
3. Model availability count (NEW)
4. Config-vs-runtime validation (NEW)
5. Port binding validation (NEW)
```

### Browser Tests (Enhanced):
```bash
1. Page load validation (existing)
2. Console error detection (enhanced - ALL messages)
3. Network request monitoring (enhanced - ALL requests)
4. 403/401/500 specific detection (NEW)
5. CORS failure detection (NEW)
6. Interactive UI testing (NEW)
7. Screenshot diff comparison (NEW)
```

---

## 📊 MOD SQUAD v2.0 File Structure

```
project-root/
├── mod_squad.config.json              # Enhanced with validation rules
├── scripts/
│   ├── health_check.py                # + model validation
│   ├── browser_mod.py                 # + enhanced error capture
│   ├── repo_audit.py                  # + all new checks
│   ├── config_validator.py            # NEW: deep config validation
│   └── manage_models.ps1              # NEW: model management
├── .cursorrules-modsquad              # Updated protocol
└── docs/mod-squad/
    ├── LESSONS_LEARNED.md             # This file
    └── UPGRADE_GUIDE.md               # How to apply v2.0
```

---

## ✅ APPLY THESE UPGRADES TO:

- ✅ WolfPackAI (apply fixes now)
- ✅ PaiiD (copy enhanced protocol)
- ✅ Global Cursor rules (C:\Users\SSaint-Cyr\.cursorrules-modsquad)
- ✅ mod.plan.md (update with v2.0 rules)

---

**These lessons are now PERMANENT in your MOD SQUAD protocol.**


# 🧪 Manual Testing Guide for Excel Sheet Selection

## Testing Environment Setup ✅

### Containers Status:
- ✅ **MongoDB**: Running on port 27017
- ✅ **Backend API**: Running on port 8000  
- ✅ **Frontend**: Running on port 3000
- ✅ **All containers**: Successfully built and started

### Test Files Available:
- ✅ `test_files/multi_sheet_test.xlsx` - 3 sheets (Employees, Products, Sales_Data)
- ✅ `test_files/single_sheet_test.xlsx` - 1 sheet (Data)
- ✅ `test_files/special_chars_test.xlsx` - 3 sheets with special characters

---

## Manual Testing Checklist

### 1. Frontend Access 🌐
- [ ] Open browser to `http://localhost:3000`
- [ ] Verify application loads without errors
- [ ] Check console for any JavaScript errors

### 2. Authentication Testing 🔐
- [ ] Test login functionality
- [ ] Verify admin mode toggle works
- [ ] Ensure file upload is disabled without authentication

### 3. Single-Sheet Excel Testing 📄
**File**: `test_files/single_sheet_test.xlsx`
- [ ] Select the single-sheet Excel file
- [ ] Verify NO sheet selection dropdown appears
- [ ] Confirm upload works normally (no extra steps)
- [ ] Check that data processes correctly

### 4. Multi-Sheet Excel Testing 📚
**File**: `test_files/multi_sheet_test.xlsx`
- [ ] Select the multi-sheet Excel file
- [ ] Verify sheet selection dropdown appears
- [ ] Check that all sheets are listed: "Employees", "Products", "Sales_Data"
- [ ] Verify upload button is disabled until sheet is selected
- [ ] Test selecting different sheets
- [ ] Complete upload with each sheet and verify data

### 5. Special Characters Excel Testing 🔤
**File**: `test_files/special_chars_test.xlsx`
- [ ] Select the special characters Excel file
- [ ] Verify sheet names display correctly:
  - "Data & Info"
  - "Products (2024)" 
  - "Sales-Report_Q1"
- [ ] Test upload with each sheet

### 6. Error Handling Testing ⚠️
- [ ] Try uploading non-Excel files (should work normally)
- [ ] Test with corrupted Excel file
- [ ] Verify proper error messages
- [ ] Check network error handling

### 7. UI/UX Testing 🎨
- [ ] Verify loading states appear during sheet detection
- [ ] Check dropdown styling matches application theme
- [ ] Test responsive design on different screen sizes
- [ ] Confirm form validation prevents submission without sheet selection

### 8. API Testing (Optional) 🔧
Using browser developer tools or Postman:
- [ ] Test `/excel-sheets` endpoint with authentication
- [ ] Verify `/upload` endpoint accepts `sheet_name` parameter
- [ ] Check proper JSON responses

---

## Expected Behaviors

### ✅ Correct Behavior:
- **Single-sheet files**: No dropdown, direct upload
- **Multi-sheet files**: Dropdown appears, sheet selection required
- **Loading states**: Brief "Loading sheets..." message
- **Form validation**: Upload disabled until sheet selected
- **Error handling**: Clear error messages for issues

### ❌ Issues to Watch For:
- Dropdown not appearing for multi-sheet files
- Sheet names not loading correctly
- Upload proceeding without sheet selection
- JavaScript errors in console
- API authentication failures
- Styling inconsistencies

---

## Quick Testing Commands

### Check Container Status:
```powershell
docker-compose ps
```

### View Backend Logs:
```powershell
docker logs risk_app_backend --tail=20
```

### View Frontend Logs:
```powershell
docker logs risk_app_frontend --tail=10
```

### Restart Containers (if needed):
```powershell
docker-compose restart
```

---

## Test Data Validation

After successful uploads, verify:
- [ ] Correct number of rows processed
- [ ] Column names match selected sheet
- [ ] Data types preserved correctly
- [ ] No data corruption or loss

---

## Performance Notes
- Sheet detection should complete within 1-2 seconds
- File uploads should not be noticeably slower
- No memory leaks or performance degradation

---

## 🎯 Success Criteria
✅ All test scenarios pass without errors  
✅ User experience is smooth and intuitive  
✅ No regression in existing functionality  
✅ Excel sheet selection works as designed

Happy Testing! 🚀
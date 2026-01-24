@echo off
cd /d "c:\Users\User\arifOS\arifos\core"

REM 1. Create clean landing zone
if exist "metabolism_final" rmdir /s /q "metabolism_final"
mkdir "metabolism_final"

REM 2. Copy ONLY the 11 Constitutional Files + Init
copy "metabolism\__init__.py" "metabolism_final\" >nul
copy "metabolism\000_void.py" "metabolism_final\" >nul
copy "metabolism\111_sense.py" "metabolism_final\" >nul
copy "metabolism\222_reflect.py" "metabolism_final\" >nul
copy "metabolism\333_reason.py" "metabolism_final\" >nul
copy "metabolism\444_evidence.py" "metabolism_final\" >nul
copy "metabolism\555_empathize.py" "metabolism_final\" >nul
copy "metabolism\666_align.py" "metabolism_final\" >nul
copy "metabolism\777_forge.py" "metabolism_final\" >nul
copy "metabolism\888_judge.py" "metabolism_final\" >nul
copy "metabolism\889_proof.py" "metabolism_final\" >nul
copy "metabolism\999_vault.py" "metabolism_final\" >nul

REM 3. Swap Directories (The Switch)
REM Rename current mess to trash
ren "metabolism" "metabolism_trash_%RANDOM%"

REM Rename clean landing zone to production
ren "metabolism_final" "metabolism"

REM 4. Cleanup Trash (Best Effort)
REM If this fails due to locks, at least the MAIN folder is clean
rmdir /s /q "metabolism_trash_*" 

echo Swap Logic Completed

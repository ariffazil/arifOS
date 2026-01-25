@echo off
cd /d "c:\Users\User\arifOS\arifos\core"

mkdir metabolism_clean 2>nul

copy "metabolism\000_void.py" "metabolism_clean\"
copy "metabolism\111_sense.py" "metabolism_clean\"
copy "metabolism\222_reflect.py" "metabolism_clean\"
copy "metabolism\333_reason.py" "metabolism_clean\"
copy "metabolism\444_evidence.py" "metabolism_clean\"
copy "metabolism\555_empathize.py" "metabolism_clean\"
copy "metabolism\666_align.py" "metabolism_clean\"
copy "metabolism\777_forge.py" "metabolism_clean\"
copy "metabolism\888_judge.py" "metabolism_clean\"
copy "metabolism\889_proof.py" "metabolism_clean\"
copy "metabolism\999_vault.py" "metabolism_clean\"
copy "metabolism\__init__.py" "metabolism_clean\"

ren metabolism metabolism_legacy_trash
ren metabolism_clean metabolism

rem Attempt deletion, but don't fail script if locked
rmdir /s /q metabolism_legacy_trash 2>nul

echo Swap Complete > swap_log.txt

@echo off
cd /d "c:\Users\User\arifOS"
rmdir /s /q "arifos\core\metabolism\000_void"
rmdir /s /q "arifos\core\metabolism\111_sense"
rmdir /s /q "arifos\core\metabolism\222_reflect"
rmdir /s /q "arifos\core\metabolism\333_reason"
rmdir /s /q "arifos\core\metabolism\444_evidence"
rmdir /s /q "arifos\core\metabolism\555_empathize"
rmdir /s /q "arifos\core\metabolism\666_align"
rmdir /s /q "arifos\core\metabolism\777_forge"
rmdir /s /q "arifos\core\metabolism\888_judge"
rmdir /s /q "arifos\core\metabolism\889_proof"
del /f /q "arifos\core\metabolism\stage_*.py"
echo Cleanup Complete > cleanup_log.txt

@echo off
REM Compile the Test Case Generation paper with pdflatex.
REM Run this from E:\EB1A_Research\TestCaseGen_Reserach\
REM Requires MiKTeX or TeXLive with pdflatex in PATH
REM and a .venv with matplotlib + numpy installed:
REM     python -m venv .venv
REM     .\.venv\Scripts\activate
REM     pip install -r requirements.txt

SET ROOT=%~dp0
SET TEX=test_case_generation_paper

cd /d "%ROOT%"

echo ============================================
echo  Activating .venv (if present)
echo ============================================
IF EXIST "%ROOT%.venv\Scripts\activate.bat" (
    call "%ROOT%.venv\Scripts\activate.bat"
    echo    .venv activated
) ELSE (
    echo    [warn] .venv not found — using system Python
)

echo.
echo ============================================
echo  Regenerating figures
echo ============================================
python scripts\generate_all_figures.py
IF ERRORLEVEL 1 (
    echo    [FAIL] figure generation failed
    goto :end
)

echo.
echo ============================================
echo  Compiling %TEX%.tex
echo ============================================
echo Running pdflatex pass 1...
pdflatex -interaction=nonstopmode %TEX%.tex > nul 2>&1
echo Running pdflatex pass 2...
pdflatex -interaction=nonstopmode %TEX%.tex > nul 2>&1
echo Running pdflatex pass 3...
pdflatex -interaction=nonstopmode %TEX%.tex > nul 2>&1

IF EXIST "%TEX%.pdf" (
    echo   [OK] %TEX%.pdf created
) ELSE (
    echo   [FAIL] %TEX%.pdf NOT created — check %TEX%.log for errors
)

:end
echo.
echo ============================================
echo  Done.
echo ============================================
pause

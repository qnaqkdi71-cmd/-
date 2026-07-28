@echo off
chcp 65001 >nul
cd /d "%~dp0"
title 랭크업 · 구글 SEO 글 자동작성기

echo(
echo ==================================================
echo    랭크업 · 구글 SEO 글 자동작성기 (윈도우)
echo ==================================================
echo(

REM --- 1) Python 확인 ---
set "PYCMD="
py -3 --version >nul 2>&1 && set "PYCMD=py -3"
if not defined PYCMD (
  python --version >nul 2>&1 && set "PYCMD=python"
)
if not defined PYCMD (
  echo [X] Python이 설치되어 있지 않습니다.
  echo     https://www.python.org/downloads/ 에서 설치하세요.
  echo     설치 첫 화면에서 "Add python.exe to PATH" 체크 필수!
  echo(
  pause
  exit /b 1
)

REM --- 2) 가상환경 (최초 1회) ---
if not exist ".venv\Scripts\python.exe" (
  echo [1/3] 최초 준비 - 가상환경 생성 중... 잠시만요.
  %PYCMD% -m venv .venv
  if errorlevel 1 ( echo [X] 가상환경 생성 실패 & pause & exit /b 1 )
)
set "VENVPY=.venv\Scripts\python.exe"

REM --- 3) .env (최초 1회, 메모장으로 키 입력) ---
if not exist ".env" (
  copy ".env.example" ".env" >nul
  echo(
  echo [안내] .env 파일을 만들었습니다. 곧 메모장이 열립니다.
  echo        GEMINI_API_KEY 에 본인 키를 넣고 [저장] 후 메모장을 닫아주세요.
  echo(
  pause
  notepad ".env"
)

REM --- 4) 패키지 설치 ---
echo [2/3] 필요한 패키지 설치 중... (최초엔 몇 분 걸릴 수 있어요)
"%VENVPY%" -m pip install --upgrade pip >nul
"%VENVPY%" -m pip install -r requirements.txt
if errorlevel 1 ( echo [X] 설치 실패 - 인터넷 연결 확인 후 다시 실행하세요. & pause & exit /b 1 )

REM --- 5) 실행 ---
echo(
echo [3/3] 서버 시작! 브라우저에서 http://localhost:8000 이 열립니다.
echo       끄려면 이 검은 창에서 Ctrl + C 를 누르거나 창을 닫으세요.
echo(
start "" http://localhost:8000
"%VENVPY%" -m uvicorn app:app --port 8000

pause

@echo off
title Krishi Mitr - Ollama Local Setup 🌾
echo ====================================================================
echo               Krishi Mitr - Ollama RAG AI Setup Script
echo ====================================================================
echo.
echo [1/3] Checking if Ollama is installed...
where ollama >nul 2>nul
if %errorlevel% neq 0 (
    echo [WARNING] Ollama was not found in your system PATH!
    echo.
    echo Opening https://ollama.com in your browser...
    start https://ollama.com
    echo.
    echo Please download and install Ollama, then run this script again!
    echo.
    pause
    exit /b
)
echo [OK] Ollama is installed!
echo.
echo [2/3] Verifying if Ollama Service is running...
netstat -ano | findstr 11434 >nul
if %errorlevel% neq 0 (
    echo [INFO] Ollama service is not running. Starting it in the background...
    start "" /B ollama serve >nul 2>nul
    echo Waiting for Ollama service to boot up...
    timeout /t 5 >nul
)
echo [OK] Ollama Service is running on http://localhost:11434!
echo.
echo [3/3] Pulling the optimal models for your GTX 1650 Ti GPU...
echo.
echo.  * Model 1: gemma2:2b (Lightweight, elite Hinglish processor)
echo             Fits entirely inside your 4GB VRAM!
echo.
ollama pull gemma2:2b
echo.
echo.  * Model 2: nomic-embed-text (Local text embeddings)
echo.
ollama pull nomic-embed-text
echo.
echo ====================================================================
echo [SUCCESS] Local AI environment is fully ready for Krishi Mitr! 🌾
echo ====================================================================
echo.
echo To run your chatbot:
echo 1. Keep your Ollama desktop app active.
echo 2. Start your Flask application (.venv\Scripts\python app.py).
echo 3. Open http://127.0.0.1:5000/chatbot in your browser!
echo.
pause

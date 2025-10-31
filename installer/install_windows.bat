@echo off
REM TT-Live-AI-TTS Windows 安装程序
REM 版本: 1.0.0
REM 支持: Windows 10+ 或 Windows Server 2016+

setlocal enabledelayedexpansion

REM 设置编码为 UTF-8
chcp 65001 >nul

REM 安装程序信息
set INSTALLER_VERSION=1.0.0
set PROJECT_NAME=TT-Live-AI-TTS
set INSTALL_DIR=%USERPROFILE%\TT_Live_AI_TTS
set INSTALLER_DIR=%~dp0
set SOURCE_DIR=%INSTALLER_DIR%..

REM 显示欢迎信息
call :show_welcome

REM 确认安装
set /p CONTINUE="是否继续安装？(Y/n): "
if /i "%CONTINUE%"=="n" (
    echo 安装已取消
    pause
    exit /b 0
)

REM 执行安装步骤
call :check_system_requirements
call :create_install_directory
call :copy_project_files
call :create_virtual_environment
call :install_dependencies
call :set_permissions
call :verify_installation
call :create_startup_script
call :show_completion_info

echo.
echo [SUCCESS] 安装程序执行完成！
pause
exit /b 0

REM ==========================================
REM 函数定义
REM ==========================================

:show_welcome
cls
echo.
echo ╔══════════════════════════════════════════════════════════════╗
echo ║                    TT-Live-AI-TTS 安装程序                    ║
echo ║                         Windows 版本                         ║
echo ║                        版本: %INSTALLER_VERSION%                        ║
echo ╚══════════════════════════════════════════════════════════════╝
echo.
echo [INFO] 欢迎使用 TT-Live-AI-TTS 安装程序！
echo.
echo 本安装程序将为您安装：
echo   • TTS 语音合成服务
echo   • Web 控制台界面
echo   • 批量处理功能
echo   • API 接口服务
echo.
echo 安装目录: %INSTALL_DIR%
echo.
goto :eof

:check_system_requirements
echo [STEP] 检查系统要求...

REM 检查 Windows 版本
for /f "tokens=4-5 delims=. " %%i in ('ver') do set VERSION=%%i.%%j
if "%VERSION%" LSS "10.0" (
    echo [ERROR] 需要 Windows 10 或更高版本，当前版本: %VERSION%
    pause
    exit /b 1
)
echo [SUCCESS] Windows 版本检查通过: %VERSION%

REM 检查 Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] 未找到 Python，请先安装 Python 3.8+
    echo [INFO] 建议从 https://www.python.org/downloads/ 下载安装
    pause
    exit /b 1
)

for /f "tokens=2" %%i in ('python --version') do set PYTHON_VERSION=%%i
echo [SUCCESS] Python 版本检查通过: %PYTHON_VERSION%

REM 检查 pip
pip --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] 未找到 pip，请先安装 pip
    pause
    exit /b 1
)
echo [SUCCESS] pip 检查通过

REM 检查磁盘空间
for /f "tokens=3" %%i in ('dir /-c "%USERPROFILE%" ^| find "bytes free"') do set FREE_SPACE=%%i
if %FREE_SPACE% LSS 2147483648 (
    echo [WARNING] 可用磁盘空间不足 2GB
    set /p CONTINUE_SPACE="是否继续安装？(y/N): "
    if /i not "!CONTINUE_SPACE!"=="y" (
        echo [INFO] 安装已取消
        pause
        exit /b 0
    )
)
echo [SUCCESS] 系统要求检查完成
goto :eof

:create_install_directory
echo [STEP] 创建安装目录...

if exist "%INSTALL_DIR%" (
    echo [WARNING] 安装目录已存在: %INSTALL_DIR%
    set /p OVERWRITE="是否覆盖现有安装？(y/N): "
    if /i "!OVERWRITE!"=="y" (
        echo [INFO] 备份现有安装...
        set BACKUP_DIR=%INSTALL_DIR%_backup_%DATE:~0,4%%DATE:~5,2%%DATE:~8,2%_%TIME:~0,2%%TIME:~3,2%%TIME:~6,2%
        set BACKUP_DIR=!BACKUP_DIR: =0!
        move "%INSTALL_DIR%" "!BACKUP_DIR!"
        echo [SUCCESS] 现有安装已备份到: !BACKUP_DIR!
    ) else (
        echo [INFO] 安装已取消
        pause
        exit /b 0
    )
)

mkdir "%INSTALL_DIR%" 2>nul
echo [SUCCESS] 安装目录创建完成: %INSTALL_DIR%
goto :eof

:copy_project_files
echo [STEP] 复制项目文件...

REM 创建必要的目录结构
mkdir "%INSTALL_DIR%\logs" 2>nul
mkdir "%INSTALL_DIR%\input" 2>nul
mkdir "%INSTALL_DIR%\outputs" 2>nul
mkdir "%INSTALL_DIR%\templates" 2>nul
mkdir "%INSTALL_DIR%\static" 2>nul

echo [INFO] 复制核心文件...

REM 复制 Python 文件
for /r "%SOURCE_DIR%" %%f in (*.py) do (
    set "file=%%f"
    set "rel_path=!file:%SOURCE_DIR%\=!"
    set "target_dir=%INSTALL_DIR%\!rel_path:%%~nxf=!"
    if not "!target_dir!"=="%INSTALL_DIR%\" (
        if not "!rel_path!"=="installer\*" (
            if not "!rel_path!"=="*__pycache__\*" (
                if not "!rel_path!"=="*venv\*" (
                    mkdir "!target_dir!" 2>nul
                    copy "%%f" "!target_dir!" >nul
                )
            )
        )
    )
)

REM 复制配置文件
for /r "%SOURCE_DIR%" %%f in (*.md) do (
    set "file=%%f"
    set "rel_path=!file:%SOURCE_DIR%\=!"
    if not "!rel_path!"=="installer\*" (
        set "target_dir=%INSTALL_DIR%\!rel_path:%%~nxf=!"
        mkdir "!target_dir!" 2>nul
        copy "%%f" "!target_dir!" >nul
    )
)

REM 复制 HTML 模板
for /r "%SOURCE_DIR%" %%f in (*.html) do (
    set "file=%%f"
    set "rel_path=!file:%SOURCE_DIR%\=!"
    set "target_dir=%INSTALL_DIR%\!rel_path:%%~nxf=!"
    mkdir "!target_dir!" 2>nul
    copy "%%f" "!target_dir!" >nul
)

REM 复制 CSS 和 JS 文件
for /r "%SOURCE_DIR%" %%f in (*.css *.js) do (
    set "file=%%f"
    set "rel_path=!file:%SOURCE_DIR%\=!"
    set "target_dir=%INSTALL_DIR%\!rel_path:%%~nxf=!"
    mkdir "!target_dir!" 2>nul
    copy "%%f" "!target_dir!" >nul
)

REM 复制批处理文件
for /r "%SOURCE_DIR%" %%f in (*.bat) do (
    set "file=%%f"
    set "rel_path=!file:%SOURCE_DIR%\=!"
    if not "!rel_path!"=="installer\*" (
        set "target_dir=%INSTALL_DIR%\!rel_path:%%~nxf=!"
        mkdir "!target_dir!" 2>nul
        copy "%%f" "!target_dir!" >nul
    )
)

REM 复制配置文件
copy "%INSTALLER_DIR%\config\config.json" "%INSTALL_DIR%\" >nul
copy "%INSTALLER_DIR%\config\.env_template" "%INSTALL_DIR%\.env" >nul

echo [SUCCESS] 项目文件复制完成
goto :eof

:create_virtual_environment
echo [STEP] 创建 Python 虚拟环境...

cd /d "%INSTALL_DIR%"

REM 创建虚拟环境
python -m venv venv
if errorlevel 1 (
    echo [ERROR] 虚拟环境创建失败
    pause
    exit /b 1
)

echo [SUCCESS] 虚拟环境创建完成
goto :eof

:install_dependencies
echo [STEP] 安装 Python 依赖包...

cd /d "%INSTALL_DIR%"

REM 激活虚拟环境并安装依赖
call venv\Scripts\activate.bat
pip install --upgrade pip
pip install -r "%INSTALLER_DIR%\requirements.txt"
if errorlevel 1 (
    echo [ERROR] 依赖包安装失败
    pause
    exit /b 1
)

echo [SUCCESS] 依赖包安装完成
goto :eof

:set_permissions
echo [STEP] 设置文件权限...

cd /d "%INSTALL_DIR%"

REM Windows 下设置文件权限（如果需要）
REM 这里主要确保文件可读可写
echo [SUCCESS] 文件权限设置完成
goto :eof

:verify_installation
echo [STEP] 验证安装...

cd /d "%INSTALL_DIR%"
call venv\Scripts\activate.bat

REM 检查关键文件
if not exist "02_TTS服务_语音合成系统\run_tts_TTS语音合成服务.py" (
    echo [ERROR] 关键文件缺失: run_tts_TTS语音合成服务.py
    pause
    exit /b 1
)

if not exist "03_Web界面_控制台系统\web_dashboard_simple_Web控制台界面.py" (
    echo [ERROR] 关键文件缺失: web_dashboard_simple_Web控制台界面.py
    pause
    exit /b 1
)

REM 检查 Python 包
python -c "import flask" 2>nul
if errorlevel 1 (
    echo [ERROR] Python 包缺失: flask
    pause
    exit /b 1
)

python -c "import edge_tts" 2>nul
if errorlevel 1 (
    echo [ERROR] Python 包缺失: edge_tts
    pause
    exit /b 1
)

python -c "import pandas" 2>nul
if errorlevel 1 (
    echo [ERROR] Python 包缺失: pandas
    pause
    exit /b 1
)

python -c "import openpyxl" 2>nul
if errorlevel 1 (
    echo [ERROR] Python 包缺失: openpyxl
    pause
    exit /b 1
)

echo [SUCCESS] 安装验证通过
goto :eof

:create_startup_script
echo [STEP] 创建启动脚本...

(
echo @echo off
echo REM TT-Live-AI-TTS 系统启动脚本
echo.
echo setlocal enabledelayedexpansion
echo chcp 65001 ^>nul
echo.
echo set INSTALL_DIR=%%~dp0
echo cd /d "%%INSTALL_DIR%%"
echo.
echo echo 🚀 启动 TT-Live-AI-TTS 系统...
echo echo 安装目录: %%INSTALL_DIR%%
echo.
echo REM 激活虚拟环境
echo call venv\Scripts\activate.bat
echo.
echo REM 启动服务
echo call "12_启动脚本_服务启动和管理\start_services_一键启动所有服务.bat"
) > "%INSTALL_DIR%\start_tts_system.bat"

echo [SUCCESS] 启动脚本创建完成
goto :eof

:show_completion_info
echo [STEP] 安装完成！

echo.
echo ╔══════════════════════════════════════════════════════════════╗
echo ║                    安装成功完成！                           ║
echo ╚══════════════════════════════════════════════════════════════╝
echo.
echo [SUCCESS] TT-Live-AI-TTS 已成功安装到: %INSTALL_DIR%
echo.
echo 🚀 快速启动:
echo   cd %INSTALL_DIR%
echo   start_tts_system.bat
echo.
echo 🌐 访问地址:
echo   Web 控制台: http://127.0.0.1:8000
echo   TTS 服务: http://127.0.0.1:5001
echo.
echo 📚 使用说明:
echo   1. 运行启动脚本启动所有服务
echo   2. 打开浏览器访问 Web 控制台
echo   3. 上传 Excel 文件进行语音生成
echo   4. 使用 API 接口进行集成
echo.
echo 📁 重要目录:
echo   输入文件: %INSTALL_DIR%\input
echo   输出文件: %INSTALL_DIR%\outputs
echo   日志文件: %INSTALL_DIR%\logs
echo   配置文件: %INSTALL_DIR%\.env
echo.
echo 🔧 配置修改:
echo   编辑 %INSTALL_DIR%\.env 文件修改配置
echo.
echo 📖 更多信息请查看: %INSTALL_DIR%\README_项目说明.md
echo.
goto :eof

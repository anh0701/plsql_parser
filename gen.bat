echo off
echo Running from: %cd%
set JAR_PATH=%USERPROFILE%\.m2\repository\antlr\antlr\4.13.2\antlr-4.13.2-complete.jar

if exist "%JAR_PATH%" (
    java -jar "%JAR_PATH%" -Dlanguage=Python3 PlSqlLexer.g4 -o output
    java -jar "%JAR_PATH%" -Dlanguage=Python3 PlSqlParser.g4 -o output
) else (
    echo ERROR: Cannot find %JAR_PATH%
)

pause
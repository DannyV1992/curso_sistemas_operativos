#!/bin/bash
# cambiar_java.sh - Cambia la versión activa de Java con update-alternatives y JAVA_HOME
# Uso: ./cambiar_java.sh <version>          ej: ./cambiar_java.sh 21
#      ./cambiar_java.sh --listar
#      source ./cambiar_java.sh <version>   (para que JAVA_HOME quede en la terminal actual)
# Firma: Daniel Vásquez González (DannyV1992) - Sistemas Operativos, LEAD University, III Cuat. 2026

if [ $# -ne 1 ]; then
    echo "Uso: $0 <version> | --listar" >&2
    return 1 2>/dev/null || exit 1
fi

if [ "$1" = "--listar" ]; then
    echo "Versiones de Java instaladas:"
    update-alternatives --list java
    return 0 2>/dev/null || exit 0
fi

VERSION="$1"
JAVA_BIN=$(update-alternatives --list java | grep "java-${VERSION}-")

if [ -z "$JAVA_BIN" ]; then
    echo "Error: Java $VERSION no está instalado. Disponibles:" >&2
    update-alternatives --list java >&2
    return 2 2>/dev/null || exit 2
fi

# 1) Cambiar el enlace del sistema /usr/bin/java (y javac si existe)
sudo update-alternatives --set java "$JAVA_BIN"
JAVAC_BIN=$(update-alternatives --list javac | grep "java-${VERSION}-")
[ -n "$JAVAC_BIN" ] && sudo update-alternatives --set javac "$JAVAC_BIN"

# 2) Apuntar JAVA_HOME al JDK elegido
JAVA_HOME="${JAVA_BIN%/bin/java}"
JAVA_HOME="${JAVA_HOME%/jre}"      # Java 8 usa .../jre/bin/java
export JAVA_HOME

echo "JAVA_HOME = $JAVA_HOME"
java --version

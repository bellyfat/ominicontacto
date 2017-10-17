#!/bin/bash

#
# Script de build y deploy para Omnileads
#
# Autor: Federico Peker
# Requiere: virtualenv activado
#
# Forma de uso:
#
#   ./build.sh -i deploy/hosts-virtual-pruebas
#


if [ "$VIRTUAL_ENV" = "" ] ; then
        echo "ERROR: virtualenv (o alguno de la flia.) no encontrado"
        exit 1
fi

set -e

cd $(dirname $0)

TMP=/dev/shm/ominicontacto-build

if [ -e $TMP ] ; then
	rm -rf $TMP
fi

mkdir -p $TMP/ominicontacto
echo "Usando directorio temporal: $TMP/ominicontacto..."

cd ~/ominicontacto

echo "Creando bundle usando git-archive..."
git archive --format=tar $(git rev-parse HEAD) | tar x -f - -C $TMP/ominicontacto

echo "Eliminando archivos innecesarios..."
rm -rf $TMP/ominicontacto/docs
rm -rf $TMP/ominicontacto/deploy
rm -rf $TMP/ominicontacto/run_coverage_tests.sh
rm -rf $TMP/ominicontacto/run_uwsgi.sh

echo "Obteniendo datos de version..."
branch_name=$(git symbolic-ref -q HEAD)
branch_name=${branch_name##refs/heads/}
branch_name=${branch_name:-HEAD}

commit="$(git rev-parse HEAD)"
author="$(id -un)@$(hostname -f)"

echo "Creando archivo de version | Branch: $branch_name | Commit: $commit | Autor: $author"
#cat > $TMP/ominicontacto/version.py <<EOF


# ----------

export DO_CHECKS="${DO_CHECKS:-no}"

echo "Ejecutando Ansible"
ansible-playbook -s /etc/ansible/deploy/main.yml -u freetech --extra-vars "BUILD_DIR=$TMP/ominicontacto" -K


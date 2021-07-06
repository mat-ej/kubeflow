#!/bin/sh
#cleanup
multipass delete --all
echo "instances deleted"
multipass purge
echo "instances purged"
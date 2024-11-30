#!/bin/bash

kubectl delete all -n plebi --all
kubectl delete all -n offloaded-namespace --all
kubectl delete -f permissions.yml
kubectl delete namespace plebi
kubectl delete namespace offloaded-namespace
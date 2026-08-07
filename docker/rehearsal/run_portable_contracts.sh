#!/usr/bin/env bash
set -euo pipefail

: "${OPENMETADATA_BASE_URL:=http://openmetadata-server:8585}"
: "${OM_LOCAL_ADMIN_EMAIL:=admin@open-metadata.org}"
: "${OM_LOCAL_ADMIN_PASSWORD:=admin}"
: "${PRODUCT_REPOSITORY:=https://github.com/easyseop/OpenMetadata.git}"
: "${PRODUCT_COMMIT:=8ac18ad053d9274774e274ba17b35911ac0b9dcb}"
: "${HARNESS_REPOSITORY:=https://github.com/easyseop/openmetadata-test.git}"
: "${HARNESS_REF:=om-1.13.1-rehearsal-runtime-v1}"
: "${DEPLOYED_ARTIFACT_DIGEST:?DEPLOYED_ARTIFACT_DIGEST is required}"
: "${RUNTIME_RUN_ID:=om-1.13.1-portable-runtime}"

rm -rf /work/harness /work/product

git clone --quiet --filter=blob:none --no-checkout \
  "$HARNESS_REPOSITORY" /work/harness

git -C /work/harness fetch --quiet --depth=1 origin "$HARNESS_REF"

git -C /work/harness checkout --quiet --detach "$HARNESS_REF"

git clone --quiet --filter=blob:none --no-checkout \
  "$PRODUCT_REPOSITORY" /work/product

git -C /work/product fetch --quiet --depth=1 origin "$PRODUCT_COMMIT"

git -C /work/product checkout --quiet --detach "$PRODUCT_COMMIT"

python -m pip install --quiet --no-cache-dir -e '/work/harness/harness[runtime,dev]'

python /work/harness/harness/prepare_runtime_contract_environment.py \
  --base-url "$OPENMETADATA_BASE_URL" \
  --product-repo /work/product \
  --artifact-digest "$DEPLOYED_ARTIFACT_DIGEST" \
  --output /work/runtime-contract.env

source /work/runtime-contract.env

cd /work/harness

python harness/om_workflow.py runtime \
  --repo /work/product \
  --version 1.13.1 \
  --artifact-digest "$DEPLOYED_ARTIFACT_DIGEST" \
  --output-dir "/evidence/$RUNTIME_RUN_ID" \
  --run-id "$RUNTIME_RUN_ID"

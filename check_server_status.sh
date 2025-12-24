#!/bin/bash
# Server Status Check Script
# Checks Hetzner server status before deployment to prevent evictions
# Run this before pushing to main branch

set -e

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Server credentials (from rules)
HETZNER_HOST="178.156.162.135"
HETZNER_USER="root"
HETZNER_PASS="rFRLpamP94tC"

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}SERVER STATUS CHECK${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Check if sshpass is available
if ! command -v sshpass &> /dev/null; then
    echo -e "${RED}❌ sshpass not found. Install with: sudo apt-get install sshpass${NC}"
    exit 1
fi

SSH_CMD="sshpass -p '${HETZNER_PASS}' ssh -o StrictHostKeyChecking=no -o ConnectTimeout=10 ${HETZNER_USER}@${HETZNER_HOST}"

echo -e "${BLUE}Connecting to Hetzner server...${NC}"
echo ""

# Check server connectivity
if ! $SSH_CMD "echo 'Connection test'" &>/dev/null; then
    echo -e "${RED}❌ Cannot connect to server${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Server connection successful${NC}"
echo ""

# Check memory usage
echo -e "${BLUE}=== Memory Status ===${NC}"
MEMORY_INFO=$($SSH_CMD "free -h | grep Mem")
MEMORY_USAGE=$($SSH_CMD "free | grep Mem | awk '{printf \"%.0f\", \$3/\$2 * 100}'")
echo "$MEMORY_INFO"
echo "Memory Usage: ${MEMORY_USAGE}%"

if [ "$MEMORY_USAGE" -gt 85 ]; then
    echo -e "${RED}❌ CRITICAL: Memory usage is ${MEMORY_USAGE}% (above 85%)${NC}"
    echo -e "${RED}   DO NOT DEPLOY - Risk of pod evictions${NC}"
    exit 1
elif [ "$MEMORY_USAGE" -gt 75 ]; then
    echo -e "${YELLOW}⚠️  WARNING: Memory usage is ${MEMORY_USAGE}% (above 75%)${NC}"
    echo -e "${YELLOW}   Proceed with caution${NC}"
else
    echo -e "${GREEN}✅ Memory usage OK (${MEMORY_USAGE}%)${NC}"
fi
echo ""

# Check disk usage
echo -e "${BLUE}=== Disk Status ===${NC}"
DISK_INFO=$($SSH_CMD "df -h / | tail -1")
DISK_USAGE=$($SSH_CMD "df / | tail -1 | awk '{print \$5}' | sed 's/%//'")
echo "$DISK_INFO"
echo "Disk Usage: ${DISK_USAGE}%"

if [ "$DISK_USAGE" -gt 90 ]; then
    echo -e "${RED}❌ CRITICAL: Disk usage is ${DISK_USAGE}% (above 90%)${NC}"
    echo -e "${RED}   DO NOT DEPLOY - Risk of disk space issues${NC}"
    exit 1
elif [ "$DISK_USAGE" -gt 80 ]; then
    echo -e "${YELLOW}⚠️  WARNING: Disk usage is ${DISK_USAGE}% (above 80%)${NC}"
    echo -e "${YELLOW}   Proceed with caution${NC}"
else
    echo -e "${GREEN}✅ Disk usage OK (${DISK_USAGE}%)${NC}"
fi
echo ""

# Check for evicted pods
echo -e "${BLUE}=== Pod Eviction Check ===${NC}"
EVICTED_PODS=$($SSH_CMD "kubectl get pods --all-namespaces --field-selector=status.phase=Failed -o json 2>/dev/null | grep -c 'Evicted' || echo '0'")
if [ "$EVICTED_PODS" -gt 0 ]; then
    echo -e "${YELLOW}⚠️  Found ${EVICTED_PODS} evicted pod(s)${NC}"
    echo -e "${YELLOW}   Checking if they're old evictions...${NC}"
    
    # Check if evicted pods are recent (within last hour)
    RECENT_EVICTIONS=$($SSH_CMD "kubectl get pods --all-namespaces --field-selector=status.phase=Failed -o json 2>/dev/null | jq -r '.items[] | select(.status.reason==\"Evicted\") | .metadata.creationTimestamp' 2>/dev/null | wc -l || echo '0'")
    
    if [ "$RECENT_EVICTIONS" -gt 0 ]; then
        echo -e "${RED}❌ CRITICAL: Recent pod evictions detected${NC}"
        echo -e "${RED}   DO NOT DEPLOY - System under memory pressure${NC}"
        exit 1
    else
        echo -e "${YELLOW}   Evicted pods appear to be old (not recent)${NC}"
        echo -e "${YELLOW}   Consider cleaning them up, but deployment should be safe${NC}"
    fi
else
    echo -e "${GREEN}✅ No evicted pods found${NC}"
fi
echo ""

# Check Cortex namespace pods
echo -e "${BLUE}=== Cortex Namespace Status ===${NC}"
CORTEX_PODS=$($SSH_CMD "kubectl get pods -n cortex 2>/dev/null || echo 'NAMESPACE_NOT_FOUND'")
if echo "$CORTEX_PODS" | grep -q "NAMESPACE_NOT_FOUND"; then
    echo -e "${YELLOW}⚠️  Cortex namespace not found (will be created on deployment)${NC}"
else
    echo "$CORTEX_PODS"
    READY_COUNT=$(echo "$CORTEX_PODS" | grep -c "Running" || echo "0")
    TOTAL_COUNT=$(echo "$CORTEX_PODS" | grep -v "NAME" | wc -l || echo "0")
    
    if [ "$TOTAL_COUNT" -gt 0 ]; then
        if [ "$READY_COUNT" -eq "$TOTAL_COUNT" ]; then
            echo -e "${GREEN}✅ All Cortex pods are running (${READY_COUNT}/${TOTAL_COUNT})${NC}"
        else
            echo -e "${YELLOW}⚠️  Some Cortex pods may not be ready${NC}"
        fi
    fi
fi
echo ""

# Check other namespaces (ensure no impact)
echo -e "${BLUE}=== Other Namespaces Status ===${NC}"
OTHER_NAMESPACES=("default" "gabay" "leadfinder" "prism" "sandata")
ALL_NAMESPACES_OK=true

for ns in "${OTHER_NAMESPACES[@]}"; do
    NS_PODS=$($SSH_CMD "kubectl get pods -n ${ns} 2>/dev/null | grep -v 'NAME' | wc -l || echo '0'")
    if [ "$NS_PODS" -gt 0 ]; then
        NS_RUNNING=$($SSH_CMD "kubectl get pods -n ${ns} 2>/dev/null | grep -c 'Running' || echo '0'")
        echo "  ${ns}: ${NS_RUNNING} running pods"
        
        if [ "$NS_RUNNING" -eq 0 ] && [ "$NS_PODS" -gt 0 ]; then
            echo -e "    ${YELLOW}⚠️  Warning: No running pods in ${ns}${NC}"
            ALL_NAMESPACES_OK=false
        fi
    fi
done

if [ "$ALL_NAMESPACES_OK" = true ]; then
    echo -e "${GREEN}✅ Other namespaces appear healthy${NC}"
fi
echo ""

# Check CPU load
echo -e "${BLUE}=== CPU Load ===${NC}"
CPU_LOAD=$($SSH_CMD "uptime | awk -F'load average:' '{print \$2}' | awk '{print \$1}' | sed 's/,//'")
CPU_CORES=$($SSH_CMD "nproc")
LOAD_PERCENT=$(echo "$CPU_LOAD $CPU_CORES" | awk '{printf "%.0f", ($1/$2)*100}')
echo "Load Average: $CPU_LOAD (${LOAD_PERCENT}% of ${CPU_CORES} cores)"

if [ "$LOAD_PERCENT" -gt 90 ]; then
    echo -e "${RED}❌ CRITICAL: CPU load is ${LOAD_PERCENT}% (above 90%)${NC}"
    exit 1
elif [ "$LOAD_PERCENT" -gt 75 ]; then
    echo -e "${YELLOW}⚠️  WARNING: CPU load is ${LOAD_PERCENT}% (above 75%)${NC}"
else
    echo -e "${GREEN}✅ CPU load OK (${LOAD_PERCENT}%)${NC}"
fi
echo ""

# Final summary
echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}SUMMARY${NC}"
echo -e "${BLUE}========================================${NC}"

ISSUES=0

if [ "$MEMORY_USAGE" -gt 85 ]; then
    echo -e "${RED}❌ Memory usage too high${NC}"
    ISSUES=$((ISSUES + 1))
fi

if [ "$DISK_USAGE" -gt 90 ]; then
    echo -e "${RED}❌ Disk usage too high${NC}"
    ISSUES=$((ISSUES + 1))
fi

if [ "$LOAD_PERCENT" -gt 90 ]; then
    echo -e "${RED}❌ CPU load too high${NC}"
    ISSUES=$((ISSUES + 1))
fi

if [ "$ISSUES" -eq 0 ]; then
    echo -e "${GREEN}✅ Server status OK - Safe to deploy${NC}"
    echo ""
    echo -e "${GREEN}You can proceed with: git push origin main${NC}"
    exit 0
else
    echo -e "${RED}❌ ${ISSUES} critical issue(s) found${NC}"
    echo -e "${RED}DO NOT DEPLOY until issues are resolved${NC}"
    exit 1
fi

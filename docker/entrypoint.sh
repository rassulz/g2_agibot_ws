#!/usr/bin/env bash
#
# Container entrypoint. Also sourced from ~/.bashrc with --shell-init so that
# interactive shells get the same environment as `docker compose run` commands.

set -o pipefail

WS_DIR="${WS_DIR:-/ws}"
ROS_DISTRO="${ROS_DISTRO:-kilted}"

# Overlays are kept per-distro. The repository root already carries build/,
# install/ and log/ from a host-side Humble build; writing a second distro's
# artifacts into those same directories would silently corrupt both.
export COLCON_BUILD_BASE="${WS_DIR}/build/${ROS_DISTRO}"
export COLCON_INSTALL_BASE="${WS_DIR}/install/${ROS_DISTRO}"
export COLCON_LOG_BASE="${WS_DIR}/log/${ROS_DISTRO}"

# --- ROS 2 underlay ---------------------------------------------------------
if [ -f "/opt/ros/${ROS_DISTRO}/setup.bash" ]; then
    # shellcheck disable=SC1090
    source "/opt/ros/${ROS_DISTRO}/setup.bash"
else
    echo "entrypoint: /opt/ros/${ROS_DISTRO}/setup.bash not found" >&2
fi

# --- workspace overlay ------------------------------------------------------
if [ -f "${COLCON_INSTALL_BASE}/setup.bash" ]; then
    # shellcheck disable=SC1090
    source "${COLCON_INSTALL_BASE}/setup.bash"
fi

# --- Fast DDS ---------------------------------------------------------------
# The variable was renamed in Fast DDS 3.x: Humble reads FASTRTPS_*, Kilted
# reads FASTDDS_*. Set whichever matches, and export both when a profile is
# supplied so the value survives a distro switch.
if [ -n "${DDS_PROFILE_FILE}" ] && [ -f "${DDS_PROFILE_FILE}" ]; then
    export FASTRTPS_DEFAULT_PROFILES_FILE="${DDS_PROFILE_FILE}"
    export FASTDDS_DEFAULT_PROFILES_FILE="${DDS_PROFILE_FILE}"
fi

# --- GDK (optional, mounted from the host) ----------------------------------
GDK_HOME="${GDK_HOME:-${HOME}/.cache/agibot}"
if [ -d "${GDK_HOME}/app/gdk/lib" ]; then
    export GDK_HOME
    export PYTHONPATH="${GDK_HOME}/app/gdk/lib:${PYTHONPATH}"
    export APP_CONF_PATH="${GDK_HOME}/app/gdk/config/app_conf.json"
    if [ -d "${GDK_HOME}/app/lib" ]; then
        export LD_LIBRARY_PATH="${GDK_HOME}/app/lib:${LD_LIBRARY_PATH}"
    fi
fi

# --- convenience ------------------------------------------------------------
# Build into the per-distro bases without having to repeat the flags.
cb() {
    ( cd "${WS_DIR}" && colcon build \
        --build-base "${COLCON_BUILD_BASE}" \
        --install-base "${COLCON_INSTALL_BASE}" \
        --symlink-install \
        "$@" )
}
export -f cb 2>/dev/null || true

# When sourced from .bashrc, stop here -- there is no command to exec.
if [ "${1}" = "--shell-init" ]; then
    return 0 2>/dev/null || exit 0
fi

if [ -t 1 ]; then
    echo "ROS ${ROS_DISTRO} | domain ${ROS_DOMAIN_ID:-unset} | rmw ${RMW_IMPLEMENTATION:-default}"
    echo "workspace ${WS_DIR}  ->  install/${ROS_DISTRO}"
    echo "build with:  cb            (colcon build into the per-distro base)"
fi

exec "$@"

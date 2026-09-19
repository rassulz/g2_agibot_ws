# syntax=docker/dockerfile:1
#
# Development container for the AgiBot G2 workspace.
#
#   ROS_DISTRO=kilted  -> Ubuntu 24.04 + ROS 2 Kilted + Python 3.12  (matches the robot)
#   ROS_DISTRO=humble  -> Ubuntu 22.04 + ROS 2 Humble + Python 3.10  (GDK's x86_64 target)
#
# See docker/README.md for the trade-off between the two.

ARG ROS_DISTRO=kilted
FROM ros:${ROS_DISTRO}-ros-base

# ARGs must be re-declared after FROM to be visible in the build stage.
ARG ROS_DISTRO
ARG USER_NAME=dev
ARG USER_UID=1000
ARG USER_GID=1000
ARG INSTALL_VIZ=0

ENV DEBIAN_FRONTEND=noninteractive \
    LANG=C.UTF-8 \
    LC_ALL=C.UTF-8
SHELL ["/bin/bash", "-o", "pipefail", "-c"]

# ---------------------------------------------------------------------------
# System packages
# ---------------------------------------------------------------------------
RUN apt-get update && apt-get install -y --no-install-recommends \
        bash-completion \
        build-essential \
        ca-certificates \
        cmake \
        curl \
        gdb \
        git \
        iproute2 \
        iputils-ping \
        less \
        lsof \
        nano \
        net-tools \
        openssh-client \
        pkg-config \
        python3-pip \
        rsync \
        sudo \
        tcpdump \
        unzip \
        vim \
        wget \
    && rm -rf /var/lib/apt/lists/*

# ---------------------------------------------------------------------------
# ROS 2 build tooling and the interface dependencies genie_msgs / gdk_msgs need
# ---------------------------------------------------------------------------
RUN apt-get update && apt-get install -y --no-install-recommends \
        python3-colcon-common-extensions \
        python3-colcon-mixin \
        python3-rosdep \
        python3-vcstool \
        "ros-${ROS_DISTRO}-ament-cmake" \
        "ros-${ROS_DISTRO}-ament-lint-auto" \
        "ros-${ROS_DISTRO}-ament-lint-common" \
        "ros-${ROS_DISTRO}-builtin-interfaces" \
        "ros-${ROS_DISTRO}-geometry-msgs" \
        "ros-${ROS_DISTRO}-nav-msgs" \
        "ros-${ROS_DISTRO}-rmw-fastrtps-cpp" \
        "ros-${ROS_DISTRO}-rosidl-default-generators" \
        "ros-${ROS_DISTRO}-rosidl-default-runtime" \
        "ros-${ROS_DISTRO}-sensor-msgs" \
        "ros-${ROS_DISTRO}-std-msgs" \
        "ros-${ROS_DISTRO}-std-srvs" \
        "ros-${ROS_DISTRO}-tf2-msgs" \
        "ros-${ROS_DISTRO}-visualization-msgs" \
    && rm -rf /var/lib/apt/lists/*

# Optional visualization stack (heavy) -- enable with --build-arg INSTALL_VIZ=1
RUN if [ "${INSTALL_VIZ}" = "1" ]; then \
        apt-get update && apt-get install -y --no-install-recommends \
            "ros-${ROS_DISTRO}-rviz2" \
            "ros-${ROS_DISTRO}-rqt" \
            "ros-${ROS_DISTRO}-rqt-common-plugins" \
        && rm -rf /var/lib/apt/lists/* ; \
    fi

# ---------------------------------------------------------------------------
# Python packages used by the GDK bindings and its examples.
#
# Anything Ubuntu ships is taken from apt: pip cannot uninstall dpkg-managed
# distributions (they carry no RECORD file), so letting pip resolve these
# pulls in a conflict it cannot complete.
# ---------------------------------------------------------------------------
RUN apt-get update && apt-get install -y --no-install-recommends \
        python3-numpy \
        python3-pybind11 \
        python3-setuptools \
        python3-typing-extensions \
        python3-yaml \
        pybind11-dev \
    && rm -rf /var/lib/apt/lists/*

# The remainder is not packaged by Ubuntu at a usable version.
# Ubuntu 24.04 enforces PEP 668, so --break-system-packages is required there
# but is not understood by the pip shipped with 22.04. Detect rather than assume.
# --ignore-installed keeps pip from trying to remove the apt-managed packages
# above while resolving these.
RUN PIP_FLAGS=""; \
    if python3 -m pip install --help 2>/dev/null | grep -q -- "--break-system-packages"; then \
        PIP_FLAGS="--break-system-packages"; \
    fi; \
    python3 -m pip install --no-cache-dir --ignore-installed ${PIP_FLAGS} \
        protobuf \
        grpcio \
        grpcio-tools \
        "packaging>=24.0"

# grpcio-tools drags in a modern setuptools, whose version handling calls
# packaging.utils.canonicalize_version(strip_trailing_zero=...). Ubuntu 22.04
# ships packaging 21.3, which has no such parameter, and ament_cmake_python
# then fails every interface package with:
#   TypeError: canonicalize_version() got an unexpected keyword argument
# Pinning packaging forward keeps the pair consistent on both distros.

# ---------------------------------------------------------------------------
# Non-root user matching the host UID/GID, so files written into the mounted
# workspace are owned by you and not by root.
#
# Ubuntu 24.04 base images ship a stock "ubuntu" account already occupying
# UID 1000, so reclaim the id before creating ours.
# ---------------------------------------------------------------------------
RUN set -eux; \
    if getent passwd "${USER_UID}" >/dev/null; then \
        existing_user="$(getent passwd "${USER_UID}" | cut -d: -f1)"; \
        userdel -r "${existing_user}" 2>/dev/null || userdel "${existing_user}"; \
    fi; \
    if getent group "${USER_GID}" >/dev/null; then \
        existing_group="$(getent group "${USER_GID}" | cut -d: -f1)"; \
        groupdel "${existing_group}" 2>/dev/null || true; \
    fi; \
    groupadd --gid "${USER_GID}" "${USER_NAME}"; \
    useradd --uid "${USER_UID}" --gid "${USER_GID}" --create-home --shell /bin/bash "${USER_NAME}"; \
    echo "${USER_NAME} ALL=(ALL) NOPASSWD:ALL" > "/etc/sudoers.d/${USER_NAME}"; \
    chmod 0440 "/etc/sudoers.d/${USER_NAME}"

# rosdep needs its cache initialised as root, before we drop privileges.
RUN rosdep init 2>/dev/null || true

COPY entrypoint.sh /usr/local/bin/entrypoint.sh
RUN chmod +x /usr/local/bin/entrypoint.sh

# ---------------------------------------------------------------------------
# Runtime environment -- mirrors gdk/scripts/ros_env.sh on the robot
# ---------------------------------------------------------------------------
ENV ROS_DISTRO=${ROS_DISTRO} \
    ROS_VERSION=2 \
    ROS_PYTHON_VERSION=3 \
    ROS_DOMAIN_ID=4 \
    RMW_IMPLEMENTATION=rmw_fastrtps_cpp \
    WS_DIR=/ws

USER ${USER_NAME}
WORKDIR /ws

RUN rosdep update --rosdistro "${ROS_DISTRO}" 2>/dev/null || true; \
    echo "source /usr/local/bin/entrypoint.sh --shell-init" >> "${HOME}/.bashrc"

ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]
CMD ["bash"]

from setuptools import find_packages, setup

package_name = 'motion_control'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    package_data={'': ['py.typed']},
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='rassulz',
    maintainer_email='rassul.zeinulla@nu.edu.kz',
    description='Motion control interface for the AgiBot G2',
    license='Apache-2.0',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': [
            'status_monitor = motion_control.status_monitor:main',
            'joint_position_client = motion_control.joint_position_client:main',
        ],
    },
)

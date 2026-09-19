from setuptools import find_packages, setup

package_name = 'computer_vision'

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
    description='Camera and perception nodes for the AgiBot G2',
    license='Apache-2.0',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': [
            'camera_monitor = computer_vision.camera_monitor:main',
            'stereo_viewer = computer_vision.stereo_viewer:main',
        ],
    },
)

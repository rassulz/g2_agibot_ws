from setuptools import find_packages, setup

package_name = 'omni_hand'

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
    description='Hand and manipulator control for the AgiBot G2',
    license='Apache-2.0',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': [
            'hand_state = omni_hand.hand_state:main',
            'command_scaffold = omni_hand.command_scaffold:main',
            'hand_identify = omni_hand.hand_identify:main',
            'hand_grasp = omni_hand.hand_grasp:main',
            'usb_hand = omni_hand.usb_hand:main',
        ],
    },
)
